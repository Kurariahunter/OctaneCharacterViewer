"""Original PC mesh LBS diagnostics; counterfactuals are not proposed fixes."""
import json,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).parent
m=json.loads((R/'pc-original-skin-mesh-audit.json').read_text())
v=np.array(m['vertices']).reshape(-1,3);tri=np.array(m['triangles']).reshape(-1,3)
names=m['bones'];weights=np.array([w['values']for w in m['weights']]);indices=np.array([w['indices']for w in m['weights']])
inverse_bind=np.array([x['values']for x in m['bindposes']]).reshape(-1,4,4);bind=np.linalg.inv(inverse_bind)
dress=[names.index(n)for n in ('UpperDress_Left','UpperDress_Right','dressLeftStart','dressRightStart')]
assert len(v)==5419 and len(names)==62 and np.max(abs(weights.sum(axis=1)-1))<2e-6
mask=(weights*np.isin(indices,dress)).sum(axis=1)>.5
p=np.c_[v,np.ones(len(v))]
def skin(world):
 matrices=world@inverse_bind
 return sum(weights[:,k,None]*np.einsum('nij,nj->ni',matrices[indices[:,k]],p)[:,:3]for k in range(4))
edges={}
for ti,t in enumerate(tri):
 if not mask[t].all():continue
 for x,y in zip(t,np.roll(t,-1)):edges.setdefault(tuple(sorted((int(x),int(y)))),[]).append(ti)
adj=[(edge,t[0],t[1])for edge,t in edges.items()if len(t)==2]
ta=np.array([a for _,a,b in adj]);tb=np.array([b for _,a,b in adj])
def normals(x):
 n=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]])
 length=np.linalg.norm(n,axis=1);return n/np.maximum(length[:,None],1e-20),length
rest=skin(bind);rn,area=normals(rest)
valid=(area[ta]>1e-10)&(area[tb]>1e-10)
ta=ta[valid];tb=tb[valid];adj=[a for a,ok in zip(adj,valid)if ok]
rest_angles=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',rn[ta],rn[tb]),-1,1)))
def severity(x):
 n,a=normals(x);angles=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',n[ta],n[tb]),-1,1)))
 return np.maximum(0,angles-rest_angles)
old=json.loads((R/'pc-upper-walk-animation.json').read_text())['clips'][0]
new=json.loads((R/'pc-feedback-walk-animation.json').read_text())['clips'][0]
rows=[];max_change=0;worst=None
for s,t in zip(old['samples'],new['samples']):
 assert s['time']==t['time']
 def worlds(sample):
  d={p['bone']:p['matrix']for p in sample['transforms']};return np.array([d[n]for n in names]).reshape(-1,4,4)
 a=worlds(s);b=worlds(t);va=skin(a);vb=skin(b)
 change=float(np.max(np.linalg.norm(va-vb,axis=1)));max_change=max(max_change,change)
 current=severity(vb)
 # Diagnostic substitution only: remove lower-chain flex, preserve upper-dress
 # motion and original bind-relative placement. This is not native reset.
 no_lower=b.copy()
 for side in ('Left','Right'):
  upper=names.index('UpperDress_'+side);lower=names.index('dress'+side+'Start')
  no_lower[lower]=b[upper]@inverse_bind[upper]@bind[lower]
 upper_driven=severity(skin(no_lower))
 # A second diagnostic keeps all dress bones rigid relative to Body. It will
 # permit leg penetration and must never be delivered as corrected animation.
 rigid=b.copy();body=names.index('Body')
 for i in dress:rigid[i]=b[body]@inverse_bind[body]@bind[i]
 rigid_severity=severity(skin(rigid))
 row=dict(time=t['time'],max_fold_change_degrees=float(current.max()),
  no_lower_flex_max_fold_degrees=float(upper_driven.max()),body_rigid_max_fold_degrees=float(rigid_severity.max()),
  aim_fix_max_vertex_displacement=change)
 rows.append(row)
 if worst is None or row['max_fold_change_degrees']>worst['max_fold_change_degrees']:
  edge_index=int(np.argmax(current));edge=adj[edge_index][0]
  worst=dict(**row,edge=list(edge),triangles=[int(ta[edge_index]),int(tb[edge_index])],
   vertices=[dict(vertex=i,posed=vb[i].tolist(),weights=[dict(bone=names[j],weight=float(w))for j,w in zip(indices[i],weights[i])if w>0])for i in edge])
report=dict(mesh_vertices=len(v),triangles=len(tri),bones=len(names),dress_vertices=int(mask.sum()),dress_adjacent_edges=len(adj),
 mesh_data_sha256=hashlib.sha256((R/'pc-original-skin-mesh-audit.json').read_bytes()).hexdigest(),
 max_aim_fix_vertex_displacement=max_change,worst_observed_edge=worst,rows=rows,
 scope='Original PC mesh/inverse binds/weights with exported palettes. Fold metric is increase in angle between adjacent dress-dominant faces relative to bind geometry; it is a diagnostic, not a complete self-intersection/collision test. Counterfactual palettes are deliberately nonphysical causal isolations, not native behavior or proposed fixes. No source mesh or weights modified.')
(R/'pc-walk-dress-fold-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items()if k!='rows'},indent=2))
