"""PC TransformTranslationOrientationScaleConnection, observed no-offset input graph."""
import math,struct
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
B=0x34000000;u.mem_map(B,0x10000)

def connect(value,initial,translate_offset=None,rotate_offset=None):
 if any(len(v)!=16 or not all(math.isfinite(x)for x in v)for v in (value,initial)):raise ValueError('Finite typed Transform input/output required')
 if translate_offset is not None and(len(translate_offset)!=3 or not all(math.isfinite(x)for x in translate_offset)):raise ValueError('Finite translation offset required')
 if rotate_offset is not None and(len(rotate_offset)!=4 or not all(math.isfinite(x)for x in rotate_offset)):raise ValueError('Finite rotor offset required')
 u.mem_write(B,bytes(0x10000));proc=B+0x1000;meta=B+0x2000;types=B+0x2100;inp=B+0x3000;out=B+0x3200;stack=B+0xe000;stop=B+0x100
 def put(a,v):u.mem_write(a,struct.pack('<I',v))
 for a,v in ((0x21aee78,1),(0x21aee7c,0xffffffff),(0x213e48c,2),(0x213e490,0xffffffff),(0x21ae4c8,3),(0x21ae4cc,0xffffffff)):put(a,v)
 put(types,2);u.mem_write(proc+0x18,struct.pack('<HBB',0x80,4,1));u.mem_write(proc+0x80,struct.pack('<5I',inp,B+0x3400 if translate_offset is not None else 0,B+0x3600 if rotate_offset is not None else 0,0,out))
 for node,data in ((inp,value),(out,initial)):
  put(node+0x10,types);put(node+0x1c,meta);u.mem_write(node+0x34,struct.pack('<16f',*data))
 if translate_offset is not None:
  put(B+0x341c,meta);u.mem_write(B+0x3434,struct.pack('<3f',*translate_offset))
 if rotate_offset is not None:
  put(B+0x361c,meta);u.mem_write(B+0x3634,struct.pack('<4f',*rotate_offset))
 put(stack,stop);u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc);u.emu_start(0x4d9f50,stop,count=200000)
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('Scaled connection failed to return')
 return list(struct.unpack('<16f',u.mem_read(out+0x34,64)))
