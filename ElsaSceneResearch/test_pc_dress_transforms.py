"""Convention checks for two newly traced native typed transform routines."""
from native_pc_dress_math import call
from native_pc_transform_scale import compose
from evaluate_pc_arms import quat
import numpy as np,random,json
from pathlib import Path
rng=random.Random(20261017);errors=[]
for j in range(50):
 states=[]
 for k in range(2):
  q=np.array([rng.uniform(-1,1)for _ in range(4)]);q/=np.linalg.norm(q);t=[rng.uniform(-1,1)for _ in range(3)];raw=compose(q,t,[1]*4,[1]*4);m=np.eye(4);m[:3,:3]=quat(q);m[:3,3]=t;states.append((raw,m))
 a,A=states[0];b,B=states[1]
 for fn,converter in [(0x4d7e90,b[:8]),(0x4d82c0,b)]:
  raw=call(fn,[a,converter],'typed',16);m=np.eye(4);m[:3,:3]=quat(raw[:4]);m[:3,3]=raw[4:7];error=float(np.max(abs(m-B@A)));assert error<2e-6,(hex(fn),error);errors.append(error)
Path(__file__).with_name('pc-dress-typed-transform-validation.json').write_text(json.dumps({'unit_scale_cases':len(errors),'max_error':max(errors),'routines':['0x4d7e90','0x4d82c0'],'scope':'Random rigid-transform convention check; nonuniform payloads are propagated by original native routines, not this analytic unit-scale reference.'},indent=2));print(len(errors),max(errors))
