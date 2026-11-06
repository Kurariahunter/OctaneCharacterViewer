"""Channel-preservation checks for native buffer composition used by the viewer."""
import json
from pathlib import Path
from compose_native_clip_layers import compose

def record(node,channels):return dict(source_node=node,path=str(node),channels=channels)

base={1:record(1,{'0':[1.,2.,3.],'4':[0.,0.,0.,1.],'10':[7.]}),
      2:record(2,{'10':[9.]})}
overlay={1:record(1,{'1':[4.]})}
r=compose([(base,1.,1),(overlay,1.,1)])
assert r[1]['channels']=={'1':[4.],'2':[2.],'3':[3.],'4':[0.,0.,0.,1.],'10':[7.]}
assert r[2]['channels']['10']==[9.]
half=compose([(base,1.,1),({1:record(1,{'10':[11.]})},.5,1)])
assert half[1]['channels']['10']==[9.]
add=compose([(base,1.,1),({1:record(1,{'0':[2.,4.,6.]})},.5,0)])
assert [add[1]['channels'][str(i)][0]for i in (1,2,3)]==[2.,4.,6.]
# A lean-only rotor must compose against native identity, not a zero quaternion.
lean=compose([({1:record(1,{'4':[0.,0.,.6,.8]})},1.,0)])
assert max(abs(a-b)for a,b in zip(lean[1]['channels']['4'],[0.,0.,.6,.8]))<1e-6
half_lean=compose([({1:record(1,{'4':[0.,0.,.6,.8]})},.5,0)])
assert max(abs(a-b)for a,b in zip(half_lean[1]['channels']['4'],[0.,0.,.31622776601683794,.9486832980505138]))<1e-6
try:compose([(base,1.,1),({1:record(99,{'10':[0.]})},1.,1)])
except ValueError:pass
else:raise AssertionError('Inconsistent binding accepted')
report=dict(pass_=True,checks=['partial overlay preserves other channels','port isolation','weighted scalar replacement','weighted additive translation','lean-only quaternion starts at native identity','half-weight lean quaternion','binding mismatch rejected'])
(Path(__file__).parent/'ControllerState/native-composition-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
