"""Execute full child-clock updater and bound all its memory writes."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x26000000;u.mem_map(B,0x20000)
P=B+0x1000;S=B+0x18000;STOP=B+0x1F000
def put(a,x):u.mem_write(a,struct.pack('<I',x))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
rows=[];writes=[]
hook=u.hook_add(UC_HOOK_MEM_WRITE,lambda uc,access,address,size,value,user:writes.append((address,size)))
try:
 for mode in range(5):
  for raw,capped in [(0,0),(16,16),(100,50)]:
   for transition in [0,1]:
    u.mem_write(P,b'\0'*128);u.mem_write(S-256,b'\0'*512)
    put(P,17);put(P+8,1000);put(P+0x18,mode);put(P+0x20,1);put(P+0x24,50)
    u.mem_write(P+0x28,struct.pack('<5f',.25,1.,.5,0.,.5))
    u.mem_write(P+0x3D,bytes([transition]))
    u.mem_write(S,struct.pack('<5I',STOP,raw,capped,0,0))
    u.mem_write(STOP+0x100,b'\xDB\xE3');u.emu_start(STOP+0x100,STOP+0x102,count=10)
    writes.clear();u.reg_write(UC_X86_REG_ECX,P);u.reg_write(UC_X86_REG_ESP,S)
    u.emu_start(0x679000,STOP,count=10000)
    assert u.reg_read(UC_X86_REG_EIP)==STOP
    expected=17 if transition else [0,max(1,capped>>1),capped<<1,capped,max(1,int(capped*.5))][mode]
    assert get(P)==expected and get(P+8)==1000+expected
    assert all(P<=a and a+n<=P+0x40 or S-256<=a and a+n<=S+20 for a,n in writes),writes
    rows.append({'mode':mode,'raw_ms':raw,'capped_ms':capped,'transition':transition,'effective_ms':get(P),'writes_confined_to_child_and_stack':True})
finally:u.hook_del(hook)
out=Path(__file__).parent/'ControllerState'
(out/'child-clock-validation.json').write_text(json.dumps({'pass':True,'exe_sha256':sha,'cases':rows,'scope':'Full original 0x679000 function, synthetic disjoint child object, no expiry countdown. All writes monitored. Does not execute container traversal/removal or prove live allocations cannot alias.'},indent=2)+'\n',encoding='utf-8')
(out/'child_clock_update.txt').write_text(disasm(0x679000,0x1E3),encoding='utf-8')
(out/'child_clock_traversal.txt').write_text(disasm(0x67AC00,0x64),encoding='utf-8')
print(json.dumps({'pass':True,'cases':len(rows),'writes_confined':True}))
