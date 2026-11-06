"""Native default-reference assignment and 16-bit channel binding window.

Windows InterlockedIncrement/Decrement imports use explicit single-thread x86
atomic shims. No game function call is replaced. Object freeing is excluded.
"""
import json,struct
from pathlib import Path
import native_pc_blend_replay as n
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_EBP,UC_X86_REG_ESP,UC_X86_REG_EIP
def ui(a):return struct.unpack('<I',n.u.mem_read(a,4))[0]
inc_iat,dec_iat=0x1ae3238,0x1ae323c
saved=[bytes(n.u.mem_read(a,4))for a in (inc_iat,dec_iat)]
rows=[]
try:
 for high in [0,0x80000000]:
  for index in [33,39,0xffff]:
   n.blend([dict(values=[10.]+[0.]*15,priority=5.,flag=0,weight=None,factor2c=None,factor30=1.)],scalar=True)
   old,new=n.BASE+0x16000,n.BASE+0x16400
   n.put(old+4,3);n.put(new+4,3);n.put(n.PROC+0x1c,old)
   n.put(n.PROC+0x18,high|0xabcd);n.fp(n.PROC+0x34,.25);n.fp(n.OUT+0x34,7.)
   # mov ecx,[esp+4]; mov eax,+/-1; lock xadd [ecx],eax;
   # inc/dec eax; ret4. These emulate Windows atomic import semantics.
   for address,delta,opcode,iat in [(n.BASE+0x17000,1,0x40,inc_iat),(n.BASE+0x17020,0xffffffff,0x48,dec_iat)]:
    n.u.mem_write(address,b'\x8b\x4c\x24\x04\xb8'+struct.pack('<I',delta)+b'\xf0\x0f\xc1\x01'+bytes([opcode])+b'\xc2\x04\x00');n.put(iat,address)
   n.put(n.STACK+0x58,new)
   n.u.reg_write(UC_X86_REG_ESI,n.PROC);n.u.reg_write(UC_X86_REG_EBP,index);n.u.reg_write(UC_X86_REG_ESP,n.STACK)
   n.u.emu_start(0x50043b,0x50044c,count=100000)
   assert n.u.reg_read(UC_X86_REG_EIP)==0x50044c
   assert ui(n.PROC+0x18)==high|index and ui(n.PROC+0x1c)==new
   assert struct.unpack('<f',n.u.mem_read(n.PROC+0x34,4))[0]==.25
   assert struct.unpack('<f',n.u.mem_read(n.OUT+0x34,4))[0]==7.
   assert ui(old+4)==2 and ui(new+4)==4
   rows.append(dict(bypass_before=bool(high),channel=index,flags_after=hex(ui(n.PROC+0x18)),fade_preserved=True,output_preserved=True,old_reference_count=2,new_reference_count=4))
finally:
 for a,value in zip((inc_iat,dec_iat),saved):n.u.mem_write(a,value)
n.u.mem_write(n.PROC,b'\xaa'*64)
n.u.reg_write(UC_X86_REG_ESI,n.PROC);n.u.reg_write(UC_X86_REG_ESP,n.STACK)
n.u.emu_start(0x533747,0x533770,count=100000)
assert n.u.reg_read(UC_X86_REG_EIP)==0x533770
assert ui(n.PROC+0x18)==0xffff and ui(n.PROC+0x1c)==0 and ui(n.PROC+0x30)==0 and ui(n.PROC+0x34)==0
result=dict(passed=True,exe_sha256=n.sha,cases=rows,constructor_flags=hex(ui(n.PROC+0x18)),constructor_fade=0,scope='Original50043B..50044C plus450900, and constructor window533747..533770. Explicit Windows atomic-import shims for binding; no freeing, output setter525400, typed factory selection or full actor binding lifecycle. Constructor clears high bits; binding preserves them.')
(Path(__file__).parent/'ControllerState/scalar-binding-assignment-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows))))
