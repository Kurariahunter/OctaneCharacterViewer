"""Corrected output-space mapping and clip-local constant/timed channels; not full idle."""
import ast,json,struct,math,copy
from pathlib import Path
import numpy as np
from evaluate_elsa_head import DN,stored,allnodes,T,get
from evaluate_elsa_feet import FootEval as Eval
from decode_elsa_static_channels import decode as constants_decode
ROOT=Path(__file__).parent
# Reuse tested isolated native routines without the old sampler's file-writing main.
tree=ast.parse((ROOT/'sample_named_controls.py').read_text());setup=[]
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='mapping' for t in n.targets):break
 setup.append(n)
env={'__file__':str(ROOT/'sample_named_controls.py')};exec(compile(ast.Module(body=setup,type_ignores=[]),'native-math-setup','exec'),env)
native_curve=env['env']['native_curve'];native_rotation=env['native_rotation']
mapping=json.loads((ROOT/'elsa-control-mapping.json').read_text());lookup={r['port']:r for r in mapping['rows']}
selected={37,64,47,74,687,703,499,207,212,336,341,368,373,219,226,232,240,246};outputs={}
model=json.loads((ROOT/'elsa-preview-model.json').read_text());bones={b['name']:b for b in model['bones']};reflect=np.diag([-1,1,1,1]);skin_world={name:reflect@np.array(b['world']).reshape(4,4)@reflect for name,b in bones.items()};binds={}
for name in outputs:
 parent_index=bones[name]['parent'];binds[name]=np.linalg.inv(skin_world[model['bones'][parent_index]['name']])@skin_world[name] if parent_index>=0 else skin_world[name]
neutral=Eval();defaults={name:neutral.run(node) for name,node in outputs.items()};checks=[]
for name,node in outputs.items():
 m=defaults[name];saved=stored(DN[node]);rerr=float(np.max(np.abs(m[:3,:3]-binds[name][:3,:3])));terr=float(np.max(np.abs(m[:3,3]-binds[name][:3,3])))
 if rerr>2e-6 or terr>.001:raise ValueError('skin local does not corroborate output mapping '+name)
 checks.append({'bone':name,'output_node':node,'rotation_bind_error':rerr,'pivot_translation_difference':terr,'evaluated_vs_stored_error':float(np.max(np.abs(m-saved)))})
def fields(node):
 data=next((c for c in DN[node]['children'] if c['name']=='Data'),None)
 return {c['name']:copy.deepcopy(c['value']) for c in data['children']} if data else {}
def apply_constant(f,op,values):
 if op==0:f['Translation']=values
 elif op in (1,2,3):f.setdefault('Translation',[0,0,0])[op-1]=values[0]
 elif op==4:f['Orientation']=values
 elif op==5:
  if max(abs(v-1) for v in values)>1e-6:raise ValueError('nonunit control scale')
 elif op in (6,7,8,9):
  if abs(values[0]-1)>1e-6:raise ValueError('nonunit scalar scale')
 else:raise ValueError('unsupported selected constant '+str(op))
clips=[];summaries=[]
for clipname in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
 clip=next(c for c in mapping['idle_clips'] if Path(c['file']).stem==clipname);b=(ROOT/(clipname+'.clipdata.bin')).read_bytes();d=json.loads((ROOT/(clipname+'-decoded-curves.json')).read_text());const=constants_decode(b,d);baseline={i:fields(i) for i in selected};applied=[]
 for track in const['tracks']:
  binding=lookup.get(track['port'])
  if binding is None or binding['data_node'] not in selected:continue
  i=binding['data_node']
  for desc in track['descriptors']:apply_constant(baseline[i],desc['opcode'],desc['values'])
  applied.append({'port':track['port'],'data_node':i,'descriptors':track['descriptors']})
 count=struct.unpack_from('<H',b,10)[0];offsets=struct.unpack_from('<'+'I'*(count+2),b,12);pool=offsets[0];floats=struct.unpack_from('<'+'f'*((len(b)-pool)//4),b,pool);duration=struct.unpack_from('<f',b,4)[0];frames=round(duration*30);samples=[]
 for frame in range(frames+1):
  time=duration*frame/frames;cache={};current=copy.deepcopy(baseline)
  def value(ref,dynamic):
   if not dynamic:
    if not 0<=ref<len(floats):raise ValueError('static operand bounds')
    return floats[ref]
   if not 0<=ref<len(d['registers']):raise ValueError('register bounds')
   r=d['registers'][ref];ci=r['curve']
   if ci not in cache:
    start=offsets[ci+2];end=offsets[ci+3] if ci+3<len(offsets) else pool;cache[ci]=native_curve(b[start:end],time,len(d['curves'][ci]['metadata']))
   return cache[ci][r['component']]
  for command in clip['commands']:
   node=command['model_control']['data_node']
   if node not in selected:continue
   for desc in command['descriptors']:
    op=desc[0]
    if op&0xf000==0x1000:
     if ((op>>6)&7)!=2:raise ValueError('unsupported Euler convention')
     flags=[(op>>shift)&3 for shift in (4,2,0)]
     if any(x not in (0,1) for x in flags):raise ValueError('unknown operand source')
     angles=[value(ref,flag==1) for ref,flag in zip(desc[1:],flags)];current[node]['Orientation']=list(native_rotation(angles))
    elif op in (0x11,0x12,0x13):current[node].setdefault('Translation',[0,0,0])[op-0x11]=value(desc[1],True)
    else:raise ValueError('unsupported selected timed command '+hex(op))
  e=Eval();e.overrides=current;transforms=[];legs=[]
  for side,target,upper,knee,midinit,endinit in [('Left',450,424,430,699,698),('Right',479,453,459,683,682)]:
   A=e.run(upper);B=e.run(knee);length=np.linalg.norm(e.run(endinit)-e.run(midinit));end=(A@B@np.array([0,0,length,1]))[:3];wanted=e.run(target);err=float(np.linalg.norm(end-wanted));scales=[np.linalg.norm(A[:3,:3],axis=0).tolist(),np.linalg.norm(B[:3,:3],axis=0).tolist()]
   if not np.isfinite(err):raise ValueError(('original foot-target endpoint mismatch',side,time,err))
   legs.append({'side':side,'target_hip_space':wanted.tolist(),'solved_ankle_hip_space':end.tolist(),'error':err,'scales':scales,'native_scale_payloads':[e.cache[423 if side=='Left' else 452].tolist(),e.cache[429 if side=='Left' else 458].tolist()],'upper_matrix':A.flatten().tolist(),'knee_matrix':B.flatten().tolist()})
  for name,node in outputs.items():
   m=e.run(node).copy()
   # Keep original skin pivots; only <=0.001 source/model offset is reconciled.
   # No bind-relative orientation retargeting is applied.
   m[:3,3]+=binds[name][:3,3]-defaults[name][:3,3]
   if np.max(np.abs(m[:3,:3].T@m[:3,:3]-np.eye(3)))>1e-5:raise ValueError('nonrigid output')
   transforms.append({'bone':name,'matrix':(reflect@m@reflect).flatten().tolist()})
  samples.append({'time':time,'transforms':transforms,'legs':legs,'body_matrix':e.run(102).flatten().tolist(),'hips_matrix':e.run(410).flatten().tolist()})
 clips.append({'name':clipname+'_HipsBodyShoulders','duration':duration,'samples':samples})
 summary={'clip':clipname,'samples':len(samples),'constant_control_records':applied,'held_controls':'Legs, upper-arm local rotations, elbows, hands, face and unselected controls remain at defaults. Body motion is included; foot planting is not solved.','bone_matrix_spans':{name:float(max(np.max(np.abs(np.array(s['transforms'][j]['matrix'])-samples[0]['transforms'][j]['matrix'])) for s in samples)) for j,name in enumerate(outputs)}};summaries.append(summary)
report={'scope':'Corrected local skin output mapping, source rotation matrices and native offset order. Clip-local constant channels combined with timed channels for selected controls only. No broad bind-relative orientation correction. Small skin pivot offsets retained explicitly. Not complete BENT/base-layer blending or full-body animation.','animated_bones':list(outputs),'clips':clips}
(ROOT/'elsa-foot-target-samples.json').write_text(json.dumps(report,separators=(',',':')));(ROOT/'foot-target-mapping-validation.json').write_text(json.dumps({'mapping_checks':checks,'clip_summaries':summaries},indent=2));print('CHECKS',checks)
for c in clips:print(c['name'],'original-clip targets',len(c['samples']),'max endpoint error',max(l['error'] for f in c['samples'] for l in f['legs']))
for row in summaries:print(row['clip'],row['samples'],row['bone_matrix_spans'])

# Persist explicit per-clip qualification: nonuniform passive matrices are diagnostics only.
qualification=[]
for c in clips:
 errors=[l['error'] for f in c['samples'] for l in f['legs']]
 departure=max(abs(x-1) for f in c['samples'] for l in f['legs'] for a in l['scales'] for x in a)
 qualification.append({'clip':c['name'],'samples':len(c['samples']),'ankle_tests':len(errors),'max_ordinary_matrix_chain_error':max(errors),'max_nonuniform_scale_departure':departure,'status':'unit-scale target/IK/FK consistency passed' if departure<1e-5 and max(errors)<5e-5 else 'diagnostic only: nonuniform scale composition unresolved; not validated original ankle motion'})
report['scope']='Original clip-local controls through Elsa-only native foot relationship and IK. Active unit-scale targets consistent; passive nonuniform Scale/Unscale composition unresolved. No final skin export.'
(ROOT/'elsa-foot-target-samples.json').write_text(json.dumps(report,separators=(',',':')))
(ROOT/'original-foot-target-validation.json').write_text(json.dumps({'scope':report['scope'],'clips':qualification,'limitations':['Idle scalar foot channels are explicitly constant zero.','Scale applied after Orientation in diagnostic compose; complete native Scale/Unscale semantics unresolved.','Port mapping remains structural; complete loader not executed.','No production importer or Unity preview changes.']},indent=2))
