"""Original native dress support operators; explicit runtime fixtures only."""
import struct,json,random
from pathlib import Path
import numpy as np
from native_leg_ik import u,sha
from evaluate_elsa_head import quat
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
P=0x10001000;META=0x10003000;STACK=0x10018000;STOP=0x10000100

def call(fn,values,layout,count,initial=None):
 u.mem_write(P,b'\0'*512);u.mem_write(META,b'\0'*64);nodes=[0x10004000+256*i for i in range(len(values)+1)]
 ptrs=[n if v is not None else 0 for n,v in zip(nodes,values)]+[nodes[-1]]
 if layout=='array':u.mem_write(P+0x18,struct.pack('<HBB',0x80,len(values),1));u.mem_write(P+0x80,struct.pack('<'+'I'*len(ptrs),*ptrs))
 else:u.mem_write(P+0x18,struct.pack('<'+'I'*len(ptrs),*ptrs))
 for n,v in zip(nodes,values+[initial or ([0,0,0,1] if count==4 else [0]*count)]):
  u.mem_write(n,b'\0'*160);u.mem_write(n+0x10,struct.pack('<I',META));u.mem_write(n+0x1c,struct.pack('<I',META))
  if v is not None:u.mem_write(n+0x34,struct.pack('<'+'f'*len(v),*v))
 for g in [0x21aee78,0x21aee7c,0x213e710,0x213e70c,0x213e490,0x213e48c]:u.mem_write(g,struct.pack('<I',0))
 u.mem_write(STACK,struct.pack('<I',STOP));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,P)
 try:u.emu_start(fn,STOP,count=300000)
 except Exception as ex:raise RuntimeError(hex(u.reg_read(UC_X86_REG_EIP))+' '+str(ex))
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('no return')
 return list(struct.unpack('<'+'f'*count,u.mem_read(nodes[-1]+0x34,4*count)))

def aim(align,reference,up,upref,initial=None):return call(0x534380,[list(align),list(reference),list(up),list(upref),None,None],'array',4,initial)
def inverse_point(v,tr):return call(0x4d57e0,[list(v),list(tr)],'typed',3)
def inverse_vector(v,tr):return call(0x4d46f0,[list(v),list(tr)],'typed',3)
def difference(a,b):return call(0x52d0e0,[list(a),list(b)],'array',3)
if __name__=='__main__':
 rng=random.Random(20261015);errors=[]
 for i in range(100):
  q=np.array([rng.uniform(-1,1) for _ in range(4)]);q/=np.linalg.norm(q);rot=quat(q);scale=rng.uniform(.8,1.2);t=np.array([rng.uniform(-2,2) for _ in range(3)]);v=np.array([rng.uniform(-1,1) for _ in range(3)]);tr=list(q)+list(t)+[scale]+[1]*8
  ep=float(np.max(abs(inverse_point(v,tr)-rot.T@(v-t)/scale)));ev=float(np.max(abs(inverse_vector(v,tr)-rot.T@v/scale)));ed=float(np.max(abs(difference(v,t)-(v-t))));qa=aim(rot[:,2],[0,0,1],rot[:,1],[0,1,0]);ea=float(np.max(abs(quat(qa)-rot)));assert max(ep,ev,ed,ea)<1e-5,(i,ep,ev,ed,ea);errors.append({'point':ep,'vector':ev,'difference':ed,'aim':ea})
 report={'exe_sha256':sha,'cases':len(errors),'max_errors':{k:max(x[k] for x in errors) for k in errors[0]},'scope':'Rigid mixed-axis and positive uniform Transform scales .8..1.2; Aim mapped orthonormal reference pairs, no optional Offset/BasisInput. No degenerate aim validation.','execute':{'AimConstraintProcessorNode':'0x534380','Position3dDifferenceProcessor':'0x52d0e0','InverseTransformPositionWithTransform':'0x4d57e0','InverseTransformVectorWithTransform':'0x4d46f0'}}
 Path('dress-native-math-validation.json').write_text(json.dumps(report,indent=2));print(report)
