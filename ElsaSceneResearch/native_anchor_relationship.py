"""Original Elsa foot relationship math harness; initialized source fixture only."""
import struct,json,math
from pathlib import Path
from native_leg_ik import u,DN,get,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
ROOT=Path(__file__).parent
PROC=0x10001000;REL=0x10002000;BLOB=0x10004000;META=0x10003000;STACK=0x10018000;STOP=0x10000100
raw=bytes.fromhex(get(DN[23],'RelationshipDataBlock')['hex'])
def invoke(va,args):
 u.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),STOP,*args));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,PROC)
 try:u.emu_start(va,STOP,count=1000000)
 except Exception as ex:raise RuntimeError(hex(u.reg_read(UC_X86_REG_EIP))+' '+str(ex))
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('processor did not return')
def run(values,full=True):
 if len(values)!=2 or not all(math.isfinite(x) for x in values):raise ValueError('two finite float inputs required')
 u.mem_write(PROC,b'\0'*512);u.mem_write(REL,b'\0'*128);u.mem_write(BLOB,raw);u.mem_write(REL+0x3c,struct.pack('<I',BLOB));u.mem_write(META,b'\0'*64)
 for off,cache,buf in [(0x50,0x10002200,0x10002400),(0x54,0x10002300,0x10002500)]:
  u.mem_write(cache,b'\0'*128);u.mem_write(cache+0x44,struct.pack('<I',buf));u.mem_write(buf,b'\0'*16);u.mem_write(PROC+off,struct.pack('<I',cache))
 u.mem_write(PROC+0x58,struct.pack('<I',REL));u.mem_write(PROC+0x5c,struct.pack('<HHHHI',2,0x80,1,0x90,0))
 ins=[0x10005000+i*256 for i in range(2)];outs=[0x10006000+i*256 for i in range(1)]
 u.mem_write(PROC+0x80,struct.pack('<2I',*ins));u.mem_write(PROC+0x90,struct.pack('<1I',*outs))
 for node,v in zip(ins,values):
  u.mem_write(node,b'\0'*128);u.mem_write(node+0x1c,struct.pack('<I',META));u.mem_write(node+0x34,struct.pack('<f',v))
 for node in outs:
  u.mem_write(node,b'\0'*128);u.mem_write(node+0x10,struct.pack('<I',META));u.mem_write(node+0x1c,struct.pack('<I',META));u.mem_write(node+0x34,struct.pack('<8f',0,0,0,1,0,0,0,1))
 # Satisfy only the observed dilation type check; no unrelated type-family guesses.
 u.mem_write(0x21aee78,struct.pack('<I',0));u.mem_write(0x21aee7c,struct.pack('<I',0))
 a=0x10008000;b=0x10009000;u.mem_write(a,b'\0'*256);u.mem_write(b,b'\0'*256)
 if full:invoke(0x54c9a0,[])
 else:invoke(0x544e00,[a,b])
 intermediate=[list(struct.unpack('<4f',u.mem_read(x,16))) for x in [a,b]]
 # Native record accessor verified in probe_foot_relationship.py: offset284,count4.
 if not full:
  stride=struct.unpack_from('<I',raw,8)[0];h=stride+struct.unpack_from('<I',raw,stride+0x14)[0];n=struct.unpack_from('<H',raw,h+2)[0];count=struct.unpack_from('<H',raw,h+n*2+6)[0];offset=h+n*2+8
  invoke(0x53d2b0,[BLOB+offset,count,b])
 result=[list(struct.unpack('<8f',u.mem_read(n+0x34,32))) for n in outs]
 if not all(math.isfinite(x) for row in result for x in row):raise ValueError('nonfinite relationship output')
 return {'inputs':values,'intermediate':intermediate if not full else None,'outputs':result,'cache_u16':[list(struct.unpack('<4H',u.mem_read(x,8))) for x in [0x10002400,0x10002500]],'full_runtime':full}


if __name__=='__main__':
 import random,hashlib
 rng=random.Random(17)
 fixtures=[[0,0]]+[[v,0] for v in [-100,-50,50,100]]+[[0,v] for v in [-100,-50,50,100]]+[[rng.uniform(-100,100),rng.uniform(-100,100)] for _ in range(100)]
 rows=[]
 for values in fixtures:
  a=run(values,True)['outputs'][0];b=run(values,False)['outputs'][0];e=max(abs(x-y) for x,y in zip(a,b))
  assert e<1e-7 and a[:7]==[0,0,0,1,0,0,0] and a[7]>0
  rows.append({'inputs':values,'scale':a[7],'stage_error':e})
 report={'exe_sha256':sha,'blob_sha256':hashlib.sha256(raw).hexdigest(),'processor':17,'output_node':4,'cases':len(rows),'max_full_vs_stage_error':max(x['stage_error'] for x in rows),'scope':'Two scalar inputs, identity-initialized Dilation output, zero caches. Native full versus staged calls; not loader or persistent-cache validation.','rows':rows}
 (ROOT/'anchor-relationship-native-validation.json').write_text(json.dumps(report,indent=2))
 print({k:v for k,v in report.items() if k!='rows'})
