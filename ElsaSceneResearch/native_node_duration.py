"""Native finite cached-duration selection; actor/source lookup is external."""
import math,struct
import native_transition_processor as t
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_EDX,UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
def select(cached_parameter,override=None,flags=0):
 if not math.isfinite(cached_parameter)or(override is not None and not math.isfinite(override)):raise ValueError('Finite node parameters required')
 if not isinstance(flags,int)or not 0<=flags<=255:raise ValueError('Byte flags required')
 t.u.mem_write(t.B,bytes(0x20000));node=t.B+0x6000;extra=t.B+0x8000
 t.u.mem_write(t.STACK+0x14,struct.pack('<f',cached_parameter))
 if override is not None:
  t.put(node+0x2c,extra);t.u.mem_write(extra+8,struct.pack('<f',override));t.u.mem_write(extra+0x10,struct.pack('<f',-1.))
 t.u.mem_write(node+0x114,bytes([flags]))
 t.u.reg_write(UC_X86_REG_ESP,t.STACK);t.u.reg_write(UC_X86_REG_ESI,node);t.u.reg_write(UC_X86_REG_EDX,flags);t.u.reg_write(UC_X86_REG_EAX,0)
 t.u.emu_start(0x1448b61,0x1448c15,count=10000)
 if t.u.reg_read(UC_X86_REG_EIP)!=0x1448c15:raise ValueError('Node duration instruction window failed')
 return struct.unpack('<f',t.u.mem_read(t.STACK+0x14,4))[0]
