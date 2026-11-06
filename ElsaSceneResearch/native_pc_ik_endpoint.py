"""Independent forward endpoint from the original solver's unit-scale outputs."""
import numpy as np
from native_pc_transform_scale import compose,concat,point
def witness(solver,root):
 inputs=solver['inputs'];q1,q2,scale=solver['outputs']
 if scale!=[1.0]:raise ValueError('Native endpoint witness requires unit solver stretch')
 root=np.asarray(root,dtype=float)
 if root.shape!=(4,4) or not np.isfinite(root).all() or np.max(abs(root[3]-[0,0,0,1]))>1e-8 or abs(np.linalg.det(root[:3,:3])-1)>2e-5 or np.max(abs(root[:3,:3].T@root[:3,:3]-np.eye(3)))>2e-5:raise ValueError('Native endpoint witness requires rigid root')
 # Original native TRS composition and point helpers, independent of the
 # evaluated skin-output graph. Solver vectors are local link translations.
 start=compose(q1,inputs[0],[1.]*4,[1.]*4)
 mid=compose(q2,inputs[1],[1.]*4,[1.]*4)
 endpoint=point(concat(mid,start),inputs[2])
 world=(root@np.r_[endpoint,1.])[:3]
 target=(root@np.r_[inputs[3],1.])[:3]
 return dict(world=world,local=endpoint,target=target,native_target_residual=float(np.linalg.norm(world-target)))
