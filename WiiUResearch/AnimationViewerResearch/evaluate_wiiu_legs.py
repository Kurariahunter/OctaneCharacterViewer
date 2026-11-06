"""Evaluate eight source-specific Wii U leg outputs; preserve independent FK checks."""
import json,hashlib,random,numpy as np
from wiiu_pc_graph_adapter import Adapter,P,refs
from wiiu_leg_adapter import SourceLegEval
from wiiu_clip_sampler import WiiUClip
from evaluate_pc_dress import DressEval
from pc_graph_controls import apply
from native_pc_transform_scale import point,compose
from native_pc_ik_endpoint import witness
from native_pc_head_connections import connect

def matrix(raw):
 origin=point(raw,[0,0,0]);m=np.eye(4);m[:3,3]=origin
 for col in range(3):
  axis=[0,0,0];axis[col]=1;m[:3,col]=point(raw,axis)-origin
 return m

rng=random.Random(20261024);offset_errors=[]
for _ in range(32):
 t=[rng.uniform(-2,2)for _ in range(3)];offset=[rng.uniform(-1,1)for _ in range(3)]
 from native_pc_clip_math import rotation
 value=rotation([rng.uniform(-2,2)for _ in range(3)])+t+[1.]
 result=connect(value,[0,0,0,1],[0,0,0,1,0,0,0,1],True,translate_offset=offset)
 expected=np.array(t,dtype=np.float32)+np.array(offset,dtype=np.float32)
 error=float(np.max(abs(np.array(result[4:7])-expected)));assert error<1e-6;offset_errors.append(error)
 zero=connect(value,[0,0,0,1],[0,0,0,1,0,0,0,1],True,translate_offset=[0,0,0])
 previous=connect(value,[0,0,0,1],[0,0,0,1,0,0,0,1],True)
 assert zero==previous

adapter=Adapter();audit=adapter.audit();clip=WiiUClip();frames=clip.frames();bindings=json.loads((P/'wiiu-skin-associations.json').read_text())
names={'Knee_Left','Knee_Right','Ankle_Left','Ankle_Right','Ball_Left','Ball_Right','Toes_Left','Toes_Right'}
selected=[b for b in bindings if b['bone']in names];assert len(selected)==8
samples=[];checks=[];blobs={}
for index,frame in enumerate(frames):
 e=DressEval();apply(e,adapter.controls(frame));source=SourceLegEval(adapter,audit,e);outputs=[]
 for binding in selected:
  node=refs(adapter.producers[binding['matrix_node']][0])['Input'];world=matrix(source.run(node));assert np.isfinite(world).all()and abs(np.linalg.det(world))>1e-8
  outputs.append({**binding,'source_node':node,'matrix':world.tolist()})
 root=source.run(62);root_transform=compose(root[:4],root[4:7],[root[7]]*3+[1],[1]*4)
 for side,node,pid in [('Left',435,413),('Right',469,407)]:
  actual=point(source.run(node),[0,0,0]);solver=source.solvers[pid]
  if solver['outputs'][2]==[1.0]:
   fk=witness(solver,np.eye(4));expected=point(root_transform,fk['local']);mode='independent original-native unit-stretch FK'
  else:expected=point(root_transform,solver['inputs'][3]);mode='source target under solver stretch'
  error=float(np.linalg.norm(actual-expected));assert error<1e-5,(index,side,error,mode)
  checks.append({'time':frame['time'],'side':side,'mode':mode,'error':error,'stretch':solver['outputs'][2][0]})
 samples.append({'time':frame['time'],'outputs':outputs})
 for node,blob in source.blobs.items():blobs[node]={'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()}
 if index%30==0:print('LEGS',index+1,'/',len(frames),flush=True)
report={'scope':'Eight differing Wii U source leg outputs using shared PC evaluator for equivalent dependencies and original PC numeric operators for source-specific routing. Explicit relationship cache fixtures; no Wii U CPU execution, live actor parity or dynamics claim.','samples':samples,'relationship_blobs':blobs,'checks':checks,'maximum_endpoint_check_error':max(r['error']for r in checks),'translation_offset_fixtures':32,'maximum_translation_offset_error':max(offset_errors)}
(P/'wiiu-source-leg-animation.json').write_text(json.dumps(report,separators=(',',':')),encoding='utf-8')
print('PASS',len(samples)*8,'source leg matrices;',len(checks),'endpoint checks; max',report['maximum_endpoint_check_error'])
