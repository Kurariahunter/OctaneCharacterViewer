"""Original blended-buffer output routine on bounded typed node fixtures."""
import struct
from native_pc_lean_ik import u
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x31000000;u.mem_map(B,0x40000)
GLOBALS=(0x213e490,0x213e48c,0x213e6f0,0x213e6ec,0x21aee5c,0x21aee58,0x21bc110,0x21bc10c,0x213e3d0,0x213e3cc,0x21aedfc,0x21aedf8)

def replay(rows,nodes,globals_):
    count=len(nodes)
    if not 1<=count<=256 or len(rows)!=52*count:raise ValueError('Output row extent')
    p=B+0x1000;array=B+0x2000;frame=B+0x3000;source=B+0x4000;stack=B+0x38000;stop=B+0x100
    u.mem_write(B,b'\0'*0x40000)
    def put(a,v):u.mem_write(a,struct.pack('<I',v))
    put(p+0x30,array);put(p+0x34,count);put(p+0x74,0);put(p+0x7c,frame);put(frame+4,source);put(frame+8,count)
    u.mem_write(source,rows);active={}
    for i,node in enumerate(nodes):
        if node is None:continue
        payload=node['payload'];width=len(payload)
        if width not in (4,32,64)or node.get('type_word')is None:raise ValueError('Unverified output node')
        n=B+0x10000+256*i;info=n+0xc0;meta=B+0x30000+64*i
        put(array+4*i,n);put(n+0x10,info);put(info,node['type_word']);put(n+0x1c,meta)
        u.mem_write(n+0x34,payload);u.mem_write(n+0x20,struct.pack('<H',node['node_stamp']))
        u.mem_write(meta+0x20,struct.pack('<H',node['metadata_stamp']));active[i]=(n,width)
    saved={a:bytes(u.mem_read(a,4))for a in GLOBALS}
    try:
        for a in GLOBALS:put(a,globals_[a])
        put(stack,stop);u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,p)
        u.emu_start(0x52b3c0,stop,count=1000000)
        if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('Output bridge did not return')
        return {i:dict(payload=bytes(u.mem_read(n+0x34,width)),node_stamp=struct.unpack('<H',u.mem_read(n+0x20,2))[0])for i,(n,width)in active.items()}
    finally:
        for a,data in saved.items():u.mem_write(a,data)
