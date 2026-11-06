"""OCT influence/bind correspondence and preserved Unity mesh audit comparison."""
import hashlib,json
from pathlib import Path
import numpy as np
from pc_skin_palette import influences,get,skin,reflect,PROD,PC_RIG
root=Path(__file__).parent;viewer=root.parent/'OctaneCharacterViewer'
meshpath=viewer/'Data/elsa-pc-mesh.json';oldpath=root/'pc-original-skin-mesh-audit.json'
m=json.loads(meshpath.read_text());old=json.loads(oldpath.read_text())
source_names=[get(x,'Name')for x in influences.values()]
assert m['bones']==source_names==old['bones'] and len(source_names)==len(set(source_names))==62
assert set(skin)==set(source_names)
vertices=np.array(m['vertices']);oldvertices=np.array(old['vertices']).reshape(-1,3)
vertex_error=float(abs(vertices-oldvertices).max());assert vertex_error<1e-6
assert [i for p in m['parts']for i in p['triangles']]==old['triangles']
assert len(m['weights'])==len(old['weights'])==len(vertices)==5419
max_sum_error=0.;finger_vertices=set();rows=[];relative=[]
for v,(a,b)in enumerate(zip(m['weights'],old['weights'])):
 assert a['indices']==b['indices'] and a['weights']==b['values']
 assert all(0<=i<62 for i in a['indices'])and all(w>=0 for w in a['weights'])
 max_sum_error=max(max_sum_error,abs(sum(a['weights'])-1))
 if any(w>0 and any(s in m['bones'][i]for s in ('Thumb','Index','Middle'))for i,w in zip(a['indices'],a['weights'])):finger_vertices.add(v)
assert max_sum_error<1e-6
for j,name in enumerate(source_names):
 source=reflect@np.array(get(influences[j],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T@reflect
 exported=np.array(m['bindposes'][j]).reshape(4,4)
 prior=np.array(old['bindposes'][j]['values']).reshape(4,4)
 prior_error=float(abs(exported-prior).max());assert prior_error<1e-6
 common=np.linalg.inv(source)@exported;relative.append(common)
 p=PROD.get(skin[name]);rows.append({'name':name,'index':j,'world_data_node':skin[name],'world_producer_type':get(p[0],'Type')if p else None,
  'source_to_export_bind_max_error':float(abs(source-exported).max()),'preserved_audit_bind_max_error':prior_error})
common=relative[source_names.index('Body')]
residual=max(float(abs(x-common).max())for x in relative);assert residual<2e-6
report={'pass':True,'model_sha256':PC_RIG.sha,'mesh_sha256':hashlib.sha256(meshpath.read_bytes()).hexdigest(),'preserved_mesh_audit_sha256':hashlib.sha256(oldpath.read_bytes()).hexdigest(),
 'bones':62,'vertices':5419,'finger_influenced_vertices':len(finger_vertices),'max_vertex_error_vs_preserved_audit':vertex_error,'max_weight_sum_error':max_sum_error,
 'weights_and_indices_exactly_match_preserved_audit':True,'triangles_match':True,'source_bone_order_matches':True,'common_source_to_export_bind_transform':common.tolist(),'max_bind_residual_after_common_transform':residual,'bone_rows':rows,
 'scope':'OCT influence names/order/binds and associations checked directly. Vertices/weights/triangles checked against preserved Unity audit, not a fresh raw VBUF decode. Common bind offset is consistent with grounded importer; no pose correction applied. This does not prove final native game skin matrices or all exporter assumptions.'}
(viewer/'skin-correspondence-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k]for k in ('pass','bones','vertices','finger_influenced_vertices','max_weight_sum_error','max_bind_residual_after_common_transform')}))
