"""Cache-wide timing, coverage and fallback invariants for the continuous adapter."""
from pathlib import Path
import json,hashlib,numpy as np
P=Path(__file__).parent
cache=json.loads((P/'wiiu-controls-pc-reference-viewer-continuous.json').read_text())
clip=cache['clips'][0];samples=clip['samples'];assert len(samples)==153
times=np.array([s['time']for s in samples]);assert times[0]==0 and times[-1]==clip['duration']and np.all(np.diff(times)>0)
assert np.max(abs(np.diff(times)-clip['duration']/152))<1e-12
assert len(cache['source_skin_nodes'])==49 and len(cache['fallback_parents'])==13
unique=set();max_fallback_error=0.;bind_relative={}
for sample in samples:
 poses={p['bone']:np.array(p['matrix']).reshape(4,4)for p in sample['transforms']}
 assert len(poses)==62 and all(np.isfinite(m).all()for m in poses.values())
 unique.add(hashlib.sha256(json.dumps(sample['transforms'],sort_keys=True).encode()).hexdigest())
 for bone,parent in cache['fallback_parents'].items():
  local=np.linalg.inv(poses[parent])@poses[bone]if parent else poses[bone]
  if bone not in bind_relative:bind_relative[bone]=local
  max_fallback_error=max(max_fallback_error,float(np.max(abs(local-bind_relative[bone]))))
assert len(unique)>100 and max_fallback_error<1e-8
report={'pass':True,'samples':len(samples),'unique_palettes':len(unique),'source_outputs':49,'fallback_outputs':13,'maximum_fallback_local_drift':max_fallback_error,'nominal_hz':152/clip['duration'],'scope':'All-cache timing/coverage/fallback checks. Poses evaluated from source curves, not interpolated. No claim of complete Wii U runtime or renderer parity.'}
(P/'continuous-adapter-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
