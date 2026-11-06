"""Native Dilation prior-output path: endpoints, translation/scale, quaternion hemisphere."""
import math,json
from pathlib import Path
from native_dilation_state import DilationStates
from native_pc_blend_replay import sha
old=[0.,0.,0.,1.,2.,-3.,4.,1.];rows=[]
for sign in (1.,-1.):
 target=[0.,0.,sign*math.sin(math.pi/4),sign*math.cos(math.pi/4),10.,5.,-4.,2.]
 for factor in (0.,.25,.5,.75,1.):
  bank=DilationStates();bank.seed('control',old);value=bank.update('control',target,factor)
  expected=[(1-factor)*a+factor*b*sign for a,b in zip(old[:4],target[:4])];norm=math.sqrt(sum(x*x for x in expected));expected=[x/norm for x in expected]
  qerror=min(max(abs(a-b)for a,b in zip(value[:4],expected)),max(abs(a+b)for a,b in zip(value[:4],expected)))
  linear=max(abs(value[i]-(old[i]+(target[i]-old[i])*factor))for i in range(4,8))
  assert qerror<2e-5 and linear<2e-6,(factor,value,expected)
  rows.append(dict(sign=sign,factor=factor,quaternion_error=qerror,linear_error=linear))
bank=DilationStates();bank.seed('sequence',old);target=[0.,0.,0.,1.,10.,5.,-4.,1.]
a=bank.update('sequence',target,.25);b=bank.update('sequence',target,.5)
assert a[4]==4. and b[4]==7. # Direct prior-output mix, NOT Float's incremental fade.
bank.seed('bypass',old,True);assert bank.update('bypass',target,.25)==target
assert bank.states['bypass']['bypass']
out=dict(passed=True,exe_sha256=sha,cases=rows,retained_translation=[a[4],b[4]],bypass_preserved=True,scope='Full original4E35D0, one unflagged contributor, synthetic cached nodes and no default network/filter. Native quaternion normalization/hemisphere and translation/uniform scale tested. No live Dilation transition parity or automatic binding claim.')
(Path(__file__).parent/'ControllerState/dilation-temporal-native-validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows),retained_translation=[a[4],b[4]])))
