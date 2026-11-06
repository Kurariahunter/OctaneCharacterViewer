"""Installed-PC native scalar curves and Euler convention 2, offline only."""
import struct,math
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
STOP=0x10000100

def curve(data,time,dims):
 if len(data)>=0x6000 or not 1<=dims<=128:raise ValueError('curve extent')
 word=struct.unpack_from('<I',data)[0];kind=word&0x3c0
 if kind not in (0,0x40)or((word>>10)&1023)!=dims:raise ValueError('unsupported native curve encoding/dimensions')
 routine=0x523520 if kind==0x40 else 0x522cf0
 stack=0x10010000;source=0x10002000;out=0x10008000;ptr=0x10009000
 u.mem_write(source,data);u.mem_write(out,b'\0'*(dims*4));u.mem_write(ptr,struct.pack('<I',out));u.mem_write(ptr+16,b'\0'*4);u.mem_write(stack,struct.pack('<IfIII',STOP,time,source,ptr,ptr+16));u.reg_write(UC_X86_REG_ESP,stack);u.emu_start(routine,STOP,count=500000 if kind else 200000)
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('curve did not return')
 v=list(struct.unpack('<'+'f'*dims,u.mem_read(out,dims*4)))
 if not all(math.isfinite(x) for x in v):raise ValueError('nonfinite curve')
 return v

def rotation(angles):
 source=0x10001000;out=source+32;stack=0x10010000
 u.mem_write(source,struct.pack('<3f',*angles));u.mem_write(out,b'\0'*16);u.mem_write(stack,struct.pack('<II',STOP,out));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,source);u.emu_start(0x40e180,STOP,count=20000)
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('rotation did not return')
 q=list(struct.unpack('<4f',u.mem_read(out,16)))
 if abs(sum(x*x for x in q)-1)>1e-5:raise ValueError('nonunit rotation')
 return q
