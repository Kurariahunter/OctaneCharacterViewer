"""Original Transform compose/point/concatenate helpers. Explicit Scale/Unscale payloads."""
import struct,json,random
from pathlib import Path
import numpy as np
from native_leg_ik import u,sha
from evaluate_elsa_head import quat
from evaluate_elsa_feet import rotor
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
ROOT=Path(__file__).parent
STACK=0x10018000;STOP=0x10000100;PROC=0x10001000;META=0x10003000

def execute(fn,args,this=PROC):
 u.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),STOP,*args));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,this);u.emu_start(fn,STOP,count=200000)
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('no return')
def payload(q,t,scale,unscale):return list(q)+list(t)+[scale[3]]+list(scale)+list(unscale[:3])+[1.0]
def compose(q,t,scale,unscale):
 u.mem_write(PROC,b'\0'*512);u.mem_write(META,b'\0'*64);nodes=[0x10004000+i*256 for i in range(5)];aggregate=nodes[0]
 for n in nodes:
  u.mem_write(n,b'\0'*160);u.mem_write(n+0x1c,struct.pack('<I',META))
 init=payload([0,0,0,1],[0,0,0],[1]*4,[1]*4);u.mem_write(aggregate+0x34,struct.pack('<16f',*init))
 for n,vals in zip(nodes[1:],[t,q,scale,unscale]):u.mem_write(n+0x34,struct.pack('<'+'f'*len(vals),*vals))
 u.mem_write(PROC+0x18,struct.pack('<I',aggregate));u.mem_write(PROC+0x1c,struct.pack('<H',0x80));u.mem_write(PROC+0x80,struct.pack('<4I',*[n|1 for n in nodes[1:]]));execute(0x5303e0,[])
 return list(struct.unpack('<16f',u.mem_read(aggregate+0x34,64)))
def point(state,v):
 out=0x10008000;vin=0x10008100;tr=0x10008200
 u.mem_write(vin,struct.pack('<3f',*v));u.mem_write(tr,struct.pack('<16f',*state));u.mem_write(out,b'\0'*16);execute(0x4c4350,[out,vin,tr]);return np.array(struct.unpack('<3f',u.mem_read(out,12)))
def concat(child,parent):
 out=0x10008000;a=0x10008200;b=0x10008300;u.mem_write(out,b'\0'*64);u.mem_write(a,struct.pack('<16f',*child));u.mem_write(b,struct.pack('<16f',*parent));execute(0x4c2d50,[out,a,b]);return list(struct.unpack('<16f',u.mem_read(out,64)))
if __name__=='__main__':
 rng=random.Random(20261015);errors=[]
 for j in range(100):
  states=[]
  for k in range(2):
   q=np.array([rng.uniform(-1,1) for _ in range(4)]);q/=np.linalg.norm(q);t=[rng.uniform(-1,1) for _ in range(3)];s=[rng.uniform(.8,1.2) for _ in range(4)];us=[rng.uniform(.8,1.2) for _ in range(4)];raw=compose(q,t,s,us);expected=payload(q,t,s,us);err=max(abs(x-y) for x,y in zip(raw,expected));assert err<1e-6;states.append(raw)
   v=np.array([rng.uniform(-1,1) for _ in range(3)]);want=(np.array(t)+quat(q)@(v*np.array(s[:3])*s[3]))*np.array(us[:3]);err2=float(np.max(abs(point(raw,v)-want)));assert err2<2e-6,(j,k,err2,raw,v.tolist(),want.tolist(),point(raw,v).tolist());errors.append({'compose':err,'point':err2})
  c,p=states;out=concat(c,p);r=quat(p[:4])@quat(c[:4]);t=np.array(p[4:7])+quat(p[:4])@(np.array(c[4:7])*np.array(c[12:15])*c[15]*p[7]);expected=payload(rotor(r),t,c[8:12],[1]*4);expected[7]=c[7]*p[7];err=float(np.max(abs(np.r_[quat(out[:4]).flatten()-r.flatten(),np.array(out[4:])-np.array(expected[4:])])));assert err<3e-6;errors[-1]['concat']=err
 report={'exe_sha256':sha,'cases':{'component_compose':200,'point_transform':200,'concatenate':100},'max_error':max(max(v.values()) for v in errors),'scope':'Positive Scale/Unscale/uniform factors 0.8..1.2 with mixed-axis rotors. Original helpers executed. This does not establish which Unscale values a complete skin hierarchy assigns.','compose_execute':'0x5303e0','point_helper':'0x4c4350','concat_helper':'0x4c2d50','payload':'quaternion[4],translation[3],uniform,Scale[4],Unscale[4]; native compose copies Scale.w to uniform and forces Unscale.w=1','rows':errors}
 (ROOT/'transform-scale-native-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='rows'})
