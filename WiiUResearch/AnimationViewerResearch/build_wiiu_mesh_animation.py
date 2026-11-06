"""Package actual Wii U mesh/weights and57 source outputs for the existing renderer."""
import json,hashlib,numpy as np
from wiiu_pc_graph_adapter import Adapter,P,get,walk
from pc_skin_palette import parents
adapter=Adapter();raw=json.loads((P/'EyelidDiagnostic/Extracted/mesh.json').read_text());shared=json.loads((P/'wiiu-controls-pc-reference-viewer-continuous.json').read_text());legs=json.loads((P/'wiiu-source-leg-animation.json').read_text());coverage=json.loads((P/'pc-evaluator-wiiu-adapter-check-continuous.json').read_text())
graph_sha=hashlib.sha256((P/'WiiUClips/fro_elsa.oct').read_bytes()).hexdigest();assert graph_sha=='fdf7c0e753e8ae34a5f68cd9322c5b711e8b8fd3a161da3d08dbb682857dea92'
reflect=np.diag([-1,1,1,1]);influences={get(n,'Name'):n for n in walk(adapter.tree)if n['name']=='Influence'}
worlds={name:np.linalg.inv(np.array(get(influences[name],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T)for name in raw['bones']}
assert len(worlds)==64
parent_map=dict(parents,hair01='hairStart',hair02='hair01');source_nodes={r['bone']:r['source_node']for r in coverage['outputs']if r['status']=='evaluated with existing PC evaluator'}
for row in legs['samples'][0]['outputs']:source_nodes[row['bone']]=row['source_node']
assert len(source_nodes)==57
fallback={name:parent_map[name]for name in worlds if name not in source_nodes};assert len(fallback)==7
bindlocals={name:np.linalg.inv(worlds[parent])@worlds[name]if parent else worlds[name]for name,parent in fallback.items()}
samples=[];maximum_upper_change=0.
for original,leg in zip(shared['clips'][0]['samples'],legs['samples']):
 assert original['time']==leg['time'];out={p['bone']:reflect@np.array(p['matrix']).reshape(4,4)@reflect for p in original['transforms']if p['bone']in shared['source_skin_nodes']}
 for row in leg['outputs']:assert row['bone']not in out;out[row['bone']]=np.array(row['matrix'])
 def world(name):
  if name not in out:
   parent=fallback[name];out[name]=(world(parent)if parent else np.eye(4))@bindlocals[name]
  return out[name]
 poses=[]
 for name in raw['bones']:
  m=world(name);assert np.isfinite(m).all();poses.append({'bone':name,'matrix':(reflect@m@reflect).flatten().tolist()})
 samples.append({'time':original['time'],'transforms':poses})
pc_mesh=json.loads((P.parents[1]/'OctaneCharacterViewer/Data/elsa-pc-mesh.json').read_text())
expected_materials=['characters__fro_elsa__materials__fro_elsa_'+name+'__skinning_isEnabled_true'for name in ('pupil','head','body')]
assert raw['materials']==expected_materials and len(raw['triangles'])==3
# Reuse existing preview PNGs only after source material-name order is checked.
model={'source':'Wii U Elsa source mesh,64skin influences and native remapped weights; matching PC preview material PNGs reused by checked pupil/head/body names.','vertices':raw['positions'],'uv':raw['uv'],'bones':raw['bones'],'bindposes':[(reflect@np.linalg.inv(worlds[name])@reflect).flatten().tolist()for name in raw['bones']],'weights':[{'indices':i,'weights':w}for i,w in zip(raw['indices'],raw['weights'])],'parts':[{'triangles':t,'texture':part['texture']}for t,part in zip(raw['triangles'],pc_mesh['parts'])]}
target=P.parents[1]/'OctaneCharacterViewer/Data/elsa-wiiu-mesh.json';target.write_text(json.dumps(model,separators=(',',':')),encoding='utf-8')
cache={'reference_rig_adapter':True,'model_sha256':graph_sha,'reference_source_outputs':57,'scope':'Actual Wii U64-bone Elsa mesh with57source-evaluated outputs and7explicit bind-relative hair/dress fallbacks. Original-PC numerical routines reused; not full game parity. Matching PC preview PNGs reused.','source_skin_nodes':source_nodes,'fallback_parents':fallback,'fixture_assumptions':['Three hair and four dress outputs remain bind-relative fallback fixtures; their parent fixtures are inherited from the PC reference hierarchy.','Independent-frame source clip evaluation, no reconstructed actor scheduling or dynamics.'],'clips':[{'name':'WiiU_Elsa_SourceMesh_SourceLegs_57_of_64','duration':samples[-1]['time'],'samples':samples}]}
(P/'wiiu-source-mesh-animation.json').write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
validation={'pass':True,'source_model_sha256':graph_sha,'vertices':len(model['vertices']),'bones':len(worlds),'source_outputs':57,'fallback_outputs':7,'samples':len(samples),'material_pngs':'Existing PC preview PNGs, matching names/order checked; not Wii U texture decoding.'}
(P/'wiiu-source-mesh-validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8');print(validation)
