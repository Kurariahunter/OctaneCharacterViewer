"""Source-associated Body/spine/Hips matrices for partial preview continuity."""
import json,numpy as np
import evaluate_wiiu_head_fixture as h
names={'Body','Spine1','Spine2','Spine3','Hips'}
bindings=json.loads((h.P/'wiiu-skin-associations.json').read_text());samples=[]
influences={h.get(n,'Name'):n for n in h.walk(h.r)if n['name']=='Influence'and h.get(n,'Name')in names}
for frame in h.frames:
 e=h.Eval(frame);outputs=[]
 for b in [b for b in bindings if b['bone']in names]:
  proc,_=h.producers[b['matrix_node']];assert h.get(proc,'Type')=='TransformToMatrix4x4VariantProcessor'
  source=h.refs(proc)['Input'];world=np.array(h.matrix_from_transform(e.run(source)))
  inverse_bind=np.array(h.get(influences[b['bone']],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T
  assert np.isfinite(world).all()and abs(np.linalg.det(world))>1e-8
  outputs.append({**b,'world_source_node':source,'skin_matrix_column_convention':(world@inverse_bind).tolist()})
 assert len(outputs)==5;samples.append({'time':frame['time'],'outputs':outputs,'stored_default_leaves':e.defaults,'evaluated_processors':e.operations})
(h.P/'wiiu-axial-world-fixture.json').write_text(json.dumps({'scope':'Five axial source-associated outputs; PC numerical replay with explicit defaults, not full Wii U actor execution.','samples':samples},indent=2))
print('PASS 15 finite source-associated axial matrices')
