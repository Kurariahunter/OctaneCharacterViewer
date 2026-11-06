"""Original dispatcher replay on captured52-byte rows; null-filter branch only."""
import math,struct
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
B=0x2e000000;u.mem_map(B,0x20000)

def replay(destination,source,weight,mode):
    if not math.isfinite(weight)or not 0<=weight<=1 or mode not in (0,1):raise ValueError('Unverified weight/mode')
    if len(source)%52 or len(destination)%52 or not 0<len(source)<=len(destination)<=256*52:raise ValueError('Invalid buffer extents')
    for data in (source,destination):
        for offset in range(0,len(data),52):
            if struct.unpack_from('<I',data,offset+48)[0]&~0x1ff:raise ValueError('Unverified channel mask')
    u.mem_write(B,b'\0'*0x20000)
    mgr=B+0x1000;table=B+0x2000;dst=B+0x3000;src=B+0x7000;stack=B+0x18000;stop=B+0x100
    def put(a,v):u.mem_write(a,struct.pack('<I',v))
    u.mem_write(dst,destination);u.mem_write(src,source);put(mgr,1);put(mgr+8,table)
    put(table+4,dst);put(table+8,len(destination)//52);put(table+20,src);put(table+24,len(source)//52)
    u.mem_write(stack,struct.pack('<IfII',stop,weight,mode,0))
    u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,mgr)
    u.emu_start(0x5a14d0,stop,count=2000000)
    if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('Native blend did not return')
    if struct.unpack('<I',u.mem_read(mgr,4))[0]!=0:raise ValueError('Native depth did not pop')
    return bytes(u.mem_read(dst,len(destination)))
