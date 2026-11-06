import json,struct
from pathlib import Path
from native_pc_keyblend_time import evaluate
f=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
cases=[]
for duration in (.6,1.,2.):
    for t in (0,.1,.3,.6,1.):
        for alpha in (0,.25,.75,1.):
            children=[.5,.8];r=evaluate(t,duration,children,alpha)
            normalized=f(f(t)/f(duration));expected=[f(f(d)*normalized)for d in children[:1 if alpha==0 else 2]]
            assert [c['time']for c in r['child_calls']]==expected
            assert [b['weight']for b in r['blend_calls']]==([]if alpha==0 else [1.,alpha])
            assert all(b['mode']==1 and b['filter']==0 for b in r['blend_calls'])
            cases.append(dict(duration=duration,time=t,alpha=alpha))
# Native fallback uses normalized1 when parent duration is zero in this fixture.
r=evaluate(.3,0,[.5,.8],.25);assert [c['time']for c in r['child_calls']]==[f(.5),f(.8)]
report=dict(cases=len(cases)+1,pass_=True,scope='Native parent time arithmetic and call argument capture with explicit child/buffer boundaries. Full parent output and duration calculation not tested.')
(Path(__file__).parent/'ControllerState/keyblend-time-native-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
