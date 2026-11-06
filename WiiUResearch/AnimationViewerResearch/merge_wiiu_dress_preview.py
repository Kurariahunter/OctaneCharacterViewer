"""Replace only four source dress fallbacks; preserve57 established matrices exactly."""
import json,numpy as np
from wiiu_pc_graph_adapter import P
base=json.loads((P/'wiiu-source-mesh-animation.json').read_text());dress=json.loads((P/'wiiu-source-dress-animation.json').read_text());R=np.diag([-1,1,1,1]);samples=[];nodes=dict(base['source_skin_nodes']);maximum_prior=0.
assert len(nodes)==57 and len(dress['samples'])==153
for prior,frame in zip(base['clips'][0]['samples'],dress['samples']):
 assert abs(prior['time']-frame['time'])<1e-10
 poses={p['bone']:p['matrix']for p in prior['transforms']}
 for output in frame['outputs']:
  name=output['bone'];assert name not in base['source_skin_nodes']
  poses[name]=(R@np.array(output['matrix'])@R).flatten().tolist();nodes[name]=output['source_node']
 for p in prior['transforms']:
  if p['bone']in base['source_skin_nodes']:maximum_prior=max(maximum_prior,float(np.max(abs(np.array(poses[p['bone']])-p['matrix']))))
 assert all(np.isfinite(m).all()for m in poses.values())
 samples.append({'time':prior['time'],'transforms':[{'bone':p['bone'],'matrix':poses[p['bone']]}for p in prior['transforms']]})
assert maximum_prior==0 and len(nodes)==61
base.update(source_skin_nodes=nodes,reference_source_outputs=61,fallback_parents={n:p for n,p in base['fallback_parents'].items()if n not in nodes},scope='Actual Wii U64-bone Elsa mesh:61source-evaluated outputs, including four dress paths with reused native PC chain solver; three hair fallbacks. Explicit gravity/warmup fixture; no scene collision or full Wii U game parity.')
assert len(base['fallback_parents'])==3
base['fixture_assumptions']=['Three hair outputs retain bind-relative parent fixtures.','Dress chains use source-matched particle parameters,120phase-zero warmup ticks,60Hzchronological simulation and explicit PC gravity fixture; no capsule collision scene.','Actor scheduling and Wii U CPU numerical parity remain unverified.']
base['clips'][0].update(name='WiiU_Elsa_SourceMesh_SourceDress_61_of_64',samples=samples)
(P/'wiiu-source-mesh-animation-dress.json').write_text(json.dumps(base,separators=(',',':')),encoding='utf-8')
report={'pass':True,'samples':153,'bones':64,'evaluated_outputs':61,'fallbacks':3,'maximum_prior_57_matrix_change':maximum_prior,'chain_checks':len(dress['chain_checks']),'maximum_chain_root_error':dress['max_root_error'],'maximum_chain_length_error':dress['max_length_error']}
(P/'wiiu-dress-preview-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report)
