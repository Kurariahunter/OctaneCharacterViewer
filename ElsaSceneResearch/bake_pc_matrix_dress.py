"""File-driven PC idles with verified native packed skin matrices and gravity dress."""
from pc_skin_palette import *
from native_pc_skin_matrix import matrix as packed_matrix
matrix_checks=[]
def matrix_world(raw,bone,clip,frame):
 packed=packed_matrix(raw);m=np.eye(4);m[:3,:3]=np.array(packed[:9]).reshape(3,3).T;m[:3,3]=packed[9:]
 reference=affine(raw);error=float(np.max(abs(m-reference)))
 if error>2e-6:raise ValueError(("native packed matrix versus native point",bone,clip,frame,error))
 matrix_checks.append(dict(clip=clip,frame=frame,bone=bone,error=error));return m
FORCE=[0.,-9.8100004196167,0.]
WARMUP=120
clips=[];checks=[];dresschecks=[];maxshear=0;scale_ranges=[]
for name in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
 clip=Clip(next((R/'InstalledGameAssetCheck/IdleMotions').rglob(name+'.oct')),PC_RIG);frames=round(clip.duration*60);samples=[];worst=0;states=ChainStates(force=FORCE,strict_types=True)
 for pre in range(WARMUP):
  e=TemporalDressEval(states,pre,1/60);apply(e,clip.sample(0));e.raw.run(skin["dressLeftStart"]);e.raw.run(skin["dressRightStart"])
 for frame in range(frames+1):
  time=clip.duration*frame/frames;e=TemporalDressEval(states,WARMUP+frame,clip.duration/frames);apply(e,clip.sample(time));out={bone:matrix_world(e.raw.run(skin[bone]),bone,name,frame) if get(DN[skin[bone]],'Type')=='Transform' else e.run(skin[bone])for bone in names}
  # Compare source ankle in AnchorScale coordinates against its IK target in Hips.
  for side,ankle,target,solver in [('Right',422,488,405),('Left',450,479,411)]:
   actual=point(e.raw.run(ankle),[0,0,0]);wanted=(e.run(400)@np.r_[e.run(target),1])[:3];error=float(np.linalg.norm(actual-wanted));worst=max(worst,error)
   if error>1e-5:raise ValueError(('PC ankle skin path',name,frame,side,error))
   checks.append({'clip':name,'frame':frame,'side':side,'endpoint_error':error,'reach_scale':e.solvers[solver]['outputs'][2][0]})
  active=set()
  def world(bone):
   if bone in out:return out[bone]
   if bone in active:raise ValueError('palette hierarchy cycle')
   active.add(bone);parent=parents[bone];out[bone]=(world(parent)if parent else np.eye(4))@bindlocals[bone];active.remove(bone);return out[bone]
  poses=[]
  if any(row['native_last_frame']!=WARMUP+frame for row in e.dress_checks):raise ValueError('native frame stamp did not advance')
  dresschecks.extend(dict(clip=name,frame=frame,**row)for row in e.dress_checks)
  for bone in worlds:
   m=world(bone);sc=np.linalg.norm(m[:3,:3],axis=0);rot=m[:3,:3]/sc;shear=float(np.max(abs(rot.T@rot-np.eye(3))));maxshear=max(maxshear,shear)
   if shear>2e-5 or min(sc)<=0 or np.linalg.det(rot)<0:raise ValueError(('non-TRS palette',bone,shear))
   scale_ranges.extend(sc.tolist());poses.append({'bone':bone,'matrix':(reflect@m@reflect).flatten().tolist()})
  if frame%2==0 or frame==frames:samples.append({'time':time,'transforms':poses})
 clips.append({'name':name+'_PC_MatrixDress','duration':clip.duration,'samples':samples,'clipdata_sha256':clip.sha});print(name,len(samples),'endpoint',worst,flush=True)
data={'scope':'PC file-only controls through source skin world output paths; Transform skin matrices use original native55da50 packed12 converter, verified against live outputs; Dilation paths retain existing evaluator; native 8/3 IK and scale compensation. 31 source-driven bones; remaining palette bones inherit bind offsets. Lower dress uses persistent original native DynamicChain updates, authored PC particle scalars, measured external force [0,-9.8100004196167,0], strict native Transform/Dilation type fixtures and no capsule scene. Previous local Aim orientation feeds the next frame; each clip starts reset. Exact game scene forces, collisions, update order and seamless looping are not established. Independent palette export avoids Unity parent-scale multiplication. Facial/finger motion and game layer blending incomplete.','model_sha256':PC_RIG.sha,'force':FORCE,'simulation_hz':60,'warmup_ticks':WARMUP,'source_skin_nodes':{n:skin[n]for n in names},'fallback_parents':{n:parents[n]for n in worlds if n not in names},'clips':clips}
(R/'pc-matrix-dress-animation.json').write_text(json.dumps(data,separators=(',',':')))
(R/'pc-matrix-dress-validation.json').write_text(json.dumps({'model_sha256':PC_RIG.sha,'force':FORCE,'simulation_hz':60,'warmup_ticks':WARMUP,'source_bones':len(names),'palette_bones':len(worlds),'max_TRS_shear':maxshear,'min_scale':min(scale_ranges),'max_scale':max(scale_ranges),'max_endpoint_error':max(c['endpoint_error']for c in checks),'checks':checks,'max_dress_root_error':max(c['root_error']for c in dresschecks),'max_dress_segment_length_error':max(c['segment_length_error']for c in dresschecks),'dress_checks':dresschecks,'native_matrix_checks':matrix_checks,'native_matrix_comparisons':len(matrix_checks),'max_native_matrix_error':max(c['error']for c in matrix_checks),'source_skin_nodes':data['source_skin_nodes'],'fallback_parents':data['fallback_parents']},indent=2))
