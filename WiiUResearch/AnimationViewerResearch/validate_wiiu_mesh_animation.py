"""Source-mesh cache invariants, exact leg/upper matrices and bind skin identity."""
import json,numpy as np
from wiiu_pc_graph_adapter import P
mesh=json.loads((P.parents[1]/'OctaneCharacterViewer/Data/elsa-wiiu-mesh.json').read_text());cache=json.loads((P/'wiiu-source-mesh-animation.json').read_text());old=json.loads((P/'wiiu-controls-pc-reference-viewer-continuous.json').read_text());legs=json.loads((P/'wiiu-source-leg-animation.json').read_text())
assert len(mesh['bones'])==len(set(mesh['bones']))==64 and len(mesh['vertices'])==5419
assert len(cache['source_skin_nodes'])==57 and len(cache['fallback_parents'])==7
assert len(cache['clips'][0]['samples'])==153
maximum_upper=maximum_leg=maximum_drift=maximum_bind=0.;locals={};R=np.diag([-1,1,1,1])
for bind in mesh['bindposes']:
 b=np.array(bind).reshape(4,4);maximum_bind=max(maximum_bind,float(np.max(abs(np.linalg.inv(b)@b-np.eye(4)))))
for w in mesh['weights']:assert len(w['weights'])==len(w['indices'])==4 and abs(sum(w['weights'])-1)<1e-6 and all(0<=i<64 for i in w['indices'])
for sample,prior,leg in zip(cache['clips'][0]['samples'],old['clips'][0]['samples'],legs['samples']):
 assert sample['time']==prior['time']==leg['time'];poses={p['bone']:np.array(p['matrix']).reshape(4,4)for p in sample['transforms']};previous={p['bone']:np.array(p['matrix']).reshape(4,4)for p in prior['transforms']}
 assert len(poses)==64 and all(np.isfinite(m).all()for m in poses.values())
 for name in old['source_skin_nodes']:maximum_upper=max(maximum_upper,float(np.max(abs(poses[name]-previous[name]))))
 for row in leg['outputs']:maximum_leg=max(maximum_leg,float(np.max(abs(poses[row['bone']]-R@np.array(row['matrix'])@R))))
 for name,parent in cache['fallback_parents'].items():
  local=np.linalg.inv(poses[parent])@poses[name]if parent else poses[name]
  if name not in locals:locals[name]=local
  maximum_drift=max(maximum_drift,float(np.max(abs(local-locals[name]))))
assert maximum_upper==maximum_leg==0 and maximum_drift<1e-8 and maximum_bind<1e-10
report={'pass':True,'source_outputs':57,'fallbacks':7,'bones':64,'samples':153,'maximum_prior_49_matrix_change':maximum_upper,'maximum_source_leg_matrix_change':maximum_leg,'maximum_fallback_local_drift':maximum_drift,'maximum_bind_identity_error':maximum_bind}
(P/'wiiu-mesh-animation-regression.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report)
