"""Bounded file-to-palette native preview. Explicit PC Elsa profiles, no pose adjustments."""
import argparse,hashlib,json,math,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))

def profile_for(path):
    path=Path(path).resolve()
    if path.suffix.lower()!='.oct' or not path.is_file() or path.stat().st_size>32*1024*1024:raise ValueError('Choose an extracted supported native clip OCT.')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    catalog=json.loads((ROOT/'OctaneCharacterViewer/native-preview-profiles.json').read_text(encoding='utf-8'))
    for blocked in catalog.get('blocked_profiles',[]):
        if blocked['source_sha256']==digest:raise ValueError(blocked['reason'])
    matches=[p for p in catalog['profiles']if p['source_sha256']==digest]
    if len(matches)!=1:raise ValueError('No validated rig-evaluation profile for this clip. Supported: Elsa active/passive idle and class_girl forward walk/run, diagonal-right and sideways-right runs. Use native inspection for other clips.')
    profile=matches[0]
    for row in profile['companions']:
        if hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Companion source changed: '+row['name'])
    return profile

def evaluate(path,output,cycles=1,timing='fixture',idle_transition_state=None,idle_transition_dilations=False,idle_transition_transforms=False,native_facial_paths=False,native_eyelid_paths=False,native_eye_paths=False,native_forearm_paths=False):
    if not 1<=cycles<=4:raise ValueError('Cycles must be between 1 and 4.')
    if timing not in ('fixture','native-default'):raise ValueError('Unsupported timing mode')
    if timing=='native-default' and cycles!=1:raise ValueError('Native default timing supports one activation only; repeat scheduling is not reconstructed.')
    profile=profile_for(path);print('PROFILE '+profile['name'],flush=True)
    if (native_facial_paths or native_eyelid_paths or native_eye_paths or native_forearm_paths) and profile['kind'] not in ('idle','turn') and profile['name'] not in ('grl_bm_walkf','grl_bm_runf','grl_bm_runrf','grl_bm_runr','grl_bm_runb','grl_bm_runrb','grl_bm_runlb','grl_bm_walkb','grl_bm_walkrb','grl_bm_walklb'):raise ValueError('Full palette source paths are currently bounded to the supported PC Elsa profiles')
    from pc_preview_filter_configuration import configuration
    source_filter_configuration=configuration(profile['name'])
    import numpy as np
    from pc_skin_palette import PC_RIG,Clip,parents,worlds,skin,names,PROD,DN,get,reflect,affine,point,ChainStates,apply
    from evaluate_pc_braid import BraidEval
    from native_pc_skin_matrix import matrix as packed_matrix
    from pc_finger_controls import prepare_fingers
    from read_pc_idle_files import tuple_decode
    from inspect_pc_run_lean import read_static
    # Source graph implementation matches the established run/braid checkpoint.
    class Eval(BraidEval):
        def run(self,i):
            if i in (644,650)and i in self.overrides:
                if i not in self.cache:self.cache[i]=affine(self.raw.run(i))
                return self.cache[i]
            return super().run(i)
    parents=dict(parents,hair01='hairStart',hair02='hair01')
    bindlocals={n:np.linalg.inv(worlds[p])@worlds[n]if p else worlds[n]for n,p in parents.items()}
    names=list(names)+[n for n in worlds if any(s in n for s in ('Thumb','Index','Middle'))]+['hairStart','hair01','hair02']
    facial_bones=['BrowCenter','BrowLeft','BrowRight','Jaw','CornerLipLeft','CornerLipRight','LowerLip','UpperLip']
    eyelid_bones=['UpperLidLeft','UpperLidRight','LowerLidLeft','LowerLidRight']
    forearm_bones=['Forearm_OL_Left','Forearm_OL_Right']
    if native_forearm_paths:names+=forearm_bones
    eye_bones=['eyeLeft','eyeRight']
    if native_eye_paths:names+=eye_bones
    if native_eyelid_paths:names+=eyelid_bones
    if native_facial_paths:names+=facial_bones
    if len(set(names))!=len(names):raise ValueError('Duplicate evaluated palette bone')
    clip=Clip(path,PC_RIG);companions={r['name']:r for r in profile['companions']}
    upper=base=None;lean=None;composition=None;upper_weight=1.;lean_weight=1.
    if profile['kind'] in ('walk','run'):
        uppername='grl_bm_'+profile['kind']+'_upbody_add'
        upper=Clip(companions[uppername]['path'],PC_RIG);base=Clip(companions['elsa_bm_idle_passive']['path'],PC_RIG)
        if upper.duration!=clip.duration:raise ValueError('Upper/lower durations differ')
    if profile['kind']=='turn':base=Clip(companions['elsa_bm_idle_passive']['path'],PC_RIG)
    if profile['kind']=='run' or (profile['kind']=='walk' and 'group' in profile):
        from audit_pc_run_source_composition import audit
        composition=audit()
        groupname=profile.get('group','Run Forward')
        group=next(g for g in composition['groups']if g['name']==groupname)
        leanname=profile.get('lean_companion','human_bm_runf_lean_add')
        expected=[profile['name']+'.oct',uppername+'.oct',leanname+'.oct']
        if [Path(t['filename']).name for t in group['tracks']]!=expected:raise ValueError('Run group source order changed')
        if group['tracks'][2]['explicit_blend_method']!=1:raise ValueError('Unsupported lean mode')
        upper_weight=float(group['tracks'][1]['explicit_weight'] if group['tracks'][1]['explicit_weight'] is not None else 1.)
        lean_weight=float(group['tracks'][2]['explicit_weight'] if group['tracks'][2]['explicit_weight'] is not None else 1.)
        if not 0<=lean_weight<=1:raise ValueError('Unsupported lean weight')
        composition['selected_group']=group
        source=Path(companions[leanname]['path']).read_bytes()
        vv=next(r['value']for r in tuple_decode(source)['records']if r['name']=='ClipDataBlock')
        lean=read_static(bytes(vv)if isinstance(vv,list)else bytes.fromhex(vv['hex']))
    skipped={'unmapped_ports':set(),'computed_output_nodes':set(),'unhandled_opcodes':set()}
    finger_input_nodes={i['node'] for p in json.loads((ROOT/'ElsaSceneResearch/pc-finger-native-probe.json').read_text(encoding='utf-8'))['relationships'] for i in p['inputs']}
    # The verified Float operation is integrated only for idle index/middle
    # controls. Locomotion's multi-layer controller remains a separate boundary.
    from native_scalar_state import ScalarStates
    scalar_states=ScalarStates()
    scalar_ports=(483,485,486,487,488,489,510,512,513,514,515,516)
    scalar_nodes={PC_RIG.lookup[p] for p in scalar_ports}
    transition=None;transition_state=None;transition_trace=[];transition_factor=1.
    dilation_states=None;dilation_nodes=[];dilation_excluded=[]
    transform_states=None;transform_nodes=[];transform_excluded=[]
    if (idle_transition_dilations or idle_transition_transforms) and not idle_transition_state:raise ValueError('Typed transition requires an explicit idle transition state')
    def transform_payload(fields):
        scale=fields.get('Scale',[1.]*4);unscale=fields.get('Unscale',[1.]*4)
        return fields['Orientation']+fields['Translation']+[scale[3]]+scale+unscale[:3]+[1.]
    if idle_transition_state:
        if profile['kind']!='idle' or cycles!=1 or timing!='fixture':raise ValueError('Explicit finger transition requires one idle cycle with fixture timing')
        from read_idle_state_parameters import read as read_states
        from native_explicit_state_transition import ExplicitStateTransition
        manifest=json.loads((ROOT/'ElsaSceneResearch/ControllerState/shared-idle-state-parameters.json').read_text())
        state_data=read_states(manifest['xml'],ROOT/'ElsaSceneResearch/installed-elsa-bent-decoded.json')
        if state_data['xml_sha256']!=manifest['xml_sha256']:raise ValueError('Shared state XML changed; revalidate its parameters')
        matches=[s for s in state_data['states']if s['state_path']==idle_transition_state]
        if len(matches)!=1 or Path(matches[0]['motion']or'').stem!=profile['name']:raise ValueError('Choose a unique full state path matching this idle motion')
        transition_state=matches[0]
        transition=ExplicitStateTransition(transition_state['ease_duration_units'])
    def audit_records(records):
        for port,row in records.items():
            node=row['source_node']
            if node is None:skipped['unmapped_ports'].add(port)
            elif node in PROD:skipped['computed_output_nodes'].add(node)
            for op in row['channels']:
                if int(op)not in range(11):skipped['unhandled_opcodes'].add(int(op))
    def controls(e,phase,finger_trace=None):
        stages={}
        def trace_stage(label,records):
            if finger_trace is None:return
            for port,record in records.items():
                node=record['source_node']
                if node in finger_input_nodes and node not in PROD:
                    stages.setdefault(node,[]).append(dict(source=label,port=port,
                        scalar_channel=record['channels'].get('10'),applied_value=e.overrides[node].get('Value'),
                        note='Each applied record starts from serialized rig fields; later source application replaces this override.'))
        if base:
            records=base.sample(0);audit_records(records);apply(e,records)
            trace_stage('passive_idle_base_at_zero',records)
        records=clip.sample(phase);audit_records(records);apply(e,records,allow_transform_scale=profile['kind'] in ('run','turn'))
        main_records=records
        trace_stage(profile['name'],records)
        if upper:
            records=upper.sample(phase);audit_records(records);apply(e,records)
            trace_stage(uppername,records)
        if lean:
            from compose_native_clip_layers import compose as compose_layers
            lean_records={}
            for row in lean['tracks']:
                node=PC_RIG.lookup[row['port']]
                allowed_lean=(240,267,352,370,252,256)if profile['name'] in ('grl_bm_runb','grl_bm_walkb')else(240,267,352,370)
                if node not in allowed_lean or node in PROD:raise ValueError('Unexpected lean target')
                lean_records[row['port']]=dict(source_node=node,path=PC_RIG.paths.get(node),
                    channels={str(d['opcode']):d['values']for d in row['descriptors']})
            # Compose entire typed channel rows before applying leaf overrides.
            # Selected source-group weights use the verified native null-filter blend.
            composed=compose_layers([(main_records,1.,1),(records,upper_weight,1),(lean_records,lean_weight,0)])
            apply(e,composed,allow_transform_scale=True)
            trace_stage('native_forward_group_composed',composed)
        if profile['kind']=='idle':
            for node in sorted(scalar_nodes):
                target=e.overrides.get(node,{}).get('Value',get(DN[node],'Data'))
                if isinstance(target,list):target=target[0]
                value=scalar_states.update(node,float(target),factor=transition_factor)
                e.overrides.setdefault(node,{})['Value']=value
        if dilation_states is not None:
            for node in dilation_nodes:
                fields=e.overrides[node]
                value=dilation_states.update(node,fields['Orientation']+fields['Translation']+[1.],transition_factor)
                if abs(value[7]-1)>1e-5:raise ValueError('Nonunit Dilation scale is not applied by this preview')
                fields['Orientation']=value[:4];fields['Translation']=value[4:7]
        if transform_states is not None:
            for node in transform_nodes:
                fields=e.overrides[node];value=transform_states.update(node,transform_payload(fields),transition_factor)
                if abs(value[7]-value[11])>1e-5:raise ValueError('Transform uniform/Scale.w disagreement')
                fields.update(Orientation=value[:4],Translation=value[4:7],Scale=value[8:12],Unscale=value[12:15]+[1.])
        prepare_fingers(e,diagnostics=finger_trace)
        if finger_trace is not None:
            for processor in finger_trace:
                for item in processor['inputs']:item['source_stages']=stages.get(item['node'],[])
    force=[0.,-9.8100004196167,0.];warmup=120
    states=ChainStates(force=force,strict_types=True)
    for tick in range(warmup):
        e=Eval(states,tick,1/60);controls(e,0)
        e.raw.run(skin['dressLeftStart']);e.raw.run(skin['dressRightStart']);e.raw.run(skin['hair01']);e.run(skin['hair02'])
    print('WARMUP complete',flush=True)
    if transition:
        # Explicit outgoing pose fixture: passive idle at phase zero, twelve controls only.
        catalog=json.loads((ROOT/'OctaneCharacterViewer/native-preview-profiles.json').read_text())
        outgoing_profile=next(p for p in catalog['profiles']if p['name']=='elsa_bm_idle_passive')
        profile_for(outgoing_profile['source'])
        outgoing=Clip(outgoing_profile['source'],PC_RIG);old=Eval(states,warmup,1/60)
        apply(old,outgoing.sample(0))
        for node in sorted(scalar_nodes):
            value=old.overrides.get(node,{}).get('Value',get(DN[node],'Data'))
            if isinstance(value,list):value=value[0]
            scalar_states.seed(node,float(value),0.,False)
        if idle_transition_dilations:
            from native_dilation_state import DilationStates
            incoming=Eval(states,warmup,1/60);apply(incoming,clip.sample(0))
            dilation_states=DilationStates()
            for node,fields in incoming.overrides.items():
                if node in PROD or get(DN[node],'Type')!='Dilation':continue
                prior=old.overrides.get(node,{})
                if not all({'Orientation','Translation'}<=v.keys()for v in (fields,prior)):
                    dilation_excluded.append(node);continue
                dilation_states.seed(node,prior['Orientation']+prior['Translation']+[1.],False);dilation_nodes.append(node)
        if idle_transition_transforms:
            from native_transform_state import TransformStates
            incoming=Eval(states,warmup,1/60);apply(incoming,clip.sample(0))
            transform_states=TransformStates();outgoing_records=outgoing.sample(0)
            def complete_transform(record):
                channels=record.get('channels',{})
                return '4'in channels and ('0'in channels or {'1','2','3'}<=channels.keys()) and '5'in channels
            for port,record in clip.sample(0).items():
                node=record['source_node']
                if node is None or node in PROD or get(DN[node],'Type')!='Transform':continue
                if not complete_transform(record)or not complete_transform(outgoing_records.get(port,{})):
                    transform_excluded.append(node);continue
                # Unit Scale/Unscale remain the existing explicit idle evaluator fixture.
                transform_states.seed(node,transform_payload(old.overrides[node]),0.,False);transform_nodes.append(node)
    frames_per_cycle=max(1,round(clip.duration*60));frames=frames_per_cycle*cycles;duration=clip.duration*cycles
    native_clock=native_curve=None;timing_trace=[];last_tick_ms=0
    if timing=='native-default':
        from native_default_clock import DefaultEngineClock
        from native_default_curve_time import DefaultCurveTime
        native_clock=DefaultEngineClock();native_curve=DefaultCurveTime(0.,clip.duration)
        native_curve.activate(native_clock.publish())
        duration=math.ceil(clip.duration*1000)/1000
    if duration>30:raise ValueError('Preview duration exceeds 30 seconds')
    samples=[];finger_diagnostics=[];max_endpoint=max_matrix=max_shear=max_root=max_length=0.;endpoint_checks=[];max_witness=0.
    for frame in range(frames+1):
        # Match the established run regression's seam semantics; a single cycle includes its authored final pose.
        phase=clip.duration*frame/frames_per_cycle if cycles==1 else clip.duration*(frame%frames_per_cycle)/frames_per_cycle
        t=duration*frame/frames;step=duration/frames
        if native_clock:
            tick_ms=round(duration*1000*frame/frames)
            if frame:
                native_clock.advance(tick_ms-last_tick_ms);native_clock.publish()
                step=native_clock.delta_seconds
            t=tick_ms/1000;phase=native_curve.request(native_clock.published);last_tick_ms=tick_ms
            timing_trace.append(dict(frame=frame,time=t,phase=phase,token=native_clock.token,state_byte63=native_curve.state_byte63))
        if transition:
            transition_factor=transition.update(t)
            if frame<12:transition_trace.append(dict(frame=frame,time=t,factor=transition_factor))
        finger_trace=[] if frame in (0,frames//2,frames) else None
        e=Eval(states,warmup+frame,step);controls(e,phase,finger_trace=finger_trace);out={}
        if finger_trace is not None:finger_diagnostics.append(dict(frame=frame,time=t,phase=phase,processors=finger_trace))
        for bone in names:
            if get(DN[skin[bone]],'Type')=='Transform':
                raw=e.raw.run(skin[bone]);packed=packed_matrix(raw);m=np.eye(4);m[:3,:3]=np.array(packed[:9]).reshape(3,3).T;m[:3,3]=packed[9:]
                err=float(np.max(abs(m-affine(raw))));max_matrix=max(max_matrix,err)
                if err>2e-6:raise ValueError('Native matrix/point mismatch')
                out[bone]=m
            else:out[bone]=e.run(skin[bone])
        for ankle,target in [(422,488),(450,479)]:
            actual=point(e.raw.run(ankle),[0,0,0]);wanted=(e.run(400)@np.r_[e.run(target),1])[:3]
            err=float(np.linalg.norm(actual-wanted));max_endpoint=max(max_endpoint,err)
            solver=e.solvers[{422:405,450:411}[ankle]]
            if solver['outputs'][2]==[1.0]:
                from native_pc_ik_endpoint import witness
                w=witness(solver,e.run(400))
                target_error=float(np.linalg.norm(w['target']-wanted))
                native_error=float(np.linalg.norm(actual-w['world']));max_witness=max(max_witness,native_error)
                if not np.isfinite(native_error) or native_error>1e-5 or target_error>1e-5:
                    raise ValueError(f'Native ankle witness mismatch: frame={frame}, ankle={ankle}, error={native_error}, target_error={target_error}')
                endpoint_checks.append(dict(frame=frame,ankle=ankle,target_residual=err,native_target_residual=w['native_target_residual'],native_output_error=native_error))
            elif err>1e-5:raise ValueError(f'Ankle endpoint invariant failed: frame={frame}, ankle={ankle}, error={err:.12g}')
        active=set()
        def world(bone):
            if bone in out:return out[bone]
            if bone in active:raise ValueError('Palette hierarchy cycle')
            active.add(bone);p=parents[bone];out[bone]=(world(p)if p else np.eye(4))@bindlocals[bone];active.remove(bone);return out[bone]
        poses=[]
        for bone in worlds:
            m=world(bone);scale=np.linalg.norm(m[:3,:3],axis=0);rot=m[:3,:3]/scale;shear=float(np.max(abs(rot.T@rot-np.eye(3))));max_shear=max(max_shear,shear)
            if not np.isfinite(m).all()or min(scale)<=0 or shear>2e-5 or np.linalg.det(rot)<0:raise ValueError('Invalid skin matrix for '+bone)
            poses.append(dict(bone=bone,matrix=(reflect@m@reflect).flatten().tolist()))
        for check in e.dress_checks:
            if check['native_last_frame']!=warmup+frame:raise ValueError('Dynamics frame did not advance')
            max_root=max(max_root,check['root_error']);max_length=max(max_length,check['segment_length_error'])
        if finger_trace is not None:
            from pc_finger_transform_audit import audit as audit_finger_transforms
            finger_diagnostics[-1]['hierarchy_audit']=audit_finger_transforms(e)
        if frame%2==0 or frame==frames:samples.append(dict(time=t,transforms=poses))
        if frame%30==0 or frame==frames:print('PROGRESS '+json.dumps(dict(frame=frame,total=frames,time=t)),flush=True)
    assumptions=['Partial PC Elsa graph; fallback bones inherit bind offsets','Original measured gravity fixture; no capsule collision scene','120 reset-pose warmup ticks; no live actor scheduler or root translation','Unmapped ports and computed-output clip channels are not applied','Hair/finger routines reused from run checkpoint; idle/walk parity not established','Not a full engine, universal clip loader, or native game parity']
    if profile['kind']=='turn':assumptions.append('Source turn skeletal motion with passive phase-zero initializer. No guessed actor yaw, world displacement or turn-state/controller reconstruction.')
    if base:assumptions+=['Passive idle phase zero initializes absent locomotion controls','Upper/lower controls combined on source nodes; dynamic filter/weight scheduling incomplete']
    report=dict(model_sha256=PC_RIG.sha,source=str(Path(path).resolve()),source_sha256=profile['source_sha256'],profile=profile,scope='Bounded native clip-to-rig evaluation; explicit fixture state, not full game runtime',fixture_assumptions=assumptions,simulation_hz=60,warmup_ticks=warmup,force=force,source_skin_nodes={n:skin[n]for n in names},fallback_parents={n:parents[n]for n in worlds if n not in names},unmapped_ports=clip.unmapped,upper_unmapped_ports=upper.unmapped if upper else [],clips=[dict(name=profile['name']+'_NativePreview',duration=duration,source_cycle_duration=clip.duration,cycles=cycles,clipdata_sha256=clip.sha,samples=samples)])
    report['skipped_channels']={key:sorted(values)for key,values in skipped.items()}
    report['forearm_source_paths']=dict(enabled=native_forearm_paths,bones=forearm_bones if native_forearm_paths else [],scope='Two PC forearm overlay paths through native rotor-to-Euler conversion and scalar product. No live parity claim.')
    report['eye_source_paths']=dict(enabled=native_eye_paths,bones=eye_bones if native_eye_paths else [],scope='Two PC Elsa eye paths through native TransformVectorWithDilation and existing graph operations; explicit preview fixtures, not live eye parity.')
    report['eyelid_source_paths']=dict(enabled=native_eyelid_paths,bones=eyelid_bones if native_eyelid_paths else [],scope='Four PC Elsa eyelid outputs through source relationship177 and native orientation connections. Explicit relationship cache initialization; no live eyelid parity or eye-direction support claim.')
    report['facial_source_paths']=dict(enabled=native_facial_paths,bones=facial_bones if native_facial_paths else [],scope='Eight PC brow/jaw/lip skin outputs through native scaled connections and existing native Transform paths. Eyelids and eye-direction graph remain excluded; no empirical pose correction or full facial/game parity claim.')
    report['source_filter_configuration']=source_filter_configuration
    report['finger_diagnostics']=dict(samples=finger_diagnostics,scope='Start/middle/end composed scalar inputs and native relationship outputs. Diagnostic only; no manual corrections.')
    report['scalar_controller']=dict(enabled=profile['kind']=='idle',evaluations=scalar_states.evaluations,ports=list(scalar_ports)if profile['kind']=='idle'else [],routine='0x4E3050',factor=1.,scope='Native stateful single unflagged source operation for idle index/middle controls. Full-weight single-clip preview; no transition scheduling or fade producer reconstructed. State persists through warmup/playback, resets for each new preview evaluation. Locomotion unchanged.')
    if transition:
        report['scalar_controller'].update(factor=None,scope='Explicit native producer fade on twelve idle index/middle scalar controls only. Outgoing scalar pose is passive idle phase zero; other channel behavior is reported separately. No automatic state scheduler or full-body crossfade.')
        report['explicit_finger_transition']=dict(state=transition_state,duration_seconds=transition.stored_duration,trace=transition_trace,outgoing='elsa_bm_idle_passive at phase zero',clock='explicit zero-origin 60Hz preview clock',scope=report['scalar_controller']['scope'])
        report['fixture_assumptions'].append(report['scalar_controller']['scope'])
        if dilation_states is not None:
            report['explicit_dilation_transition']=dict(nodes=dilation_nodes,excluded_incomplete_nodes=dilation_excluded,evaluations=dilation_states.evaluations,routine='0x4E35D0',scope='Explicit native retained-output blend on complete common Dilation leaf controls with unit uniform scale. Outgoing seed is passive phase zero. Float retains its different native incremental-fade path; Transform controls and incomplete Dilation fields switch directly. No automatic runtime binding or full-body parity claim.')
            report['fixture_assumptions'].append(report['explicit_dilation_transition']['scope'])
        if transform_states is not None:
            report['explicit_transform_transition']=dict(nodes=transform_nodes,excluded_incomplete_nodes=transform_excluded,evaluations=transform_states.evaluations,routine='0x4E3FC0',scope='Explicit native retained Transform output/fade on complete common translation, quaternion and scale channels. Existing idle evaluator unit Scale/Unscale fixture preserved; absent channels are excluded, not filled from an inferred runtime default policy. No live Transform binding or full-state scheduler claim.')
            report['fixture_assumptions'].append(report['explicit_transform_transition']['scope'])
    report['timing_configuration']=dict(mode=timing,boundary_byte=0xf8 if native_clock else None,
        scope='Explicit one-activation fixture; integer-ms schedule supplied by preview, not reconstructed game scheduler' if native_clock else 'Established fixed-step preview fixture',trace=timing_trace)
    if composition:
        report['source_composition']=composition
        report['native_group_composition']=dict(routine='0x5A14D0',row_bytes=52,
            layers=['main: weight 1 mode 1',f'upper: weight {upper_weight:g} mode 1',f'lean: weight {lean_weight:g} mode 0'],
            scope='Selected serialized run group; initializer and profile phase remain preview fixtures. No runtime speed/direction selection.')
    validation=dict(pass_=True,source_bones=len(names),palette_bones=len(worlds),frames=frames+1,samples=len(samples),max_endpoint_error=max_endpoint,max_native_matrix_error=max_matrix,max_TRS_shear=max_shear,max_dress_root_error=max_root,max_dress_segment_length_error=max_length)
    validation['ankle_validation']=dict(mode='Independent original-native FK endpoint for unit solver stretch and rigid root; otherwise original target check',tolerance=1e-5,max_native_output_error=max_witness,checks=endpoint_checks,target_residual_is_not_decoder_error=True)
    validation['pass']=validation.pop('pass_')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    def atomic(p,value):
        tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(value,separators=(',',':'),allow_nan=False),encoding='utf-8');tmp.replace(p)
    atomic(output.with_suffix('.validation.json'),validation);atomic(output,report)
    print('COMPLETE '+json.dumps({k:v for k,v in validation.items() if k!='ankle_validation'}|{'max_native_ankle_output_error':max_witness}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('clip');p.add_argument('--output',required=True);p.add_argument('--cycles',type=int,default=1);p.add_argument('--timing',choices=['fixture','native-default'],default='fixture');p.add_argument('--idle-transition-state',help='Opt-in full XML state path; fades twelve verified idle finger controls');p.add_argument('--idle-transition-dilations',action='store_true',help='Also test complete common Dilation controls through native4E35D0');p.add_argument('--idle-transition-transforms',action='store_true',help='Also test complete common Transform controls through native4E3FC0');p.add_argument('--native-facial-paths',action='store_true',help='Evaluate eight tested PC Elsa facial skin paths');p.add_argument('--native-eyelid-paths',action='store_true',help='Evaluate four tested PC Elsa eyelid source paths');p.add_argument('--native-eye-paths',action='store_true',help='Evaluate two PC Elsa eye-direction source paths');p.add_argument('--native-forearm-paths',action='store_true',help='Evaluate two PC Elsa forearm overlay paths');a=p.parse_args();evaluate(a.clip,a.output,a.cycles,a.timing,a.idle_transition_state,a.idle_transition_dilations,a.idle_transition_transforms,a.native_facial_paths,a.native_eyelid_paths,a.native_eye_paths,a.native_forearm_paths)
if __name__=='__main__':main()
