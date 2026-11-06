"""One-row native direct clip-buffer blend; supported field masks only."""
import struct,math
from native_pc_lean_ik import u
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
BASE=0x13000000;u.mem_map(BASE,0x20000)
def apply_layer(base_fields,delta_fields,mask,weight=1.,additive=True):
 if mask&~0x177 or not 0<=weight<=1:raise ValueError('unsupported blend mask/weight')
 mgr=BASE+0x1000;table=BASE+0x2000;dst=BASE+0x3000;src=BASE+0x4000;stack=BASE+0x18000;stop=BASE+0x100
 u.mem_write(BASE,b'\0'*0x20000)
 def put(a,v):u.mem_write(a,struct.pack('<I',v))
 def scales(f):
  s=f.get("Scale",[1]*4)
  return [float(s)]*4 if isinstance(s,(int,float))else list(s)
 def pack(f):
  v=list(f.get('Translation',[0,0,0]))+[0.]+scales(f)[:3]+[0.]+list(f.get('Orientation',[0,0,0,1]))
  if len(v)!=12 or not all(math.isfinite(x)for x in v):raise ValueError('bad clip buffer fields')
  return struct.pack('<12f',*v)
 u.mem_write(dst,pack(base_fields));u.mem_write(src,pack(delta_fields));put(src+0x30,mask);put(mgr,1);put(mgr+8,table);put(table+4,dst);put(table+20,src);put(table+24,1)
 u.mem_write(stack,struct.pack('<IfII',stop,weight,0 if additive else 1,0));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,mgr);u.emu_start(0x5a14d0,stop,count=100000)
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('blend did not return')
 v=list(struct.unpack('<12f',u.mem_read(dst,48)));assert all(math.isfinite(x)for x in v)
 return dict(Translation=v[:3],Scale=v[4:7]+[scales(base_fields)[3]],Orientation=v[8:12])
