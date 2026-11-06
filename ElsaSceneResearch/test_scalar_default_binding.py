"""Native default-network residual blending, with observed indexed layout."""
import json,struct
from pathlib import Path
from native_pc_blend_replay import blend,sha
def f(v):return struct.unpack('<f',struct.pack('<f',v))[0]
rows=[]
for default in [0.,2.,-4.]:
 for weight in [0.,.25,.5,.75,1.]:
  c=dict(values=[10.]+[0.]*15,priority=5.,flag=0,weight=weight,factor2c=None,factor30=1.)
  observed=blend([c],scalar=True,bypass_fade=False,default_scalar=default)[0]
  expected=f(f(default*f(1-weight))+f(10*weight))
  assert observed==expected,(default,weight,observed,expected)
  rows.append(dict(default=default,source_weight=weight,output=observed))
r=dict(passed=True,exe_sha256=sha,cases=rows,scope='Original Float blender with synthetic default-network pointers; index-map entry16 selects scalar16, as observed live for slots33..44. Unit temporal factor, unflagged single source. Does not establish the binding writer or actor reset semantics.')
(Path(__file__).parent/'ControllerState/scalar-default-binding-native-validation.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows))))
