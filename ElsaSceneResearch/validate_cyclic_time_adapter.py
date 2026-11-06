"""Native curve arithmetic comparisons and demand-driven clock integration."""
import json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'OctaneCharacterViewer'))
from native_default_clock import DefaultEngineClock,ClockInputs
from native_cyclic_time import CyclicCurveTime
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x2B000000;u.mem_map(B,0x20000);P=B+0x1000;INPUT=B+0x2000;S=B+0x18000
def native(state,clock):
 u.mem_write(P,b'\0'*128);u.mem_write(S,b'\0'*128)
 for off,v in [(0x3c,state.lower),(0x40,state.upper),(0x44,state.rate1),(0x48,state.rate2),(0x50,state.previous_clock),(0x54,state.phase)]:u.mem_write(P+off,struct.pack('<f',v))
 u.mem_write(P+0x60,struct.pack('<HBB',int(state.reverse),14,0));u.mem_write(INPUT,struct.pack('<f',clock))
 u.reg_write(UC_X86_REG_EAX,INPUT);u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_ESP,S)
 u.emu_start(0x533D84,0x53409D,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x53409D
 return struct.unpack('<f',u.mem_read(P+0x54,4))[0]
cases=[]
for reverse in [False,True]:
 for rate1,rate2 in [(1.,1.),(.5,2.),(0.,1.),(-1.,1.)]:
  for dt in [-.25,0.,.125,.75,4.5]:
   state=CyclicCurveTime(.25,1.75,phase=.875,previous_clock=100.,rate1=rate1,rate2=rate2,reverse=reverse)
   inputs=ClockInputs(100.+dt,0.,1,1);expected=native(state,inputs.seconds);actual=state.request(inputs)
   assert actual==expected,(actual,expected)
   cases.append({'reverse':reverse,'rate1':rate1,'rate2':rate2,'delta':dt})
# Endpoint handling is not equivalent to blindly applying modulo at every step.
endpoints=[]
for reverse in [False,True]:
 for phase in [.25,1.75]:
  for dt in [0.,1.5,3.,4.5]:
   state=CyclicCurveTime(.25,1.75,phase=phase,reverse=reverse)
   inputs=ClockInputs(dt,0.,1,1);expected=native(state,dt);actual=state.request(inputs)
   assert actual==expected
   endpoints.append({'reverse':reverse,'phase':phase,'delta':dt,'result':actual})
clock=DefaultEngineClock();fast=CyclicCurveTime(0.,.125);lazy=CyclicCurveTime(0.,.125)
checks=0
for tick,dt in enumerate([16,17,16,100,250,0,16,17]*4):
 clock.advance(dt);inputs=clock.publish()
 for state in ([fast,lazy] if tick%3==0 else [fast]):
  expected=native(state,inputs.seconds);actual=state.request(inputs);assert actual==expected
  before=state.consumer.evaluations;assert state.request(inputs)==actual and state.consumer.evaluations==before
  checks+=1
report={'pass':True,'exe_sha256':sha,'rate_direction_cases':len(cases),'endpoint_cases':endpoints,'demand_sequence_native_comparisons':checks,
 'scope':'Original time arithmetic window with boundary byte 0x0E, finite in-range initial phases and positive ranges. Exact float32 phase comparisons. Clock adapter supplies inputs; native node lookup, flags/token bookkeeping, frozen branch, output emission, dynamics and full sampler remain outside this fixture.'}
(Path(__file__).parent/'ControllerState/cyclic-time-adapter-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'rate_direction_cases':len(cases),'endpoint_cases':len(endpoints),'demand_sequence_native_comparisons':checks}))
