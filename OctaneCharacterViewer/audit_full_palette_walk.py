"""Check supported locomotion coverage and isolate newly enabled bone changes."""
import argparse,hashlib,json,math
from pathlib import Path
R=Path(__file__).parent/'NativePreviews'
p=argparse.ArgumentParser();p.add_argument('--motion',choices=('walk','run','runrf','runr'),default='walk');motion=p.parse_args().motion
old=json.loads((R/f'native-{motion}-coverage-baseline.json').read_text())
new=json.loads((R/f'native-{motion}-full-palette.json').read_text())
validation=json.loads((R/f'native-{motion}-full-palette.validation.json').read_text())
assert validation['pass'] and validation['source_bones']==validation['palette_bones']==62
assert not new['fallback_parents'] and old['source_sha256']==new['source_sha256']
assert hashlib.sha256(Path(new['source']).read_bytes()).hexdigest()==new['source_sha256']
allowed=set(new['source_skin_nodes'])-set(old['source_skin_nodes']);assert len(allowed)==16
a=old['clips'][0]['samples'];b=new['clips'][0]['samples'];assert len(a)==len(b)
changed=set();maximum=0.;previous=-1.;deltas={bone:0. for bone in allowed}
for x,y in zip(a,b):
 assert x['time']==y['time'] and y['time']>previous;previous=y['time']
 before={t['bone']:t['matrix'] for t in x['transforms']};after={t['bone']:t['matrix'] for t in y['transforms']}
 assert before.keys()==after.keys()==set(new['source_skin_nodes'])
 for bone in before:
  assert len(after[bone])==16 and all(math.isfinite(v) for v in after[bone])
  delta=max(abs(v-w) for v,w in zip(before[bone],after[bone]))
  if delta:
   assert bone in allowed,(bone,delta)
   changed.add(bone);maximum=max(maximum,delta);deltas[bone]=max(deltas[bone],delta)
if motion!='walk':assert new['native_group_composition']==old['native_group_composition']
report=dict(passed=True,motion=motion,source_sha256=new['source_sha256'],source_bones=62,fallback_count=0,samples=len(b),duration=new['clips'][0]['duration'],validation=validation,added_bones=sorted(allowed),changed_bones=sorted(changed),max_matrix_component_difference=maximum,per_added_bone_matrix_difference=deltas,unmapped_ports=new['unmapped_ports'],upper_unmapped_ports=new['upper_unmapped_ports'],scope='Same existing PC Elsa '+motion+' composition and explicit passive seed, with16 additional source graph paths. All previously evaluated palette matrices remain exactly unchanged. This is coverage and numerical regression validation, not game parity, native layer scheduling or a running finger fix.')
(R/f'full-palette-{motion}-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('per_added_bone_matrix_difference','unmapped_ports','upper_unmapped_ports')}))
