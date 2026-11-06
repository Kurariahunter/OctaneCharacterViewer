"""Original KeyBlend selector with effective parameter supplied as constant fixture."""
import math,struct
from native_pc_lean_ik import u
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x2f000000;u.mem_map(B,0x20000)

def select(value,keys,children,initial=(0,0,0.)):
    if not math.isfinite(value)or not 1<=children<=64 or len(keys)>64 or any(not math.isfinite(x)for x in keys):raise ValueError('Selector bounds')
    if keys and len(keys)!=children:raise ValueError('Only explicit complete keys or uniform keys supported')
    if keys and any(a>=b for a,b in zip(keys,keys[1:])):raise ValueError('Non-increasing keys')
    if not keys and not 0<=value<=1:raise ValueError('Uniform parameter outside tested range')
    p=B+0x1000;k=B+0x2000;stack=B+0x18000;stop=B+0x100
    u.mem_write(B,b'\0'*0x20000)
    u.mem_write(p+0x28,struct.pack('<I',children));u.mem_write(p+0x34,struct.pack('<II',k,len(keys)))
    u.mem_write(p+0x44,struct.pack('<ffII',value,initial[2],initial[0],initial[1]))
    if keys:u.mem_write(k,struct.pack('<'+'f'*len(keys),*keys))
    u.mem_write(0x21c1950,b'\0') # disable native debug parameter override in isolated fixture
    u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,p)
    u.emu_start(0x59dc50,stop,count=100000)
    if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('Selector did not return')
    alpha,left,right=struct.unpack('<fII',u.mem_read(p+0x48,12))
    return dict(left=left,right=right,alpha=alpha)
