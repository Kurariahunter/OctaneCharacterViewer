"""Check opt-in eyelid bake changes only the four intended palette bones."""
import json
from pathlib import Path
R=Path(__file__).parent/'NativePreviews'
old=json.loads((R/'native-idleC-facial-paths.json').read_text())
new=json.loads((R/'native-idleC-eyelid-paths.json').read_text())
a=old['clips'][0]['samples'];b=new['clips'][0]['samples'];assert len(a)==len(b)
allowed={'UpperLidLeft','UpperLidRight','LowerLidLeft','LowerLidRight'}
changed=set();maximum=0.;changed_samples=0
for x,y in zip(a,b):
 assert x['time']==y['time']
 before={t['bone']:t['matrix'] for t in x['transforms']};after={t['bone']:t['matrix'] for t in y['transforms']}
 assert before.keys()==after.keys()
 any_change=False
 for bone in before:
  delta=max(abs(v-w) for v,w in zip(before[bone],after[bone]))
  if delta:
   assert bone in allowed,(bone,delta)
   changed.add(bone);maximum=max(maximum,delta);any_change=True
 changed_samples+=any_change
assert changed==allowed
report=dict(passed=True,samples=len(a),changed_samples=changed_samples,changed_bones=sorted(changed),max_matrix_component_difference=maximum,source_bones=len(new['source_skin_nodes']),scope='Numerical palette comparison only: all non-eyelid matrices exactly unchanged. Difference is not an angle, distance or game-parity error score.')
(R/'eyelid-paths-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
