"""Original Elsa foot relationship math harness; initialized source fixture only."""
import struct,json,math
from pathlib import Path
from native_leg_ik import u,DN,get,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
ROOT=Path(__file__).parent
PROC=0x10001000;REL=0x10002000;BLOB=0x10004000;META=0x10003000;STACK=0x10018000;STOP=0x10000100
raw=bytes.fromhex(get(DN[39],'RelationshipDataBlock')['hex'])
def invoke(va,args):
 u.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),STOP,*args));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,PROC)
 try:u.emu_start(va,STOP,count=1000000)
 except Exception as ex:raise RuntimeError(hex(u.reg_read(UC_X86_REG_EIP))+' '+str(ex))
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('processor did not return')
def run(values,full=False):
 if len(values)!=4 or not all(math.isfinite(x) for x in values):raise ValueError('four finite float inputs required')
 u.mem_write(PROC,b'\0'*512);u.mem_write(REL,b'\0'*128);u.mem_write(BLOB,raw);u.mem_write(REL+0x3c,struct.pack('<I',BLOB));u.mem_write(META,b'\0'*64)
 for off,cache,buf in [(0x50,0x10002200,0x10002400),(0x54,0x10002300,0x10002500)]:
  u.mem_write(cache,b'\0'*128);u.mem_write(cache+0x44,struct.pack('<I',buf));u.mem_write(buf,b'\0'*16);u.mem_write(PROC+off,struct.pack('<I',cache))
 u.mem_write(PROC+0x58,struct.pack('<I',REL));u.mem_write(PROC+0x5c,struct.pack('<HHHHI',4,0x80,4,0x90,0))
 ins=[0x10005000+i*256 for i in range(4)];outs=[0x10006000+i*256 for i in range(4)]
 u.mem_write(PROC+0x80,struct.pack('<4I',*ins));u.mem_write(PROC+0x90,struct.pack('<4I',*outs))
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
 if not full:invoke(0x53d2b0,[BLOB+284,4,b])
 result=[list(struct.unpack('<8f',u.mem_read(n+0x34,32))) for n in outs]
 if not all(math.isfinite(x) for row in result for x in row):raise ValueError('nonfinite relationship output')
 return {'inputs':values,'intermediate':intermediate if not full else None,'outputs':result,'cache_u16':[list(struct.unpack('<4H',u.mem_read(x,8))) for x in [0x10002400,0x10002500]],'full_runtime':full}

if __name__=='__main__':
 import random
 baseline=run([0,0,0,0]);rows=[];rng=random.Random(20261015)
 fixtures=[[0,0,0,0]]
 for axis in range(4):
  for value in [-100,-75,-25,0,25,75,100]:
   v=[0,0,0,0];v[axis]=value;fixtures.append(v)
 fixtures += [[rng.uniform(-100,100) for _ in range(4)] for j in range(40)]
 max_angle_error=0;max_crosstalk=0;max_stage_error=0
 for values in fixtures:
  staged=run(values);full=run(values,full=True);err=max(abs(x-y) for a,b in zip(staged['outputs'],full['outputs']) for x,y in zip(a,b));max_stage_error=max(max_stage_error,err)
  if err>1e-7:raise AssertionError('full vs stage mismatch')
  for axis,row in enumerate(full['outputs']):
   q=row[:4]
   if abs(sum(v*v for v in q)-1)>1e-5 or max(abs(x) for x in q[1:3])>1e-6 or max(abs(x) for x in row[4:7])>1e-6 or abs(row[7]-1)>1e-6:raise AssertionError('invalid axis/translation/scale')
   # Ideal percent-like linear response is only a comparison; quantized source is authoritative.
   expected=(1 if axis%2==0 else -1)*values[axis]*math.pi/200
   actual=-2*math.atan2(q[0],q[3]);max_angle_error=max(max_angle_error,abs(actual-expected))
   if values[axis]==0:
    delta=max(abs(x-y) for x,y in zip(row,baseline['outputs'][axis]));max_crosstalk=max(max_crosstalk,delta)
    if delta>1e-7:raise AssertionError('unrelated control changed')
  rows.append(full)
 report={'exe_sha256':sha,'blob_sha256':__import__('hashlib').sha256(raw).hexdigest(),'scope':'Full original RelationshipProcessor0x54c9a0 vs staged input/output routines on the shared Elsa foot blob, scalar inputs[-100,100], zero-initialized segment caches, identity dilation outputs and explicit minimal dilation type selection. Not original clip playback; no persistent-cache or other relationship types validation.','cases':len(rows),'max_full_vs_staged_error':max_stage_error,'max_unrelated_output_change':max_crosstalk,'max_angle_difference_from_ideal_linear_radians':max_angle_error,'neutral_max_quaternion_xyz':max(abs(x) for a in baseline['outputs'] for x in a[:3]),'rows':rows}
 (ROOT/'foot-relationship-native-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='rows'})
