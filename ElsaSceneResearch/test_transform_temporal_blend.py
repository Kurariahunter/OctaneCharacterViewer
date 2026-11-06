"""Original Transform blender: rotation, translation, nonuniform Scale and Unscale."""
import json,math
from pathlib import Path
from native_transform_state import TransformStates
from native_pc_blend_replay import sha
old=[0.,0.,0.,1.,2.,-3.,4.,1.]+[1.]*8;rows=[]
for sign in (1.,-1.):
 target=[0.,0.,sign*math.sin(math.pi/4),sign*math.cos(math.pi/4),10.,5.,-4.,1.,2.,3.,4.,1.,.5,.25,.125,1.]
 for previous,current in ((0.,0.),(0.,.25),(.25,.5),(.5,.75),(.75,.5),(0.,1.)):
  bank=TransformStates();bank.seed('control',old,previous);value=bank.update('control',target,current)
  inc=current if previous>current else (current-previous)/(1-previous)
  expected=[(1-inc)*a+inc*b*sign for a,b in zip(old[:4],target[:4])];norm=math.sqrt(sum(v*v for v in expected));expected=[v/norm for v in expected]
  qerr=min(max(abs(a-b)for a,b in zip(value[:4],expected)),max(abs(a+b)for a,b in zip(value[:4],expected)))
  linear=max(abs(value[i]-(old[i]+(target[i]-old[i])*inc))for i in range(4,16))
  assert qerr<2e-5 and linear<2e-6,(previous,current,value)
  assert abs(bank.states['control']['factor']-current)<1e-7
  rows.append(dict(previous=previous,current=current,rotation_error=qerr,linear_error=linear))
bank=TransformStates();target=[0.,0.,0.,1.,10.,5.,-4.,1.]+[1.]*8;bank.seed('sequence',old)
a=bank.update('sequence',target,.25);b=bank.update('sequence',target,.5)
assert a[4]==4. and abs(b[4]-6.)<1e-6
bank.seed('bypass',old,bypass=True);assert bank.update('bypass',target,.25)==target
result=dict(passed=True,exe_sha256=sha,routine='0x4E3FC0',vtable='0x1B2BA3C',rtti='Blender<TypedDataNode<Types::Transform3d>>',cases=rows,retained_translation=[a[4],b[4]],scope='Original full native Transform blender and525450 helper with one unflagged cached contributor, explicit output/fade/bypass seed and no default network/filter. Synthetic math tests, not live transition binding or missing-channel policy.')
(Path(__file__).parent/'ControllerState/transform-temporal-native-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows),retained_translation=[a[4],b[4]])))
