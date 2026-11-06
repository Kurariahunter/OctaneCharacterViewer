"""Offline native PC RelationshipProcessor with file-provided blobs/counts."""
import struct,math
from native_pc_lean_ik import u
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP

def run(blob,values,count,initial_outputs=None,staged=False,output_types=None):
 if len(blob)>0x3000 or len(values)>16 or count>16 or not all(math.isfinite(v)for v in values):raise ValueError('relationship fixture bounds')
 proc=0x10001000;rel=0x10002000;data=0x10004000;meta=0x10003000;stack=0x10018000;stop=0x10000100
 u.mem_write(proc,b'\0'*512);u.mem_write(rel,b'\0'*0x1000);u.mem_write(meta,b'\0'*128);u.mem_write(data,blob);u.mem_write(rel+0x3c,struct.pack('<I',data))
 for off,cache,buf in [(0x50,0x10002200,0x10002500),(0x54,0x10002300,0x10002800)]:
  u.mem_write(cache,b'\0'*128);u.mem_write(cache+0x44,struct.pack('<I',buf));u.mem_write(buf,b'\0'*512);u.mem_write(proc+off,struct.pack('<I',cache))
 u.mem_write(proc+0x58,struct.pack('<I',rel));u.mem_write(proc+0x5c,struct.pack('<HHHHI',len(values),0x80,count,0xc0,0))
 if initial_outputs is not None and (len(initial_outputs)!=count or any(len(row)not in(8,16) or not all(math.isfinite(v)for v in row)for row in initial_outputs)):raise ValueError('invalid relationship initial outputs')
 ins=[0x10008000+i*256 for i in range(len(values))];outs=[0x1000a000+i*256 for i in range(count)]
 u.mem_write(proc+0x80,struct.pack('<'+'I'*len(ins),*ins));u.mem_write(proc+0xc0,struct.pack('<'+'I'*len(outs),*outs))
 for ptr,vals in [(p,[v])for p,v in zip(ins,values)]+[(p,row)for p,row in zip(outs,initial_outputs if initial_outputs is not None else [[0,0,0,1,0,0,0,1]for _ in outs])]:
  u.mem_write(ptr,b'\0'*128);u.mem_write(ptr+0x10,struct.pack('<I',meta));u.mem_write(ptr+0x1c,struct.pack('<I',meta));u.mem_write(ptr+0x34,struct.pack('<'+'f'*len(vals),*vals))
 if output_types is not None:
  if len(output_types)!=count or any(t not in ('Dilation','Transform','Float','Position','Vector','Rotor','Scale','EulerZXY')for t in output_types):raise ValueError('Unsupported relationship output types')
  for address,value in ((0x21aee78,1),(0x21aee7c,0xffffffff),(0x213e48c,2),(0x213e490,0xffffffff),(0x21ae4c8,3),(0x21ae4cc,0xffffffff)):u.mem_write(address,struct.pack('<I',value))
  for ptr,typ in zip(outs,output_types):
   tag={'Dilation':1,'Transform':2}.get(typ,4);tagptr=0x10003200+16*tag;u.mem_write(tagptr,struct.pack('<I',tag));u.mem_write(ptr+0x10,struct.pack('<I',tagptr))
 else:
  for address in (0x21aee78,0x21aee7c,0x213e48c,0x213e490,0x21ae4c8,0x21ae4cc):u.mem_write(address,struct.pack('<I',0))
 u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc)
 try:
  if staged:
   # Original input evaluator followed by the original output-list accessor
   # and output writer. Keep the same explicit cache/output initialization.
   a=0x1000c000;b=0x1000d000;oa=0x1000e000;ob=oa+4
   u.mem_write(a,b'\0'*512);u.mem_write(b,b'\0'*512)
   def invoke(va,args):
    u.mem_write(stack,struct.pack('<'+'I'*(len(args)+1),stop,*args));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc)
    u.emu_start(va,stop,count=1000000)
    if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('relationship stage did not return')
   invoke(0x544e00,[a,b])
   u.reg_write(UC_X86_REG_ECX,rel)
   u.mem_write(stack,struct.pack('<4I',stop,oa,ob,0));u.reg_write(UC_X86_REG_ESP,stack)
   u.emu_start(0x503e00,stop,count=1000000)
   if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('relationship accessor did not return')
   n,ptr=struct.unpack('<II',u.mem_read(oa,8))
   if n>64 or not data<=ptr<data+len(blob):raise ValueError('relationship record bounds')
   invoke(0x53d2b0,[ptr,n,b])
  else:u.emu_start(0x54c9a0,stop,count=1000000)
 except Exception as ex:raise RuntimeError(f'{u.reg_read(UC_X86_REG_EIP):x} {ex}')
 assert u.reg_read(UC_X86_REG_EIP)==stop
 result=[list(struct.unpack('<'+'f'*width,u.mem_read(p+0x34,width*4)))for p,width in zip(outs,[len(row)for row in initial_outputs]if initial_outputs is not None else [8]*len(outs))]
 if not all(math.isfinite(v)for row in result for v in row):raise ValueError('nonfinite relationship')
 return result
