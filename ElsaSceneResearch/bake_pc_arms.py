"""Bake file-only PC upper body, arms and deformation helpers graph outputs for Unity."""
import json,copy
from pathlib import Path
from evaluate_pc_arms import *
from read_pc_idle_files import Clip
OUTPUTS={'Body':134,'Spine1':139,'Spine2':144,'Spine3':149,'Clavicle_Left':154,'Clavicle_Right':179,'Shoulder_Spin_Left':158,'Shoulder_Spin_Right':183,'Neck':457,'Head':462,'Shoulder_Left':162,'Shoulder_Right':187,'Elbow_Left':167,'Elbow_Right':192,'Hand_Left':172,'Hand_Right':197,'Shoulder_OL_Left':616,'Shoulder_OL_Right':619,'Elbow_OL_Left':490,'Elbow_OL_Right':494};reflect=np.diag([-1,1,1,1]);worlds={get(x,'Name'):np.linalg.inv(np.array(get(x,'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T)for x in allnodes(T,'Influence')}
checks=[];pivots={}
PARENTS={'Body':None,'Spine1':'Body','Spine2':'Spine1','Spine3':'Spine2','Clavicle_Left':'Spine3','Clavicle_Right':'Spine3','Shoulder_Spin_Left':'Clavicle_Left','Shoulder_Spin_Right':'Clavicle_Right','Neck':'Spine3','Head':'Neck','Shoulder_Left':'Shoulder_Spin_Left','Shoulder_Right':'Shoulder_Spin_Right','Elbow_Left':'Shoulder_Left','Elbow_Right':'Shoulder_Right','Hand_Left':'Elbow_Left','Hand_Right':'Elbow_Right','Shoulder_OL_Left':'Shoulder_Spin_Left','Shoulder_OL_Right':'Shoulder_Spin_Right','Elbow_OL_Left':'Shoulder_Left','Elbow_OL_Right':'Shoulder_Right'}
for name,parent in PARENTS.items():
 expected=np.linalg.inv(worlds[parent])@worlds[name] if parent else worlds[name];actual=Eval().run(OUTPUTS[name]);rotation_error=float(np.max(abs(actual[:3,:3]-expected[:3,:3])));pivot=expected[:3,3]-actual[:3,3];authored_error=float(np.max(abs(actual[:3,:3]-stored(DN[OUTPUTS[name]])[:3,:3])));
 if name in ('Shoulder_Left','Shoulder_Right'):assert authored_error<0.00001
 elif name.startswith('Shoulder_OL_'):assert np.max(abs(actual[:3,:3]-Eval().run(162 if name.endswith('Left') else 187)[:3,:3]))<0.00001
 else:assert rotation_error<0.00001
 assert max(abs(pivot))<0.001;pivots[name]=pivot;checks.append({'bone':name,'parent':parent,'node':OUTPUTS[name],'rotation_bind_error':rotation_error,'authored_cached_rotation_error':authored_error,'preserved_skin_pivot_delta':pivot.tolist()})
clips=[]
for name in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
 clip=Clip(next((ROOT/'InstalledGameAssetCheck/IdleMotions').rglob(name+'.oct')),PC_RIG);frames=round(clip.duration*30);samples=[]
 for frame in range(frames+1):
  time=clip.duration*frame/frames;controls=clip.sample(time);e=Eval()
  for record in controls.values():
   node=record['source_node']
   if node is None or node in PROD:continue
   fields={c['name']:copy.deepcopy(c['value']) for c in next((c for c in DN[node]['children']if c['name']=='Data'),{'children':[]})['children']};channels=record['channels']
   if '0'in channels:fields['Translation']=channels['0'][:]
   for op in [1,2,3]:
    if str(op)in channels:fields.setdefault('Translation',[0,0,0])[op-1]=channels[str(op)][0]
   if '4'in channels:fields['Orientation']=channels['4'][:]
   if '10'in channels:fields['Value']=channels['10'][0]
   # Only unit scale paths are supported by this bounded evaluator.
   for op in [5,6,7,8,9]:
    if str(op)in channels and max(abs(v-1)for v in channels[str(op)])>1e-5:raise ValueError('nonunit PC control scale')
   e.overrides[node]=fields
  poses=[]
  for bone,node in OUTPUTS.items():
   m=e.run(node).copy();m[:3,3]+=pivots[bone];assert np.max(abs(m[:3,:3].T@m[:3,:3]-np.eye(3)))<1e-5;poses.append({'bone':bone,'matrix':(reflect@m@reflect).flatten().tolist()})
  samples.append({'time':time,'transforms':poses})
 clips.append({'name':name+'_PC_UpperBodyArms','duration':clip.duration,'samples':samples,'clipdata_sha256':clip.sha})
summary=[]
for clip in clips:
 spans={b:max(float(np.max(abs(np.array(s['transforms'][j]['matrix'])-clip['samples'][0]['transforms'][j]['matrix'])))for s in clip['samples'])for j,b in enumerate(OUTPUTS)};assert max(spans.values())>0.001;summary.append({'clip':clip['name'],'frames':len(clip['samples']),'matrix_spans':spans})
report={'scope':'File-only verified PC clips, structurally mapped control channels through bounded PC upper-body/arm/helper graph; shoulders retain authored default rather than force mesh bind orientation; explicit sub-millimeter skin pivot preservation and original native curve/Euler/Dilation connection routines. No capture values. Legs, fingers and dress remain at defaults; feet not planted; no base-layer blending, full-body animation or secondary dynamics.','model_sha256':PC_RIG.sha,'bind_checks':checks,'clips':clips}
(ROOT/'pc-arms-animation.json').write_text(json.dumps(report,separators=(',',':')));(ROOT/'pc-arms-bake-validation.json').write_text(json.dumps({'bind_checks':checks,'clips':summary},indent=2));print(checks,summary)
