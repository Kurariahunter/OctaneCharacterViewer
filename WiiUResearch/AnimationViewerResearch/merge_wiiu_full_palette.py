"""Replace the three final hair fallbacks without changing the established61outputs."""
import json,numpy as np
from wiiu_pc_graph_adapter import P
base=json.loads((P/'wiiu-source-mesh-animation-dress.json').read_text());hair=json.loads((P/'wiiu-source-hair-animation.json').read_text());R=np.diag([-1,1,1,1]);nodes=dict(base['source_skin_nodes']);samples=[];max_prior=0.
assert len(nodes)==61 and len(hair['samples'])==153
for previous,frame in zip(base['clips'][0]['samples'],hair['samples']):
 assert abs(previous['time']-frame['time'])<1e-10;poses={p['bone']:p['matrix']for p in previous['transforms']}
 for output in frame['outputs']:
  name=output['bone'];assert name not in base['source_skin_nodes'];poses[name]=(R@np.array(output['matrix'])@R).flatten().tolist();nodes[name]=output['source_node']
 for p in previous['transforms']:
  if p['bone']in base['source_skin_nodes']:max_prior=max(max_prior,float(np.max(abs(np.array(poses[p['bone']])-p['matrix']))))
 assert set(poses)==set(nodes)and len(poses)==64 and all(np.isfinite(m).all()for m in poses.values())
 samples.append({'time':previous['time'],'transforms':[{'bone':p['bone'],'matrix':poses[p['bone']]}for p in previous['transforms']]})
assert max_prior==0 and len(nodes)==64
base.update(source_skin_nodes=nodes,reference_source_outputs=64,fallback_parents={},scope='Actual Wii U Elsa mesh with64source-evaluated outputs for the supported specific idle clip. Shared PC numerical routines and source-specific leg/hair/dress routing, explicit gravity/warmup and activation fixtures. Complete palette is not complete engine/game parity.')
base['fixture_assumptions']=['Hair and dress chains use source-matched parameters and PC native dynamics with120tick phase-zero warmup,60Hzschedule and explicit gravity.','Scene capsules/collision and complete actor scheduling remain unreconstructed.','This supported specific idle and its source mesh are validated fixtures, not a universal Wii U clip loader.','Existing matching PC material PNGs remain preview texture references.']
base['clips'][0].update(name='WiiU_Elsa_SourceMesh_FullPalette_64_of_64',samples=samples)
(P/'wiiu-source-mesh-animation-full.json').write_text(json.dumps(base,separators=(',',':')),encoding='utf-8')
report={'pass':True,'source_outputs':64,'fallback_outputs':0,'samples':153,'maximum_prior_61_matrix_change':max_prior,'hair_chain_checks':len(hair['chain_checks']),'max_hair_root_error':hair['max_root_error'],'max_hair_length_error':hair['max_length_error'],'scope':'Full palette for supported source idle; explicit physics/activation fixtures, not complete game parity.'}
(P/'wiiu-full-palette-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report)
