"""File-derived PC skin-world palette; native leg compensation and reset-only dress."""
import json,re
from pathlib import Path
from evaluate_pc_temporal_dress import *
from native_pc_chain_step import ChainStates
from evaluate_pc_raw_transform import affine
from native_pc_transform_scale import point
from read_pc_idle_files import Clip
from pc_graph_controls import apply

R=ROOT;reflect=np.diag([-1,1,1,1]);influences={int(x['value']):x for x in allnodes(T,'Influence')}
worlds={get(x,'Name'):np.linalg.inv(np.array(get(x,'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T)for x in influences.values()}
prefab=Path('C:/Users/Kurar/Disney Reloaded/Assets/DI3Converted/fro_elsa/fro_elsa_Rigged.prefab').read_text()
objects={};transforms={}
for kind,ident,body in re.findall(r'--- !u!(\d+) &(\d+)\n(.*?)(?=--- !u!|\Z)',prefab,re.S):
 if kind=='1':objects[int(ident)]=re.search(r'^  m_Name: (.*)$',body,re.M)[1]
 if kind=='4':transforms[int(ident)]={'object':int(re.search(r'm_GameObject: \{fileID: (\d+)\}',body)[1]),'parent':int(re.search(r'm_Father: \{fileID: (\d+)\}',body)[1])}
parents={objects[t['object']]:objects[transforms[t['parent']]['object']] if t['parent']in transforms else None for t in transforms.values() if objects[t['object']]in worlds}
parents={name:(parent if parent in worlds else None)for name,parent in parents.items()}
for side in ['Left','Right']:
 parents.update({'Shoulder_OL_'+side:'Shoulder_Spin_'+side,'Elbow_OL_'+side:'Shoulder_'+side,'Thumb2_'+side:'Thumb1_'+side,'Forearm_OL_'+side:'Elbow_'+side})
for name in ['LowerLidLeft','LowerLidRight','UpperLidLeft','UpperLidRight','hair02']:parents[name]='Head'
assert set(parents)==set(worlds)
names=['Body','Spine1','Spine2','Spine3','Clavicle_Left','Clavicle_Right','Shoulder_Spin_Left','Shoulder_Spin_Right','Neck','Head','Shoulder_Left','Shoulder_Right','Elbow_Left','Elbow_Right','Hand_Left','Hand_Right','Shoulder_OL_Left','Shoulder_OL_Right','Elbow_OL_Left','Elbow_OL_Right','Hips','Knee_Right','Ball_Right','Toes_Right','Knee_Left','Ball_Left','Toes_Left','UpperDress_Left','UpperDress_Right','dressLeftStart','dressRightStart']
skin={}
for a in allnodes(T,'Association'):
 if get(a,'Type')!='SkinInfluence':continue
 ids=[i for i,path in PC_RIG.paths.items()if path==get(a,'NodeName')]
 if len(ids)!=1:raise ValueError('ambiguous skin association')
 prod,attr=PROD[ids[0]]
 if get(prod,'Type')not in ('TransformToMatrix4x4VariantProcessor','DilationToMatrix4x4VariantProcessor'):raise ValueError('unrecognized skin matrix producer')
 node=dict(zip(get(prod,'DataNodeAttributes'),get(prod,'DataNodeRefs')))['Input']
 for ref in get(a,'InfluenceRefs'):skin[get(influences[ref],'Name')]=node
assert set(skin)==set(worlds)
bindlocals={name:np.linalg.inv(worlds[parent])@worlds[name] if parent else worlds[name] for name,parent in parents.items()}
clips=[];checks=[];dresschecks=[];maxshear=0;scale_ranges=[]
for name in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
 clip=Clip(next((R/'InstalledGameAssetCheck/IdleMotions').rglob(name+'.oct')),PC_RIG);frames=round(clip.duration*30);samples=[];worst=0;states=ChainStates()
 for frame in range(frames+1):
  time=clip.duration*frame/frames;e=TemporalDressEval(states,frame,clip.duration/frames);apply(e,clip.sample(time));out={bone:affine(e.raw.run(skin[bone])) if get(DN[skin[bone]],'Type')=='Transform' else e.run(skin[bone])for bone in names}
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
  if any(row['native_last_frame']!=frame for row in e.dress_checks):raise ValueError('native frame stamp did not advance')
  dresschecks.extend(dict(clip=name,frame=frame,**row)for row in e.dress_checks)
  for bone in worlds:
   m=world(bone);sc=np.linalg.norm(m[:3,:3],axis=0);rot=m[:3,:3]/sc;shear=float(np.max(abs(rot.T@rot-np.eye(3))));maxshear=max(maxshear,shear)
   if shear>2e-5 or min(sc)<=0 or np.linalg.det(rot)<0:raise ValueError(('non-TRS palette',bone,shear))
   scale_ranges.extend(sc.tolist());poses.append({'bone':bone,'matrix':(reflect@m@reflect).flatten().tolist()})
  samples.append({'time':time,'transforms':poses})
 clips.append({'name':name+'_PC_TemporalDress','duration':clip.duration,'samples':samples,'clipdata_sha256':clip.sha});print(name,len(samples),'endpoint',worst,flush=True)
data={'scope':'PC file-only controls through source skin world output paths; native 8/3 IK and scale compensation. 31 source-driven bones; remaining palette bones inherit bind offsets. Lower dress uses persistent original native DynamicChain updates, authored PC particle scalars, zero external force and no capsule scene. Previous local Aim orientation feeds the next frame; each clip starts reset. Exact game scene forces, collisions, update order and seamless looping are not established. Independent palette export avoids Unity parent-scale multiplication. Facial/finger motion and game layer blending incomplete.','model_sha256':PC_RIG.sha,'source_skin_nodes':{n:skin[n]for n in names},'fallback_parents':{n:parents[n]for n in worlds if n not in names},'clips':clips}
(R/'pc-temporal-dress-animation.json').write_text(json.dumps(data,separators=(',',':')))
(R/'pc-temporal-dress-validation.json').write_text(json.dumps({'model_sha256':PC_RIG.sha,'source_bones':len(names),'palette_bones':len(worlds),'max_TRS_shear':maxshear,'min_scale':min(scale_ranges),'max_scale':max(scale_ranges),'max_endpoint_error':max(c['endpoint_error']for c in checks),'checks':checks,'max_dress_root_error':max(c['root_error']for c in dresschecks),'max_dress_segment_length_error':max(c['segment_length_error']for c in dresschecks),'dress_checks':dresschecks,'source_skin_nodes':data['source_skin_nodes'],'fallback_parents':data['fallback_parents']},indent=2))
