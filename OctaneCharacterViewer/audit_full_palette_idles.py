"""Validate the three bounded full-palette idle artifacts and summarize motion."""
import hashlib,json,math
from pathlib import Path
R=Path(__file__).parent/'NativePreviews'
rows=[];reference=None;hashes=set()
for letter in 'ABC':
 path=R/f'native-idle{letter}-full-palette.json'
 data=json.loads(path.read_text());validation=json.loads(path.with_suffix('.validation.json').read_text())
 assert validation['pass'] and validation['source_bones']==validation['palette_bones']==62
 assert not data['fallback_parents']
 source=Path(data['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==data['source_sha256']
 hashes.add(data['source_sha256'])
 names=set(data['source_skin_nodes']);assert len(names)==62
 if reference is None:reference=names
 assert names==reference
 for key in ('facial_source_paths','eyelid_source_paths','eye_source_paths','forearm_source_paths'):assert data[key]['enabled']
 assert data['explicit_finger_transition']['state']['state_path'].endswith('/Idle'+letter)
 clip=data['clips'][0];samples=clip['samples'];assert len(samples)==validation['samples'] and len(samples)>1
 initial={row['bone']:row['matrix'] for row in samples[0]['transforms']}
 spans={bone:0. for bone in names};previous=-1.
 for sample in samples:
  assert sample['time']>previous;previous=sample['time']
  matrices={row['bone']:row['matrix'] for row in sample['transforms']}
  assert len(sample['transforms'])==62 and matrices.keys()==names
  for bone,matrix in matrices.items():
   assert len(matrix)==16 and all(math.isfinite(v) for v in matrix)
   spans[bone]=max(spans[bone],max(abs(a-b) for a,b in zip(matrix,initial[bone])))
 assert abs(samples[-1]['time']-clip['duration'])<1e-8
 rows.append(dict(idle=letter,artifact=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_sha256=data['source_sha256'],duration=clip['duration'],validation=validation,fallback_count=0,unmapped_ports=data['unmapped_ports'],matrix_component_change_from_first_sample=spans))
assert len(hashes)==3
report=dict(passed=True,profiles=rows,scope='Three distinct hash-verified PC Elsa idle sources, each with all62 palette bones evaluated and no bind-offset palette fallbacks. Finite coverage and existing geometric invariants only. Motion component changes are diagnostics, not visual accuracy scores; game scheduling and missing-channel policies remain explicit fixtures.')
(R/'full-palette-idles-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=True,idles=[dict(idle=r['idle'],duration=r['duration'],samples=r['validation']['samples'],source_bones=62,fallbacks=0) for r in rows])))
