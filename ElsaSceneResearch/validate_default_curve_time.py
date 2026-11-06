"""Default phase/stop and activation compared with original native routines."""
import json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'OctaneCharacterViewer'))
from native_default_clock import ClockInputs
from native_default_curve_time import DefaultCurveTime
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x2D000000;u.mem_map(B,0x20000);P=B+0x1000;INPUT=B+0x2000;S=B+0x18000;STOP=B+0x1F000
def seed(state):
 u.mem_write(P,b'\0'*128);u.mem_write(S,b'\0'*128)
 for off,v in [(0x3c,state.lower),(0x40,state.upper),(0x44,state.rate1),(0x48,state.rate2),(0x50,state.previous_clock),(0x54,state.phase)]:u.mem_write(P+off,struct.pack('<f',v))
 u.mem_write(P+0x60,struct.pack('<HBB',int(state.reverse),0xf8,state.state_byte63))
def native_phase(state,clock):
 seed(state);u.mem_write(INPUT,struct.pack('<f',clock))
 u.reg_write(UC_X86_REG_EAX,INPUT);u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_ESP,S)
 u.emu_start(0x533D84,0x53409D,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x53409D
 return struct.unpack('<f',u.mem_read(P+0x54,4))[0],u.mem_read(P+0x63,1)[0]
cases=[]
for reverse in [False,True]:
 for phase in [.25,.875,1.75]:
  for dt in [-.25,0.,.125,.75,1.5,4.5]:
   for r1,r2 in [(1.,1.),(.5,2.),(0.,1.),(-1.,1.)]:
    state=DefaultCurveTime(.25,1.75,phase=phase,rate1=r1,rate2=r2,reverse=reverse)
    initial=ClockInputs(100.,0.,1,1);state.activate(initial)
    inp=ClockInputs(100.+dt,0.,2,2);expected=native_phase(state,inp.seconds);actual=state.request(inp)
    assert (actual,state.state_byte63)==expected,(reverse,phase,dt,r1,actual,expected)
    cases.append({'reverse':reverse,'phase':phase,'delta':dt,'rates':[r1,r2],'result':actual,'state_byte63':state.state_byte63})
activation=[]
for status in [0,1,3]:
 state=DefaultCurveTime(0.,1.,phase=.5);state.state_byte63=status;state.previous_clock=2.
 seed(state)
 # Original activation resolves input zero from the state-relative pointer array.
 u.mem_write(P+0x18,struct.pack('<HBB',0x64,2,1));u.mem_write(P+0x64,struct.pack('<I',INPUT))
 u.mem_write(INPUT+0x34,struct.pack('<f',10.));u.mem_write(S,struct.pack('<I',STOP))
 u.reg_write(UC_X86_REG_ECX,P);u.reg_write(UC_X86_REG_ESP,S)
 u.emu_start(0x4969C0,STOP,count=10000);assert u.reg_read(UC_X86_REG_EIP)==STOP
 state.activate(ClockInputs(10.,0.,1,1))
 assert state.previous_clock==struct.unpack('<f',u.mem_read(P+0x50,4))[0]
 assert state.state_byte63==u.mem_read(P+0x63,1)[0]==0
 activation.append({'prior_status':status,'cached_clock':state.previous_clock})
out=Path(__file__).parent/'ControllerState/default-curve-time-validation.json'
out.write_text(json.dumps({'pass':True,'exe_sha256':sha,'phase_cases':cases,'activation_cases':activation,'scope':'Original time window for applied F8 and complete activation with metadata/callback pointers null. Checks phase and state byte63, not event flags/marker, callbacks, frozen update output, or full graph.'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'phase_cases':len(cases),'activation_cases':len(activation)}))
