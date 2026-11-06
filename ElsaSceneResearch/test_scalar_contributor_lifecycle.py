"""Execute native registration/removal with explicit cached scalar state."""
import json,struct
from pathlib import Path
import native_pc_blend_replay as n
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_EAX
def ui(a):return struct.unpack('<I',n.u.mem_read(a,4))[0]
def call(address,args):
 n.put(n.STACK,n.STOP)
 for i,value in enumerate(args):n.put(n.STACK+4+i*4,value)
 n.u.reg_write(UC_X86_REG_ESP,n.STACK);n.u.reg_write(UC_X86_REG_ECX,n.PROC)
 n.u.emu_start(address,n.STOP,count=500000)
 assert n.u.reg_read(UC_X86_REG_EIP)==n.STOP
 return n.u.reg_read(UC_X86_REG_EAX)
def state():return dict(flags=ui(n.PROC+0x18),fade_hex=bytes(n.u.mem_read(n.PROC+0x34,4)).hex(),output_hex=bytes(n.u.mem_read(n.OUT+0x34,4)).hex())
rows=[]
for flags in [0x0000ffff,0x8000ffff]:
 for fade in [0.,.25,1.]:
  c=dict(values=[10.]+[0.]*15,priority=5.,flag=0,weight=None,factor2c=None,factor30=1.)
  n.blend([c],scalar=True)
  n.put(n.PROC+0x18,flags);n.fp(n.PROC+0x34,fade);n.fp(n.OUT+0x34,7.)
  n.put(n.PROC+0x2c,8) # Preallocated fixture; avoid native allocator paths.
  before=state();ctrl=n.BASE+0x5000
  assert call(0x5337a0,[ctrl])&255==1 and ui(n.PROC+0x28)==0
  assert state()==before
  call(0x5440c0,[ctrl,0,0]);assert ui(n.PROC+0x28)==1
  assert state()==before
  assert call(0x5337a0,[ctrl+0x10000])&255==0
  assert ui(n.PROC+0x28)==1 and state()==before
  rows.append(dict(flags=hex(flags),fade=fade,state_preserved=before))
report=dict(passed=True,exe_sha256=n.sha,cases=rows,scope='Native5337A0 removal,5440C0 insertion and absent-controller removal; one synthetic preallocated contributor. Flags/fade/output preserved. Does not prove broader activation/default-network binding or allocation paths preserve state.')
(Path(__file__).parent/'ControllerState/scalar-contributor-lifecycle-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows),operations_per_case=3)))
