"""Original parent time/dispatch control flow; child and buffer calls are boundaries."""
import math,struct
from native_pc_lean_ik import u
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x30000000;u.mem_map(B,0x20000)

def evaluate(time,parent_duration,durations,alpha):
    if len(durations)!=2 or not all(math.isfinite(x)for x in [time,parent_duration,alpha]+list(durations))or not 0<=alpha<=1:raise ValueError('Time fixture bounds')
    p=B+0x1000;table=B+0x2000;children=[B+0x3000,B+0x3100];vt=B+0x4000;stack=B+0x18000;stop=B+0x100
    u.mem_write(B,b'\0'*0x20000)
    def put(a,v):u.mem_write(a,struct.pack('<I',v))
    u.mem_write(p+0x14,struct.pack('<f',parent_duration));put(p+0x24,table)
    u.mem_write(p+0x48,struct.pack('<fII',alpha,0,1));u.mem_write(table,struct.pack('<2I',*children))
    for c,d in zip(children,durations):put(c,vt);u.mem_write(c+0x14,struct.pack('<f',d))
    put(vt+0x24,stop+0x100)
    calls=[];blends=[]
    def hook(uc,address,size,unused):
        esp=uc.reg_read(UC_X86_REG_ESP)
        if address in (0x5a1695,0x5a16cd,0x5a1722):
            child=uc.reg_read(UC_X86_REG_ECX);t=struct.unpack('<f',uc.mem_read(esp,4))[0]
            calls.append(dict(site=hex(address),child=children.index(child),time=t))
            uc.reg_write(UC_X86_REG_ESP,esp+16);uc.reg_write(UC_X86_REG_EIP,address+2)
        elif address in (0x5a16ee,0x5a1740):
            weight,mode,filter_=struct.unpack('<fII',uc.mem_read(esp,12))
            blends.append(dict(site=hex(address),weight=weight,mode=mode,filter=filter_))
            uc.reg_write(UC_X86_REG_ESP,esp+12);uc.reg_write(UC_X86_REG_EIP,address+5)
        elif address in (0x5a16b0,0x5a1709):
            uc.reg_write(UC_X86_REG_EIP,address+5)
    token=u.hook_add(UC_HOOK_CODE,hook)
    try:
        u.mem_write(stack,struct.pack('<IfIII',stop,time,0,0,0));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,p)
        u.emu_start(0x5a1630,stop,count=100000)
        if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('Parent time did not return')
    finally:u.hook_del(token)
    return dict(child_calls=calls,blend_calls=blends,normalized_time=struct.unpack('<f',u.mem_read(stack+4,4))[0],
        scope='Original5A1630 arithmetic/control flow. Child evaluation, buffer push and blend dispatch are intercepted boundaries; no child pose or buffer result evaluated here.')
