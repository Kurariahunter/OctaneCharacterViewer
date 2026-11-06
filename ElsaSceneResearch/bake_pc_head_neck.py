"""Bake file-only PC head/neck graph outputs for Unity."""
import json,copy
from pathlib import Path
from evaluate_pc_head import *
from read_pc_idle_files import Clip
OUTPUTS={'Neck':457,'Head':462};reflect=np.diag([-1,1,1,1]);worlds={get(x,'Name'):np.linalg.inv(np.array(get(x,'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T)for x in allnodes(T,'Influence')}
checks=[]
for name,parent in [('Neck','Spine3'),('Head','Neck')]:
 expected=np.linalg.inv(worlds[parent])@worlds[name];actual=Eval().run(OUTPUTS[name]);error=float(np.max(abs(actual-expected)));assert error<0.00001;checks.append({'bone':name,'node':OUTPUTS[name],'bind_error':error})
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
   m=e.run(node);assert np.max(abs(m[:3,:3].T@m[:3,:3]-np.eye(3)))<1e-5;poses.append({'bone':bone,'matrix':(reflect@m@reflect).flatten().tolist()})
  samples.append({'time':time,'transforms':poses})
 clips.append({'name':name+'_PC_HeadNeck','duration':clip.duration,'samples':samples,'clipdata_sha256':clip.sha})
summary=[]
for clip in clips:
 spans={b:max(float(np.max(abs(np.array(s['transforms'][j]['matrix'])-clip['samples'][0]['transforms'][j]['matrix'])))for s in clip['samples'])for j,b in enumerate(OUTPUTS)};assert max(spans.values())>0.001;summary.append({'clip':clip['name'],'frames':len(clip['samples']),'matrix_spans':spans})
report={'scope':'File-only verified PC clips, structurally mapped control channels through bounded PC head/neck graph and original native curve/Euler/Dilation connection routines. No capture values. Other bones remain bind pose; no base-layer blending, full-body animation or secondary dynamics.','model_sha256':PC_RIG.sha,'bind_checks':checks,'clips':clips}
(ROOT/'pc-head-neck-animation.json').write_text(json.dumps(report,separators=(',',':')));(ROOT/'pc-head-neck-bake-validation.json').write_text(json.dumps({'bind_checks':checks,'clips':summary},indent=2));print(checks,summary)
