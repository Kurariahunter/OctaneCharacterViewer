"""Original Transform compose/point/concatenate helpers. Explicit Scale/Unscale payloads."""
import struct,json,random
from pathlib import Path
import numpy as np
from native_pc_lean_ik import u,sha
from evaluate_pc_arms import quat
from evaluate_pc_arms import rotor
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
ROOT=Path(__file__).parent
STACK=0x10018000;STOP=0x10000100;PROC=0x10001000;META=0x10003000

def execute(fn,args,this=PROC):
 u.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),STOP,*args));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,this);u.emu_start(fn,STOP,count=200000)
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('no return')
def payload(q,t,scale,unscale):return list(q)+list(t)+[scale[3]]+list(scale)+list(unscale[:3])+[1.0]
def compose(q,t,scale,unscale):
 u.mem_write(PROC,b'\0'*512);u.mem_write(META,b'\0'*64);nodes=[0x10004000+i*256 for i in range(5)];aggregate=nodes[0]
 for n in nodes:
  u.mem_write(n,b'\0'*160);u.mem_write(n+0x1c,struct.pack('<I',META))
 init=payload([0,0,0,1],[0,0,0],[1]*4,[1]*4);u.mem_write(aggregate+0x34,struct.pack('<16f',*init))
 for n,vals in zip(nodes[1:],[t,q,scale,unscale]):u.mem_write(n+0x34,struct.pack('<'+'f'*len(vals),*vals))
 u.mem_write(PROC+0x18,struct.pack('<I',aggregate));u.mem_write(PROC+0x1c,struct.pack('<H',0x80));u.mem_write(PROC+0x80,struct.pack('<4I',*[n|1 for n in nodes[1:]]));execute(0x5303e0,[])
 return list(struct.unpack('<16f',u.mem_read(aggregate+0x34,64)))
def point(state,v,return_state=False):
 out=0x10008000;vin=0x10008100;tr=0x10008200
 u.mem_write(vin,struct.pack('<3f',*v));u.mem_write(tr,struct.pack('<16f',*state));u.mem_write(out,b'\0'*16);execute(0x4c4350,[out,vin,tr]);result=np.array(struct.unpack('<3f',u.mem_read(out,12)))
 # Native point at4c435b..4c435e writes uniform(+1c) into Scale.w(+2c).
 # Preserve the default point-only API; expose the post-call numeric state for
 # comparison with already-consumed live Transform payloads.
 return (result,list(struct.unpack('<16f',u.mem_read(tr,64)))) if return_state else result
def concat(child,parent):
 out=0x10008000;a=0x10008200;b=0x10008300;u.mem_write(out,b'\0'*64);u.mem_write(a,struct.pack('<16f',*child));u.mem_write(b,struct.pack('<16f',*parent));execute(0x4c2d50,[out,a,b]);return list(struct.unpack('<16f',u.mem_read(out,64)))
