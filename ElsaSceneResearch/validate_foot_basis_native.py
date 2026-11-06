"""Executable-backed unit-scale foot basis fixtures; not universal transform support."""
import json,math,random,struct
from pathlib import Path
import numpy as np
from native_leg_ik import u,sha
from evaluate_elsa_head import quat
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
ROOT=Path(__file__).parent
SPECS={'TransformPositionWithDilation':(0x4d4b40,'typed',3),'TransformDilationWithTransform':(0x4d78d0,'typed',8),'ConcatenateInverseTransformDilation':(0x4d1220,'array',16),'InvertConcatenateChainTransform':(0x4d2540,'array',16),'Position3dOffsetProcessor':(0x4c18a0,'array',3),'FloatNegate':(0x52d5c0,'unary',1)}
def native(name,a,b=None):
 fn,layout,count=SPECS[name];proc=0x10001000;meta=0x10003000;stack=0x10018000;stop=0x10000100;nodes=[0x10002000,0x10002200,0x10002400]
 u.mem_write(proc,b'\0'*512);u.mem_write(meta,b'\0'*64)
 if layout=='typed':u.mem_write(proc+0x18,struct.pack('<III',*nodes))
 else:
  n=1 if layout=='unary' else 2;u.mem_write(proc+0x18,struct.pack('<HBB',0x80,n,1));u.mem_write(proc+0x80,struct.pack('<'+'I'*(n+1),*(nodes[:n]+[nodes[2]])))
 for node,val in zip(nodes,[a,b or [0],([0,0,0,1,0,0,0,1]+[1]*8)[:max(count,8)]]):
  u.mem_write(node,b'\0'*160);u.mem_write(node+0x10,struct.pack('<I',meta));u.mem_write(node+0x1c,struct.pack('<I',meta));u.mem_write(node+0x34,struct.pack('<'+'f'*len(val),*val))
 for ptr in [0x21aee78,0x21aee7c,0x213e70c,0x213e710,0x213e48c,0x213e490]:u.mem_write(ptr,struct.pack('<I',0))
 u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc)
 try:u.emu_start(fn,stop,count=200000)
 except Exception as ex:raise RuntimeError(name+' '+hex(u.reg_read(UC_X86_REG_EIP))+' '+str(ex))
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('no return '+name)
 return list(struct.unpack('<'+'f'*count,u.mem_read(nodes[2]+0x34,count*4)))
def matrix(a):
 m=np.eye(4);m[:3,:3]=quat(a[:4])*a[7];m[:3,3]=a[4:7];return m
if __name__=='__main__':
 rng=random.Random(20261015);rows=[]
 for j in range(60):
  vals=[]
  for k in range(2):
   q=np.array([rng.uniform(-1,1) for _ in range(4)]);q/=np.linalg.norm(q);vals.append(list(q)+[rng.uniform(-1,1) for _ in range(3)]+[1])
  a,b=vals;A=matrix(a);B=matrix(b);point=[rng.uniform(-1,1) for _ in range(3)]
  for name in SPECS:
   if name=='TransformPositionWithDilation':actual=np.array(native(name,point,b));expected=(B@np.array(point+[1]))[:3]
   elif name=='TransformDilationWithTransform':actual=matrix(native(name,a,b+[1]*8));expected=B@A
   elif name=='ConcatenateInverseTransformDilation':actual=matrix(native(name,a+[1]*8,b));expected=np.linalg.inv(B)@A
   elif name=='InvertConcatenateChainTransform':actual=matrix(native(name,a+[1]*8,b+[1]*8));expected=np.linalg.inv(A)@np.linalg.inv(B)
   elif name=='Position3dOffsetProcessor':actual=np.array(native(name,point,b[4:7]));expected=np.array(point)+b[4:7]
   else:actual=np.array(native(name,[point[0]]));expected=np.array([-point[0]])
   error=float(np.max(abs(actual-expected)))
   if error>1e-5:raise AssertionError((name,j,error,actual.tolist(),expected.tolist()))
   rows.append({'operator':name,'case':j,'error':error})
 report={'exe_sha256':sha,'scope':'All scale components fixed to 1; random rigid transforms and positions. Original runtime fixture type predicates selected explicitly; no loader validation. Other scales unvalidated.','cases':len(rows),'operators':{n:{'execute':hex(v[0]),'cases':sum(r['operator']==n for r in rows),'max_error':max(r['error'] for r in rows if r['operator']==n)} for n,v in SPECS.items()},'formulas':{'TransformPositionWithDilation':'converter @ homogeneous point','TransformDilationWithTransform':'converter @ input (unit scales only)','ConcatenateInverseTransformDilation':'inverse(Right) @ Left (unit scales only)','InvertConcatenateChainTransform':'inverse(Input0) @ inverse(Input1), order preserved','Position3dOffsetProcessor':'Input + Offset','FloatNegate':'-Input'},'rows':rows}
 (ROOT/'foot-basis-native-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='rows'})
