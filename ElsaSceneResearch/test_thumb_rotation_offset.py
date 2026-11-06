"""Thumb graph offsets against original native connection execution, not live proof."""
import json,math
from pathlib import Path
import numpy as np
from evaluate_pc_legs import LegEval
from pc_skin_palette import DN,get
from native_pc_head_connections import connect
from native_pc_transform_scale import compose

checks=[]
for input_node,output_node,offset_node in [(332,222,3),(337,228,2)]:
    for angle in (0.,.35,-.8):
        value=[math.sin(angle/2),0.,0.,math.cos(angle/2),.01,.02,.03,1.]
        e=LegEval();e.raw.cache[input_node]=value
        actual=e.raw.run(output_node)
        offset=get(DN[offset_node],'Data')
        initial=compose(value[:4],value[4:7],[1]*4,[1]*4)
        expected=connect(value,offset,initial,True,output_transform=True)
        error=float(np.max(abs(np.array(actual)-expected)))
        assert error<1e-6
        assert np.max(abs(np.array(actual[:4])-initial[:4]))>.5,'Offset still ignored'
        assert np.max(abs(np.array(actual[4:])-initial[4:]))<1e-6,'Connection damaged translation/scale'
        checks.append(dict(input_node=input_node,output_node=output_node,angle=angle,max_error=error))
report=dict(pass_=True,checks=checks,scope='Six synthetic thumb graph cases versus original 4E84A0; loader factory chain established statically. Live thumb output validation still pending.')
(Path(__file__).parent/'ControllerState/thumb-offset-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(pass_=True,cases=len(checks),max_error=max(c['max_error']for c in checks))))
