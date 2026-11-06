"""Native selector versus explicit f32 interval reference; no live selection claim."""
import json,struct
from pathlib import Path
from native_pc_keyblend_selector import select
f=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
cases=[]
for keys in ([.25,.5],[0,.12,.25,.38,.5,.63,.75,.88,1]):
    keys=list(map(f,keys))
    for value in [-1]+[i/100 for i in range(101)]+[2]+keys:
        value=f(value);expected=None
        for i in range(len(keys)-1):
            alpha=f(f(value-keys[i])/f(keys[i+1]-keys[i]))
            if alpha<=0:expected=dict(left=i,right=i,alpha=0.);break
            if alpha<=1:expected=dict(left=i,right=i+1,alpha=alpha);break
        if expected is None:expected=dict(left=len(keys)-1,right=len(keys)-1,alpha=0.)
        actual=select(value,keys,len(keys));assert actual==expected,(value,actual,expected)
        cases.append(dict(value=value,keys=keys,result=actual))
for count in (2,9):
    for value in (0,.125,.25,.5,.75,1):
        actual=select(value,[],count);scaled=(count-1)*f(value);left=int(scaled);right=min(left+1,count-1)
        assert actual==dict(left=left,right=right,alpha=f(scaled-left)if left!=right else 0.)
        cases.append(dict(value=value,uniform_children=count,result=actual))
report=dict(cases=len(cases),pass_=True,scope='Native selector with null expression and debug override disabled; explicit file Speed/Direction key arrays plus bounded uniform cases. Effective runtime parameter not yet captured.',examples=cases[:3])
(Path(__file__).parent/'ControllerState/keyblend-selector-native-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
