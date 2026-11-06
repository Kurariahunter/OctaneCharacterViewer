"""PC-isolated native dress math; no old model/clip dependencies."""
import struct,json,random
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
P=0x10001000;META=0x10003000;STACK=0x10018000;STOP=0x10000100

def call(fn,values,layout,count,initial=None,normal_input_count=None):
 u.mem_write(P,b'\0'*512);u.mem_write(META,b'\0'*64);nodes=[0x10004000+256*i for i in range(len(values)+1)]
 ptrs=[n if v is not None else 0 for n,v in zip(nodes,values)]+[nodes[-1]]
 if layout=='array':u.mem_write(P+0x18,struct.pack('<HBB',0x80,len(values),1));u.mem_write(P+0x80,struct.pack('<'+'I'*len(ptrs),*ptrs))
 else:u.mem_write(P+0x18,struct.pack('<'+'I'*len(ptrs),*ptrs))
 if normal_input_count is not None:
  if layout!='array' or not 0<=normal_input_count<=len(values):raise ValueError('invalid normal-input count')
  u.mem_write(P+0x1c,struct.pack('<I',normal_input_count))
 for n,v in zip(nodes,values+[initial or ([0,0,0,1] if count==4 else [0]*count)]):
  u.mem_write(n,b'\0'*160);u.mem_write(n+0x10,struct.pack('<I',META));u.mem_write(n+0x1c,struct.pack('<I',META))
  if v is not None:u.mem_write(n+0x34,struct.pack('<'+'f'*len(v),*v))
 for g in [0x21aee78,0x21aee7c,0x213e710,0x213e70c,0x213e490,0x213e48c]:u.mem_write(g,struct.pack('<I',0))
 u.mem_write(STACK,struct.pack('<I',STOP));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,P)
 try:u.emu_start(fn,STOP,count=300000)
 except Exception as ex:raise RuntimeError(hex(u.reg_read(UC_X86_REG_EIP))+' '+str(ex))
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('no return')
 return list(struct.unpack('<'+'f'*count,u.mem_read(nodes[-1]+0x34,4*count)))

def aim(align,reference,up,upref,initial=None):return call(0x534380,[list(align),list(reference),list(up),list(upref),None,None],'array',4,initial)
def inverse_point(v,tr):return call(0x4d57e0,[list(v),list(tr)],'typed',3)
def inverse_vector(v,tr):return call(0x4d46f0,[list(v),list(tr)],'typed',3)
def difference(a,b):return call(0x52d0e0,[list(a),list(b)],'array',3)
