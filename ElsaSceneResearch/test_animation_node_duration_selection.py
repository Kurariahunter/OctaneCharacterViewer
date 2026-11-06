"""Native caller duration getter, override, force-zero and 1/30 conversion."""
import struct,json
from pathlib import Path
import native_transition_processor as t
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EDX,UC_X86_REG_EAX,UC_X86_REG_EIP
def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def fp(a,x):t.u.mem_write(a,struct.pack('<f',x))
rows=[]
for default in [-3.,0.,3.,6.]:
 for override in [None,-1.,0.,9.]:
  for flags in [0,4]:
   t.u.mem_write(t.B,bytes(0x20000));node=t.B+0x6000;view=t.B+0x7000;data=t.B+0x7100;extra=t.B+0x8000
   t.put(view,data);fp(data+0x14,default)
   t.u.reg_write(UC_X86_REG_ECX,view);t.u.reg_write(UC_X86_REG_ESP,t.STACK)
   t.u.emu_start(0x1448b4a,0x1448b53,count=1000)
   assert struct.unpack('<f',t.u.mem_read(t.STACK+0x14,4))[0]==default
   if override is not None:t.put(node+0x2c,extra);fp(extra+8,override);fp(extra+0x10,-1.)
   t.u.mem_write(node+0x114,bytes([flags]));fp(t.STACK+0x18,0.);fp(t.STACK+0x1c,0.);fp(t.STACK+0x20,0.)
   t.u.reg_write(UC_X86_REG_ESI,node);t.u.reg_write(UC_X86_REG_EDX,flags);t.u.reg_write(UC_X86_REG_EAX,0)
   t.u.emu_start(0x1448b61,0x1448c15,count=10000)
   assert t.u.reg_read(UC_X86_REG_EIP)==0x1448c15
   actual=struct.unpack('<f',t.u.mem_read(t.STACK+0x14,4))[0]
   selected=override if override is not None and override>=0 else default
   if flags&4:selected=0.
   expected=f(max(0.,selected)*f(1/30));assert actual==expected,(default,override,flags,actual,expected)
   if flags&4:assert bytes(t.u.mem_read(node+0x114,1))[0]&4==0
   rows.append(dict(default_parameter=default,override=override,force_zero=bool(flags&4),duration_seconds=actual))
r=dict(passed=True,exe_sha256=t.sha,cases=rows,scope='Original1448B4A..1448B53 getter and1448B61..1448C15 selection/conversion windows. Synthetic animation-node parameter/override fixtures; no full actor/node scheduling or live branch-selection claim.')
(Path(__file__).parent/'ControllerState/animation-node-duration-selection-validation.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows))))
