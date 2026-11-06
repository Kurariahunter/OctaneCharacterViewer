"""Overlay verified source-specific legs on the unchanged upper-body reference bake."""
import json,numpy as np
from wiiu_pc_graph_adapter import Adapter,P
from pc_skin_palette import worlds,parents
source=json.loads((P/'wiiu-controls-pc-reference-viewer-continuous.json').read_text());legs=json.loads((P/'wiiu-source-leg-animation.json').read_text());adapter=Adapter()
assert len(source['clips'][0]['samples'])==len(legs['samples'])==153
reflect=np.diag([-1,1,1,1]);parent_map=dict(parents,hair01='hairStart',hair02='hair01')
bindlocals={name:np.linalg.inv(worlds[parent_map[name]])@m if parent_map[name]else m for name,m in worlds.items()}
new_nodes=dict(source['source_skin_nodes']);samples=[];maximum_upper_difference=0.
for original,leg in zip(source['clips'][0]['samples'],legs['samples']):
 assert original['time']==leg['time'];prior={p['bone']:np.array(p['matrix']).reshape(4,4)for p in original['transforms']}
 out={name:prior[name]for name in source['source_skin_nodes']}
 for row in leg['outputs']:
  name=row['bone']
  if name not in worlds:assert name in ('Ankle_Left','Ankle_Right');continue
  assert name not in out;out[name]=reflect@np.array(row['matrix'])@reflect;new_nodes[name]=adapter.mapping[row['source_node']]
 assert len(out)==55
 def world(name):
  if name in out:return out[name]
  parent=parent_map[name];out[name]=(world(parent)if parent else np.eye(4))@(reflect@bindlocals[name]@reflect);return out[name]
 poses=[]
 for name in worlds:
  m=world(name);assert np.isfinite(m).all();poses.append({'bone':name,'matrix':m.flatten().tolist()})
  if name in source['source_skin_nodes']:maximum_upper_difference=max(maximum_upper_difference,float(np.max(abs(m-prior[name]))))
 samples.append({'time':original['time'],'transforms':poses})
assert maximum_upper_difference==0
source.update(source_skin_nodes=new_nodes,fallback_parents={name:parent_map[name]for name in worlds if name not in new_nodes},reference_source_outputs=57,scope='Wii U source controls and differing source leg graph on PC62-bone reference mesh:55evaluated/7bind-relative fallback. Two additional Wii U ankle outputs evaluated separately; no full Wii U mesh or actor parity claim.')
source['clips'][0].update(name='WiiU_Elsa_Shared_Upper_Source_Legs_55_of_62',samples=samples)
(P/'wiiu-controls-pc-reference-viewer-legs.json').write_text(json.dumps(source,separators=(',',':')),encoding='utf-8')
(P/'leg-preview-merge-validation.json').write_text(json.dumps({'pass':True,'samples':153,'reference_evaluated':55,'reference_fallbacks':7,'wiiu_outputs_evaluated':57,'wiiu_outputs_total':64,'maximum_existing_49_output_change':maximum_upper_difference},indent=2),encoding='utf-8')
print('PASS 55/62 reference outputs, 57/64 Wii U source outputs; all previous49outputs unchanged')
