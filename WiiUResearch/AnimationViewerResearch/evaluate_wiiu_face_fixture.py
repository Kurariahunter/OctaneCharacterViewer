"""Eight face influences evaluated from source graph with original PC operators."""
import json,numpy as np
import evaluate_wiiu_head_fixture as h
names={'BrowLeft','BrowCenter','BrowRight','Jaw','CornerLipLeft','CornerLipRight','LowerLip','UpperLip','Neck'}
bindings=json.loads((h.P/'wiiu-skin-associations.json').read_text());samples=[]
influences={}
for n in h.walk(h.r):
 if n['name']=='Influence'and h.get(n,'Name')in names:
  name=h.get(n,'Name');assert name not in influences;influences[name]=n
for frame in h.frames:
 e=h.Eval(frame);outputs=[]
 for b in [b for b in bindings if b['bone']in names]:
  proc,_=h.producers[b['matrix_node']];assert h.get(proc,'Type')=='TransformToMatrix4x4VariantProcessor'
  source=h.refs(proc)['Input'];raw=e.run(source);assert len(raw)==16
  world=np.array(h.matrix_from_transform(raw));inverse_bind=np.array(h.get(influences[b['bone']],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T
  assert np.isfinite(world).all()and abs(np.linalg.det(world))>1e-8
  skin=world@inverse_bind
  outputs.append({**b,'world_source_node':source,'world_matrix_column_convention':world.tolist(),'skin_matrix_column_convention':skin.tolist()})
 assert len(outputs)==9
 samples.append({'time':frame['time'],'outputs':outputs,'stored_default_leaves':e.defaults,'evaluated_processors':e.operations})
report={'scope':'Eight source-bound facial outputs plus Neck; original PC numerical helpers, three approximate clip-control snapshots and explicit source-default leaves. Transform matrices recovered with original PC point transforms. Not Wii U execution or actor scheduling parity.','samples':samples}
(h.P/'wiiu-face-world-fixture.json').write_text(json.dumps(report,indent=2));print('PASS 27 finite source-bound face/neck world/skin matrices')
