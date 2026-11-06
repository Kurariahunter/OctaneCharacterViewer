"""Native source-mode normalization -> track copy -> direct clip-buffer dispatch.
Tests specific instruction windows; not whole game loader or actor scheduling.
"""
import struct,json,math
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
from probe_pc_blend_order import qaxis,mul,err
BASE=0x12000000;u.mem_map(BASE,0x20000);SOURCE=BASE+0x1000;TRACK=BASE+0x2000;MGR=BASE+0x3000;TABLE=BASE+0x4000;DST=BASE+0x5000;SRC=BASE+0x6000;STACK=BASE+0x18000;STOP=BASE+0x100

def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def run(a,z):
 u.emu_start(a,z,count=100000)
 assert u.reg_read(UC_X86_REG_EIP)==z

def native_case(mode,weight,b,d):
 u.mem_write(BASE,b'\0'*0x20000);u.reg_write(UC_X86_REG_ESP,STACK)
 # Original normalization: raw accepted ESI -> EAX boolean -> [EDI+8].
 u.reg_write(UC_X86_REG_ESI,mode&0xffffffff);u.reg_write(UC_X86_REG_EDI,SOURCE);run(0x7807d4,0x7807e2)
 # Original base-track clone field copy.
 u.reg_write(UC_X86_REG_ESI,TRACK);u.reg_write(UC_X86_REG_EDI,SOURCE);run(0x5a261a,0x5a2620)
 mode_copied=struct.unpack('<I',u.mem_read(TRACK+8,4))[0]
 # One destination row and one source row, both fully authored TRS masks.
 t=[1.,2.,3.];dt=[.4,-.3,.2];sc=[2.,3.,4.];ds=[1.2,.8,1.5]
 for ptr,q,tr,s in [(DST,b,t,sc),(SRC,d,dt,ds)]:
  u.mem_write(ptr,struct.pack('<12f',*(tr+[0.]+s+[0.]+q)));put(ptr+0x30,0x177)
 put(MGR,1);put(MGR+8,TABLE);put(TABLE+4,DST);put(TABLE+16+4,SRC);put(TABLE+16+8,1)
 u.mem_write(STACK+0x28,struct.pack('<f',weight));u.reg_write(UC_X86_REG_ESI,TRACK);u.reg_write(UC_X86_REG_EDI,MGR);u.reg_write(UC_X86_REG_ESP,STACK)
 visited=[]
 def hook(uc,a,size,data):
  if a in (0x5a14d0,0x59f3e0,0x5a00d0):visited.append(hex(a))
 h=u.hook_add(UC_HOOK_CODE,hook)
 try:run(0x5a15f4,0x5a1616)
 finally:u.hook_del(h)
 out=list(struct.unpack('<12f',u.mem_read(DST,48)));assert all(math.isfinite(x)for x in out)
 return dict(raw_mode=mode,normalized_mode=mode_copied,weight=weight,visited=visited,translation=out[:3],scale=out[4:7],rotor=out[8:12],remaining_depth=struct.unpack('<I',u.mem_read(MGR,4))[0])

def main():
 rows=[]
 for mode in (0,1,2,-1):
  for w in (0.,.25,.5,1.):
   b=mul(qaxis(0,37),qaxis(2,-21));d=mul(qaxis(1,43),qaxis(0,-17));r=native_case(mode,w,b,d)
   route='0x59f3e0'if mode==0 else'0x5a00d0';assert route in r['visited']and r['remaining_depth']==0
   if mode==0:
    q=[(1-w)*a+w*z for a,z in zip(b,d)];wanted_t=[a+(z-a)*w for a,z in zip([1,2,3],[.4,-.3,.2])];wanted_s=[a+(z-a)*w for a,z in zip([2,3,4],[1.2,.8,1.5])]
   else:
    q0=mul(d,b);q=[(1-w)*a+w*z for a,z in zip(b,q0)];wanted_t=[a+z*w for a,z in zip([1,2,3],[.4,-.3,.2])];wanted_s=[a*(1+w*(z-1))for a,z in zip([2,3,4],[1.2,.8,1.5])]
   n=math.sqrt(sum(a*a for a in q));q=[a/n for a in q]
   r['candidate_rotor_error']=err(r['rotor'],q);r['translation_error']=max(abs(a-z)for a,z in zip(r['translation'],wanted_t));r['scale_error']=max(abs(a-z)for a,z in zip(r['scale'],wanted_s));rows.append(r)
 report=dict(exe_sha256=sha,cases=len(rows),max_candidate_rotor_error=max(x['candidate_rotor_error']for x in rows),max_translation_error=max(x['translation_error']for x in rows),max_scale_error=max(x['scale_error']for x in rows),rows=rows,scope='Normalization/copy/child-dispatch instruction windows with pre-evaluated one-row buffers. No complete parser, parent scheduling, masked mapping, or live actor proof. Source buffer additive rotation delta*base, then shortest-sign normalized interpolation from base; positive-dot controlled cases only.')
 assert report['max_candidate_rotor_error']<2e-6 and report['max_translation_error']<2e-6 and report['max_scale_error']<2e-6
 Path(__file__).with_name('pc-source-mode-dispatch-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='rows'})

if __name__=="__main__":main()
