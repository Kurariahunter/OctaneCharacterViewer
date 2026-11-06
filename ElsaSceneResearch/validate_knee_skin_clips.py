"""Compare native skin-chain ankle outputs with original clip IK targets."""
import json,numpy as np
from pathlib import Path
from evaluate_native_skin import NativeSkinEval,affine
from evaluate_elsa_feet import FootEval
from native_transform_scale import point,compose
from evaluate_elsa_head import stored,DN
R=Path(__file__).parent
model=json.loads((R/'elsa-preview-model.json').read_text());bones={b['name']:np.array(b['world']).reshape(4,4) for b in model['bones']};reflect=np.diag([-1,1,1,1]);checks=[]
for side,upper,knee,kout,aout,target in [('Left',424,430,432,441,450),('Right',453,459,461,470,479)]:
 e=FootEval()
 for i in [upper,knee]:e.cache[i]=stored(DN[i])
 n=NativeSkinEval(e)
 for i in [upper,knee]:
  data=next(c for c in DN[i]['children'] if c['name']=='Data');f={c['name']:c['value'] for c in data['children']};n.cache[i]=compose(f.get('Orientation',[0,0,0,1]),f.get('Translation',[0,0,0]),f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
 bindlike=reflect@affine(n.run(kout))@reflect
 checks.append({'side':side,'stored_local_chain_knee_bind_error':float(np.max(abs(bindlike-bones['Knee_'+side]))),'scope':'Stored authored upper/knee locals substituted for IK outputs; explicit test only.'})
source=json.loads((R/'elsa-knee-dress-control-samples.json').read_text());clips=[]
for clip in source['clips']:
 rows=[]
 for sample in clip['samples']:
  e=FootEval();e.overrides={int(k):v for k,v in sample['controls'].items()};n=NativeSkinEval(e);worlds={};legs=[]
  for side,kout,aout,target in [('Left',432,441,450),('Right',461,470,479)]:
   raw=n.run(aout);actual=point(raw,[0,0,0]);wanted=point(n.run(419),e.run(target));err=float(np.linalg.norm(actual-wanted))
   legs.append({'side':side,'ankle_target_world_error':err,'ankle_raw':raw,'knee_raw':n.run(kout)})
   for name,i in [('Knee_'+side,kout),('Ankle_'+side,aout)]:worlds[name]=(reflect@affine(n.run(i))@reflect).flatten().tolist()
  for name,i in [('Ball_Left',482),('Toes_Left',640),('Ball_Right',486),('Toes_Right',645)]:worlds[name]=(reflect@affine(n.run(i))@reflect).flatten().tolist()
  worlds['Hips']=(reflect@affine(n.run(419))@reflect).flatten().tolist()
  rows.append({'time':sample['time'],'worlds':worlds,'legs':legs})
 clips.append({'name':clip['name'],'duration':clip['duration'],'samples':rows,'max_ankle_target_error':max(l['ankle_target_world_error'] for f in rows for l in f['legs'])})
report={'scope':'Native Transform operators on explicit source output paths. Bounded FootEval supplies clip controls, Dilation, IK. Positive scales only; not complete original loader or full-body animation.','stored_local_checks':checks,'clips':clips}
(R/'native-knee-skin-clip-validation.json').write_text(json.dumps(report,separators=(',',':')));print(checks);print([(c['name'],len(c['samples']),c['max_ankle_target_error']) for c in clips])
