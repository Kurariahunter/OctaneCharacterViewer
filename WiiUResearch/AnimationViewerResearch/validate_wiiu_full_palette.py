"""Source-association coverage and zero-change regression for the full idle cache."""
import json,numpy as np
from wiiu_pc_graph_adapter import Adapter,P,refs
a=Adapter();cache=json.loads((P/'wiiu-source-mesh-animation-full.json').read_text());prior=json.loads((P/'wiiu-source-mesh-animation-dress.json').read_text());hair=json.loads((P/'wiiu-source-hair-animation.json').read_text());bindings=json.loads((P/'wiiu-skin-associations.json').read_text());R=np.diag([-1,1,1,1])
expected={b['bone']:refs(a.producers[b['matrix_node']][0])['Input']for b in bindings}
assert cache['source_skin_nodes']==expected and len(expected)==64 and cache['fallback_parents']=={}
assert len(cache['clips'][0]['samples'])==len(prior['clips'][0]['samples'])==len(hair['samples'])==153
max_prior=max_hair=0.;minimum_determinant=float('inf')
for sample,old,raw in zip(cache['clips'][0]['samples'],prior['clips'][0]['samples'],hair['samples']):
 assert sample['time']==old['time']and abs(sample['time']-raw['time'])<1e-10
 poses={p['bone']:np.array(p['matrix']).reshape(4,4)for p in sample['transforms']};previous={p['bone']:np.array(p['matrix']).reshape(4,4)for p in old['transforms']}
 assert len(poses)==len(sample['transforms'])==64 and set(poses)==set(expected)
 for m in poses.values():
  assert np.isfinite(m).all()and np.max(abs(m[3]-[0,0,0,1]))<1e-8
  determinant=float(np.linalg.det(m[:3,:3]));assert determinant>1e-8;minimum_determinant=min(minimum_determinant,determinant)
 for name in prior['source_skin_nodes']:max_prior=max(max_prior,float(np.max(abs(poses[name]-previous[name]))))
 for row in raw['outputs']:max_hair=max(max_hair,float(np.max(abs(poses[row['bone']]-R@np.array(row['matrix'])@R))))
assert max_prior==max_hair==0
assert len(hair['chain_checks'])==425 and all(c['tick']==i and c['native_last_frame']==i for i,c in enumerate(hair['chain_checks']))
assert len(hair['parameter_checks'])==3 and all(c['equivalent']for c in hair['parameter_checks'])
report={'pass':True,'source_associations':64,'evaluated_outputs':64,'fallbacks':0,'samples':153,'maximum_prior_61_change':max_prior,'maximum_hair_matrix_change':max_hair,'minimum_basis_determinant':minimum_determinant,'chronological_hair_ticks':425,'scope':'Complete palette for this supported clip fixture; does not establish full engine, Wii U numerical execution or live game parity.'}
(P/'wiiu-full-palette-regression.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report)
