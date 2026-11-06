"""Measure source dress deformation without changing mesh or animation."""
import json,collections,itertools,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
root=P.parents[1]
m=json.loads((root/'OctaneCharacterViewer/Data/elsa-wiiu-mesh.json').read_text())
cache_name=sys.argv[1]if len(sys.argv)>1 else 'wiiu-source-mesh-animation-full.json'
c=json.loads((P/cache_name).read_text())
v=np.array(m['vertices']);h=np.c_[v,np.ones(len(v))];bind=np.array(m['bindposes']).reshape(-1,4,4)
ids=np.array([r['indices']for r in m['weights']]);weights=np.array([r['weights']for r in m['weights']]);names=m['bones']
dress=[i for i,n in enumerate(names)if 'dress' in n.lower()]
dw=np.sum(weights*np.isin(ids,dress),axis=1)
tri=np.array(m['parts'][2]['triangles']).reshape(-1,3)
sel=np.max(dw[tri],axis=1)>.05;tri=tri[sel]
edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
rest=np.linalg.norm(v[edges[:,0]]-v[edges[:,1]],axis=1);edges=edges[rest>1e-6];rest=rest[rest>1e-6]
groups=collections.defaultdict(list)
for i in set(tri.flatten()):groups[tuple(np.round(v[i],6))].append(int(i))
pairs=np.array([p for g in groups.values()for p in itertools.combinations(g,2)],dtype=int)
maxsplit=0.;worst={'ratio':0};samples=[]
for s in c['clips'][0]['samples']:
 pose={r['bone']:np.array(r['matrix']).reshape(4,4)for r in s['transforms']};skin=np.array([pose[n]for n in names])@bind
 x=np.sum(np.einsum('nkij,nj->nki',skin[ids],h)*weights[:,:,None],axis=1)[:,:3]
 ratio=np.linalg.norm(x[edges[:,0]]-x[edges[:,1]],axis=1)/rest
 k=int(np.argmax(ratio))
 if ratio[k]>worst['ratio']:
  e=edges[k];worst={'ratio':float(ratio[k]),'time':s['time'],'vertices':e.tolist(),'bind_length':float(rest[k]),'bind_positions':v[e].tolist(),'weights':[[{'bone':names[j],'weight':float(w)}for j,w in zip(ids[i],weights[i])if w>0]for i in e]}
 if len(pairs):maxsplit=max(maxsplit,float(np.max(np.linalg.norm(x[pairs[:,0]]-x[pairs[:,1]],axis=1))))
 samples.append({'time':s['time'],'maximum_edge_stretch':float(max(ratio)),'minimum_edge_ratio':float(min(ratio))})
r={'cache':cache_name,'scope':'Dress-weighted body triangles only. Edge stretching and split checks do not detect all self-intersections. No model or pose modified.','dress_bones':[names[i]for i in dress],'triangles':len(tri),'edges':len(edges),'coincident_pairs':len(pairs),'maximum_coincident_separation':maxsplit,'worst_edge':worst,'samples':samples}
(P/('dress-deformation-audit-fallback.json'if len(sys.argv)>1 else 'dress-deformation-audit.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({k:z for k,z in r.items()if k!='samples'},indent=2))
