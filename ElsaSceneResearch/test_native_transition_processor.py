"""Original transition activation/update instructions, explicit offline fixtures."""
import json,struct
from pathlib import Path
from native_transition_processor import activate,step,sha
from native_scalar_state import ScalarStates
R=Path(__file__).parent
identity=json.loads((R/'ControllerState/live-fade-producer-identity.json').read_text())
original=bytes.fromhex(identity[2]['hex'])
def f(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def get(h,o):return struct.unpack_from('<f',h,o)[0]
rows=[]
for start,end,duration,offset,delay in [(0.,1.,.1,0.,0.),(1.,0.,.2,.25,.05),(0.,1.,0.,0.,0.)]:
 h=activate(original,10.,start=start,end=end,duration=duration,clock_offset=offset,delay=delay)
 assert get(h,0x48)==f(10.-offset)and get(h,0x4c)==f(10.-offset)and h[0x54]==0
 assert get(h,0x2c)==f(f(10.-offset)+delay)
 for clock in [10.,10.025,10.05,10.1,10.25,10.5]:
  value,after=step(h,clock)
  elapsed=f(f(f(clock)-get(h,0x48))*get(h,0x50));local=f(get(h,0x4c)+elapsed)
  assert get(after,0x48)==f(clock)and get(after,0x4c)==local
  if duration==0:expected=start if local<get(h,0x2c)else end
  else:
   phase=max(0.,min(1.,f(f(local-get(h,0x2c))/get(h,0x24))))
   expected=f(start+(end-start)*phase)
  assert value==expected,(value,expected)
  rows.append(dict(start=start,end=end,duration=duration,clock=clock,value=value,completion=after[0x54]));h=after
 assert h[0x54]==1
# The verified producer and scalar blender compose without fitted offsets.
h=activate(original,0.,duration=.1);bank=ScalarStates();bank.seed('finger',2.,0.,False);composed=[]
for clock in [0.,.025,.05,.075,.1]:
 factor,h=step(h,clock);value=bank.update('finger',10.,factor);composed.append(dict(clock=clock,factor=factor,output=value))
assert composed[0]['output']==2. and composed[-1]['output']==10.
report=dict(passed=True,exe_sha256=sha,transition_cases=rows,producer_to_scalar=composed,scope='Original52D9B0 activation and53C800 update with observed mode1, synthetic clock/curve arguments and empty event/callback fixture. Completion flags tested; actor-selected activation arguments and callback effects not reconstructed.')
(R/'ControllerState/transition-processor-native-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows),producer_to_scalar=composed)))
