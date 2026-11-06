"""Fresh raw PC VBUF skin weight decode, independent of preserved Unity export."""
import hashlib,json,struct
from pathlib import Path
import numpy as np
from pc_skin_palette import T,get,allnodes
ROOT=Path(__file__).resolve().parent
base=ROOT/'InstalledGameAssetCheck/FreshWeightAudit/fro_elsa';source=base/'fro_elsa_0.vbuf';raw=source.read_bytes()
model=json.loads((ROOT.parent/'OctaneCharacterViewer/Data/elsa-pc-mesh.json').read_text())
assert not list(allnodes(T,'InfluenceRemapInfluenceRefs')),'Unexpected remap; direct palette audit cannot apply'
rows=[];positions=[]
for p in allnodes(T,'Primitive'):
 v=get(p,'Vdata');assert v[0]==2 and v[5]==0 and v[7]==24
 for j in range(v[1]):
  x,y,z=struct.unpack_from('<3f',raw,v[3]+16*j);positions.append([-x,y,z])
 for i in range(v[1]):
  offset=v[6]+i*v[7];indices=list(raw[offset:offset+4]);values=list(raw[offset+4:offset+8]);assert len(values)==4 and sum(values)>0
  combined={}
  for idx,w in zip(indices,values):
   if w:
    assert idx<len(model['bones'])
    combined[idx]=float(np.float32(combined.get(idx,0.))+np.float32(w)/np.float32(sum(values)))
  pairs=sorted(combined.items(),key=lambda x:-x[1]);ids=[x[0]for x in pairs]+[0]*(4-len(pairs));weights=[x[1]for x in pairs]+[0.]*(4-len(pairs))
  rows.append(dict(indices=ids,weights=weights))
assert len(rows)==len(model['weights'])==5419
index_mismatches=sum(a['indices']!=b['indices']for a,b in zip(rows,model['weights']))
max_weight_error=max(max(abs(x-y)for x,y in zip(a['weights'],b['weights']))for a,b in zip(rows,model['weights']))
delta=np.array(model['vertices'])-np.array(positions);offset=np.median(delta,axis=0)
position_residual=float(np.max(abs(delta-offset)))
report=dict(source=str(source),sha256=hashlib.sha256(raw).hexdigest(),vertices=len(rows),index_mismatches=index_mismatches,max_weight_error=max_weight_error,
 common_vertex_offset=offset.tolist(),max_vertex_residual_after_offset=position_residual,
 pass_=index_mismatches==0 and max_weight_error<1e-7 and position_residual<1e-6,scope='Fresh PC Elsa VBUF decode: direct palette indices/weights and reflected vertex positions up to common grounding offset. No live GPU or game-renderer validation.')
(ROOT/'ControllerState/fresh-vbuf-weight-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
