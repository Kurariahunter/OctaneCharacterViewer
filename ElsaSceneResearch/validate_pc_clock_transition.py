"""Native smoothing branch, including whether it writes effective delta."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import read,disasm
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x25000000;u.mem_map(B,0x20000)
P=B+0x1000;S=B+0x18000;STOP=B+0x1F000
def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def put(a,x):u.mem_write(a,struct.pack('<I',x))
eps=struct.unpack('<f',read(0x1B23C4C,4))[0];rows=[]
for raw_ms in [0,16,100,1000]:
 for current,target,duration in [(1.,.5,.25),(.5,1.,.25),(1.,1.,.25),(1.,.5,0.)]:
  for retained in [0,17]:
    u.mem_write(P,b'\0'*128);u.mem_write(S,b'\0'*128)
    put(P+4,raw_ms);put(P+0x10,retained);put(P+0x18,1000);put(P+0x28,3)
    u.mem_write(P+0x38,struct.pack('<3f',duration,current,target));u.mem_write(P+0x51,b'\x01')
    put(S+20,STOP)
    u.mem_write(STOP+0x100,b'\xDB\xE3');u.emu_start(STOP+0x100,STOP+0x102,count=10)
    u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_ESP,S)
    u.emu_start(0x67B02F,STOP,count=1000)
    assert u.reg_read(UC_X86_REG_EIP)==STOP
    dt=f(raw_ms*f(.001));den=f(dt+duration)
    expected=target if den==0 else f(f(f(current*duration)+f(target*dt))/den)
    actual=struct.unpack('<f',u.mem_read(P+0x3C,4))[0]
    assert actual==expected,(actual,expected)
    active=u.mem_read(P+0x51,1)[0]
    assert active==int(abs(f(actual-target))>eps)
    assert struct.unpack('<I',u.mem_read(P+0x10,4))[0]==retained
    assert struct.unpack('<I',u.mem_read(P+0x18,4))[0]==1000+retained
    rows.append({'raw_ms':raw_ms,'current':current,'target':target,'duration':duration,'retained_effective_ms':retained,'new_scale':actual,'transition_active':active})
out=Path(__file__).parent/'ControllerState'
(out/'clock-transition-validation.json').write_text(json.dumps({'pass':True,'exe_sha256':sha,'epsilon':eps,'cases':rows,'scope':'Original 0x67B02F through return, seeded clock state/stack. Ordinary finite nonnegative inputs; OS timer, pre-branch callbacks, extreme exponent guard cases and live settings not executed.'},indent=2)+'\n',encoding='utf-8')
(out/'clock_publication_order.txt').write_text(disasm(0x6A0740,0x17)+'\n'+disasm(0x69F9A0,0x25)+'\n'+disasm(0x133EE60,0x26),encoding='utf-8')
print(json.dumps({'pass':True,'cases':len(rows),'epsilon':eps}))
