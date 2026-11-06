"""Native PC Dilation connection variants with explicit runtime type fixtures."""
import struct
from native_pc_lean_ik import u
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP

def connect(value,offset,initial,translation,input_transform=False,output_transform=False,translate_offset=None):
 proc=0x10001000;net=0x10003000;typeinfo=net+0x100;stack=0x10010000;stop=0x10000100
 u.mem_write(proc,b'\0'*512);u.mem_write(net,b'\0'*512);u.mem_write(typeinfo,struct.pack('<I',1))
 for a,v in [(0x21aee78,1),(0x21aee7c,0xffffffff),(0x213e48c,2),(0x213e490,0xffffffff),(0x21ae4c8,3),(0x21ae4cc,0xffffffff)]:u.mem_write(a,struct.pack('<I',v))
 nodes=[0x10004000+i*256 for i in range(4)]
 # Translation+orientation: Input, optional TranslateOffset, RotateOffset.
 # Orientation-only: Input, RotateOffset.
 if translate_offset is not None:
  if not translation or len(translate_offset)!=3:raise ValueError('Translation offset requires translation connection and three values')
 refs=[nodes[0],nodes[2]if translate_offset is not None else 0,nodes[1],nodes[3]] if translation else [nodes[0],nodes[1],nodes[3]]
 u.mem_write(proc+0x18,struct.pack('<HBB',0x80,len(refs)-1,1));u.mem_write(proc+0x80,struct.pack('<'+'I'*len(refs),*refs))
 u.mem_write(typeinfo+4,struct.pack('<I',2))
 values=[(nodes[0],value),(nodes[1],offset),(nodes[3],initial)]
 if translate_offset is not None:values.append((nodes[2],translate_offset))
 for ptr,vals in values:
  u.mem_write(ptr,b'\0'*128);u.mem_write(ptr+0x10,struct.pack('<I',typeinfo+4 if input_transform and ptr==nodes[0] else typeinfo));u.mem_write(ptr+0x1c,struct.pack('<I',net));u.mem_write(ptr+0x34,struct.pack('<'+'f'*len(vals),*vals))
 u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc);u.emu_start(0x4e84a0 if translation else 0x4e84b0,stop,count=200000)
 assert u.reg_read(UC_X86_REG_EIP)==stop
 width=16 if output_transform else 8
 return list(struct.unpack('<'+'f'*width,u.mem_read(nodes[3]+0x34,width*4)))
