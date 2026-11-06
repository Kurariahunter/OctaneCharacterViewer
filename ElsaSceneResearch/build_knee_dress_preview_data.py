"""Merge bounded torso channels with native leg-world transforms for a flat skin palette."""
import json,copy,numpy as np
from pathlib import Path
R=Path(__file__).parent
model=json.loads((R/'elsa-preview-model.json').read_text());base=json.loads(Path(r'C:\Users\Kurar\Disney Reloaded\Assets\DI3ElsaHipsResearch\Editor\elsa-hips-animation.json').read_text());native=json.loads((R/'native-knee-skin-clip-validation.json').read_text());upper=json.loads((R/'native-knee-upper-dress-samples.json').read_text());
for c,u in zip(native['clips'],upper['clips']):
 assert c['name']==u['name'] and len(c['samples'])==len(u['samples'])
 for f,g in zip(c['samples'],u['samples']):
  assert abs(f['time']-g['time'])<1e-6
  f['worlds'].update(g['worlds'])
dynamic=json.loads((R/'native-knee-dynamic-dress-samples.json').read_text())
for c,d in zip(native['clips'],dynamic['clips']):
 assert c['name']==d['name'] and len(c['samples'])==len(d['samples'])
 for f,g in zip(c['samples'],d['samples']):
  assert abs(f['time']-g['time'])<1e-6
  f['worlds'].update(g['worlds'])
worlds=[np.array(b['world']).reshape(4,4) for b in model['bones']];locals=[worlds[i] if b['parent']<0 else np.linalg.inv(worlds[b['parent']])@worlds[i] for i,b in enumerate(model['bones'])];clips=[];maxshear=0
for original,new in zip(base['clips'],native['clips']):
 assert original['name']==new['name'] and len(original['samples'])==len(new['samples']);samples=[]
 for a,b in zip(original['samples'],new['samples']):
  assert abs(a['time']-b['time'])<1e-6
  source={p['bone']:np.array(p['matrix']).reshape(4,4) for p in a['transforms']};overrides={k:np.array(v).reshape(4,4) for k,v in b['worlds'].items()};cache={}
  def world(i):
   if i in cache:return cache[i]
   bone=model['bones'][i];name=bone['name'];p=bone['parent']
   m=overrides[name] if name in overrides else (np.eye(4) if p<0 else world(p))@source.get(name,locals[i]);cache[i]=m;return m
  poses=[]
  for i,bone in enumerate(model['bones']):
   m=world(i);scale=np.linalg.norm(m[:3,:3],axis=0);rot=m[:3,:3]/scale;shear=float(np.max(abs(rot.T@rot-np.eye(3))));maxshear=max(maxshear,shear)
   if shear>2e-5 or np.linalg.det(rot)<0:raise ValueError(('non TRS skin output',bone['name'],shear))
   poses.append({'bone':bone['name'],'matrix':m.flatten().tolist()})
  samples.append({'time':a['time'],'transforms':poses})
 clips.append({'name':original['name'].replace('_HipsBodyShoulders','_AuthoredKneeDressPartial'),'duration':original['duration'],'samples':samples})
for b in model['bones']:b['parent']=-1
model['parent_notes']=['Independent palette bones preserve native world transforms without parent-relative shear. Original weights and inverse binds retained.']
(R/'elsa-knee-dress-model.json').write_text(json.dumps(model,separators=(',',':')))
(R/'elsa-knee-dress-animation.json').write_text(json.dumps({'scope':'Partial original idle: bounded torso channels plus native leg/foot world transforms. Independent world-space palette, not reusable humanoid rig or full BENT playback. UpperDress source outputs included. Lower dress sampled through native DynamicChain and Aim with explicit zero external force, reset start and previous-frame orientation feedback; full loader/update-order fidelity not demonstrated. Arm and face local controls held at bind.','animated_bones':[b['name'] for b in model['bones']],'clips':clips},separators=(',',':')))
(R/'knee-dress-export-validation.json').write_text(json.dumps({'max_world_TRS_shear_residual':maxshear,'bones':len(model['bones']),'clips':[(c['name'],len(c['samples'])) for c in clips]},indent=2));print('PASS',maxshear)
