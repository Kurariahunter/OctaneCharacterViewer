"""Offline replay validation; original capture unchanged."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import replay,sha
R=Path(__file__).parent
P=R.parent/"OctaneLiveInspector/Captures/octane_20261017_151848_1792264728047355700.json"
d=json.loads(P.read_text())
rows=[]
for candidate in d['samples'][0]['pc_lean_ik_processors']:
 addr=candidate['address'];frames=[next(p for p in s['pc_lean_ik_processors'] if p['address']==addr) for s in d['samples']]
 # Skip unrelated zero-initialized connections; these aren't usable solver inputs.
 if not any(bytes.fromhex(candidate['inputs'][1]['payload_prefix_hex64'])[:12]):continue
 errors=[]
 for frame in frames:
  expected=replay(frame);actual=[struct.unpack('<'+('4f' if i<2 else 'f'),bytes.fromhex(x['payload_prefix_hex64'])[:16 if i<2 else 4]) for i,x in enumerate(frame['outputs'])]
  errors.append([min(max(abs(a-b) for a,b in zip(x,y)),max(abs(a+b) for a,b in zip(x,y))) if i<2 else abs(x[0]-y[0]) for i,(x,y) in enumerate(zip(expected,actual))])
 row={'address':addr,'network':candidate['outputs'][0]['network_reference_raw'],'samples':len(frames),'distinct_output_values':[len({f['outputs'][i]['payload_prefix_hex64'][:32 if i<2 else 8] for f in frames}) for i in range(3)],'max_component_errors':[max(e[i] for e in errors) for i in range(3)],'per_sample_errors':errors}
 rows.append(row);print({k:v for k,v in row.items() if k!='per_sample_errors'},flush=True)
report={'capture':str(P),'exe_sha256':sha,'scope':'Original PC 8/3 solver replay with captured numeric slots. Cached input values used without recursively executing producers; live reads non-atomic. No semantic mapping or complete animation recovery claimed.','solvers':rows}
(R/'pc-lean-replay-validation.json').write_text(json.dumps(report,indent=2))
