"""Audit source eyelid output associations and column-convention skin matrices.
Algebraic binding checks only: not execution of Wii U matrix conversion code.
"""
from pathlib import Path
import json
import numpy as np
P=Path(__file__).parent
def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
def get(n,k,default=None):return next((c['value']for c in n['children']if c['name']==k),default)
def refs(n):return dict(zip(get(n,'DataNodeAttributes',[]),get(n,'DataNodeRefs',[])))
tree=json.loads((P/'WiiUClips/fro_elsa.tree.json').read_text())
net=next(n for n in walk(tree)if n['name']=='SubNetwork')
procs=[n for n in walk(net)if n['name']=='ProcessorNode']
scene={int(n['value']):n for pool in walk(tree)if pool['name']=='SceneTreeNodePool'for n in pool['children']if n['name']=='Node'}
bindings=json.loads((P/'wiiu-skin-associations.json').read_text())
fixture=json.loads((P/'wiiu-head-eyelid-world-fixture.json').read_text());results=[]
for sample in fixture['samples']:
 for eye in sample['eyelids']:
  matches=[b for b in bindings if b['matrix_node']==eye['associated_matrix_node']]
  assert len(matches)==1;b=matches[0]
  assert b['bone']==eye['bone']and b['influence']==eye['skin_influence']
  producers=[p for p in procs if refs(p).get('Output')==b['matrix_node']]
  assert len(producers)==1 and get(producers[0],'Type')=='DilationToMatrix4x4VariantProcessor'
  assert refs(producers[0])['Input']==eye['world_source_node']
  influences=next(c for c in scene[b['scene_node']]['children']if c['name']=='Influences')['children']
  influence=next(n for n in influences if int(n['value'])==b['influence'])
  assert get(influence,'Name')==b['bone']
  inverse_bind=np.array(get(influence,'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T
  assert np.isfinite(inverse_bind).all()and abs(np.linalg.det(inverse_bind))>1e-8
  bind=np.linalg.inv(inverse_bind);world=np.array(eye['world_matrix_column_convention'])
  skin=world@inverse_bind
  identity_error=float(np.max(abs(bind@inverse_bind-np.eye(4))))
  # Independently test points expressed in bone-local and mesh bind coordinates.
  points=np.array([[0,0,0,1],[1,0,0,1],[0,1,0,1],[0,0,1,1],[.13,-.24,.37,1]]).T
  point_error=float(np.max(abs(skin@(bind@points)-world@points)))
  assert identity_error<1e-10 and point_error<1e-10
  results.append({'time':sample['time'],**b,'matrix_processor':int(producers[0]['value']),'inverse_bind_column_convention':inverse_bind.tolist(),'skin_matrix_column_convention':skin.tolist(),'bind_identity_error':identity_error,'point_roundtrip_error':point_error})
report={'scope':'Source association/producer audit and binding algebra under existing column-matrix convention. Derived skin matrices use evaluated bounded world fixture. Not native Wii U Matrix4x4 conversion execution, weighted vertex deformation, renderer parity or complete palette.','checks':len(results),'maximum_point_roundtrip_error':max(r['point_roundtrip_error']for r in results),'results':results}
(P/'eyelid-skin-binding-check.json').write_text(json.dumps(report,indent=2))
print('PASS',len(results),'source-bound eyelid matrices; max point roundtrip error',report['maximum_point_roundtrip_error'])
