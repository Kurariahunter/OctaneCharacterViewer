"""Execute original AnimCurveControlProcessor time arithmetic and boundaries."""
import json,struct,math
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x21000000;u.mem_map(B,0x20000)
OBJ=B+0x1000;CLOCK=B+0x2000;STACK=B+0x18000
def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def put(off,x):u.mem_write(OBJ+off,struct.pack('<f',x))
cases=[]
for reverse in [False,True]:
 for rate1,rate2 in [(1.,1.),(.5,2.),(0.,1.),(-1.,1.)]:
  for dt in [-.25,0.,.125,.75,4.5]:
   u.mem_write(OBJ,b'\0'*128);u.mem_write(STACK,b'\0'*128)
   lo,hi=.25,1.75;phase=.875;clock=f(100.+dt)
   for off,x in [(0x3c,lo),(0x40,hi),(0x44,rate1),(0x48,rate2),(0x50,100.),(0x54,phase)]:put(off,x)
   u.mem_write(OBJ+0x60,struct.pack('<HBB',int(reverse),14,0)) # cyclic both directions, no clamps
   u.mem_write(CLOCK,struct.pack('<f',clock));u.reg_write(UC_X86_REG_EAX,CLOCK)
   u.reg_write(UC_X86_REG_ESI,OBJ);u.reg_write(UC_X86_REG_ESP,STACK)
   u.emu_start(0x533D84,0x53409D,count=100000)
   assert u.reg_read(UC_X86_REG_EIP)==0x53409D
   last,actual=struct.unpack('<2f',u.mem_read(OBJ+0x50,8))
   delta=max(0.,f(f(rate2*rate1)*f(clock-100.)))
   expected=f(phase-delta if reverse else phase+delta)
   if expected<lo:expected=f(hi-((lo-expected)%(hi-lo)))
   elif expected>hi:expected=f(lo+((expected-hi)%(hi-lo)))
   assert abs(actual-expected)<2e-6,(reverse,dt,rate1,actual,expected)
   assert last==clock
   cases.append({'reverse':reverse,'rate1':rate1,'rate2':rate2,'input_delta':dt,
                 'local_time':actual,'expected':expected,'error':abs(actual-expected)})
out=Path(__file__).parent/'ControllerState'
report={'pass':True,'exe_sha256':sha,'cases':cases,
        'scope':'Original time-update window 0x533D84..0x53409D, including original native remainder calls. Supplied input-clock pointer; skips node lookup, frozen-output branch and output emission. Synthetic cyclic mode byte +0x62=14; finite values only. Tests rates/direction/wrapping, not all flag combinations or callbacks.'}
capture_checks=[]
for filename in ['ce_controllerstate_20261019_095258_37237546.jsonl',
                 'ce_controllerstate_20261019_095352_37292187.jsonl',
                 'ce_controllerstate_20261019_094738_36918343.jsonl']:
    previous=None;transitions=advances=0;max_error=0.
    path=Path(__file__).parent.parent/'OctaneLiveInspector/Captures'/filename
    for line in path.read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        for c in event.get('contributions',{}).values():
            if c.get('controller')!='0x08A0C100':continue
            state=c['controller_state'];raw=bytes.fromhex(state['state_header_hex128'])
            identity=(state['source_asset'],state['state_object'])
            if previous and previous[0]==identity:
                old=previous[1];clock=struct.unpack_from('<f',raw,0x50)[0]
                oldclock=struct.unpack_from('<f',old,0x50)[0]
                u.mem_write(OBJ,old);u.mem_write(STACK,b'\0'*128)
                u.mem_write(CLOCK,struct.pack('<f',clock))
                u.reg_write(UC_X86_REG_EAX,CLOCK);u.reg_write(UC_X86_REG_ESI,OBJ);u.reg_write(UC_X86_REG_ESP,STACK)
                u.emu_start(0x533D84,0x53409D,count=100000)
                assert u.reg_read(UC_X86_REG_EIP)==0x53409D
                actual=struct.unpack('<f',u.mem_read(OBJ+0x54,4))[0]
                expected=struct.unpack_from('<f',raw,0x54)[0]
                error=abs(actual-expected);assert error<2e-6,(filename,actual,expected)
                transitions+=1;advances+=int(clock!=oldclock);max_error=max(max_error,error)
            previous=(identity,raw)
    capture_checks.append({'capture':filename,'transitions':transitions,'clock_changes':advances,
                           'max_local_time_error':max_error})
report['captured_local_time_replay']=capture_checks
report['captured_replay_scope']='Controller 0x08A0C100 only, previous captured state plus next captured input clock; short slices, duplicate output observations included. Does not prove full-cycle boundaries or clock producer.'
(out/'curve-control-time-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(out/'curve_control_update.txt').write_text(disasm(0x533D10,0x40F)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'native_cases':len(cases),'max_error':max(c['error'] for c in cases),
                  'capture_checks':capture_checks}))
