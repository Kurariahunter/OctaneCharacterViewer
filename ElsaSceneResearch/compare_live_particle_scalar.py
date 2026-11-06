"""Compare only the captured +0x98 scalar; preserve source fixtures and prior bakes."""
import json,struct,math
from pathlib import Path
import numpy as np
from native_dynamic_chain_fixture import make,invoke,positions,u,BASE,sha
R=Path(__file__).parent
results=[]
for synthetic in [False]:
 runs=[]
 for value in [1.0,.5]:
  ins,outs=make(orientation=[0,0,0,1]);u.mem_write(ins[2]+0x34,struct.pack('<I',0xfffffffe))
  for slot in [9,14]:u.mem_write(ins[slot]+0x98,struct.pack('<f',value))
  if synthetic:u.mem_write(ins[14]+0x90,struct.pack('<I',7))
  frames=[]
  for frame in range(120):
   t=frame/30;anchor=[0,0,0,1,.03*math.sin(t*2),0,0,1];container=anchor.copy();container[6]=.3010336757
   u.mem_write(ins[0]+0x34,struct.pack('<I',frame));u.mem_write(ins[1]+0x34,struct.pack('<f',1/30));u.mem_write(ins[5]+0x34,struct.pack('<8f',*anchor));u.mem_write(ins[6]+0x34,struct.pack('<8f',*container));u.mem_write(ins[11]+0x34,struct.pack('<3f',anchor[4],0,.01));invoke(0x4ae360)
   p=np.array(positions(outs));assert np.isfinite(p).all();frames.append(p.tolist())
  runs.append(frames)
 err=float(np.max(abs(np.array(runs[0])-runs[1])));results.append({'synthetic_tip_flag7':synthetic,'max_position_difference':err,'reset_difference':float(np.max(abs(np.array(runs[0][0])-runs[1][0])))})
 print('MOVING',synthetic,err,flush=True)
# Positive control: unmodified arithmetic block with explicit nonzero inputs.
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_XMM1,UC_X86_REG_XMM2,UC_X86_REG_XMM4,UC_X86_REG_XMM5,UC_X86_REG_XMM6,UC_X86_REG_XMM7
pack=lambda x:int.from_bytes(struct.pack('<f',x)+bytes(12),'little')
unpack=lambda x:struct.unpack('<f',int(x).to_bytes(16,'little')[:4])[0]
positive=[]
for value in [1.,.5]:
 u.mem_write(BASE+0x1000+0x98,struct.pack('<f',value));stack=BASE+0x1e000
 u.mem_write(stack+0x90,struct.pack('<f',1));u.mem_write(stack+0xa4,struct.pack('<f',1));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EAX,BASE+0x1000)
 for reg,x in [(UC_X86_REG_XMM1,2),(UC_X86_REG_XMM2,3),(UC_X86_REG_XMM4,0),(UC_X86_REG_XMM5,0),(UC_X86_REG_XMM6,0),(UC_X86_REG_XMM7,0)]:u.reg_write(reg,pack(x))
 u.emu_start(0x4a21ef,0x4a222b,count=100)
 positive.append([unpack(u.reg_read(reg)) for reg in [UC_X86_REG_XMM4,UC_X86_REG_XMM5,UC_X86_REG_XMM6]])
assert positive==[[2.,3.,1.],[1.,1.5,.5]],positive
# Execute unchanged sampler mechanics with an explicit constructor wrapper in a separate namespace.
src=(R/'sample_knee_dynamic_dress.py').read_text()
for value,label in [(1.0,'slot98_1'),(.5,'slot98_05')]:
 wrapper=f'''original_make=make
def make(*args,**kwargs):
 ins,outs=original_make(*args,**kwargs)
 for slot in [9,14]:u.mem_write(ins[slot]+0x98,struct.pack('<f',{value}))
 return ins,outs
'''
 code=src.replace('R=Path(__file__).parent;',wrapper+'\nR=Path(__file__).parent;').replace('native-knee-dynamic-dress-samples.json',f'native-dress-{label}-samples.json').replace('Particle scalar slot98 kept at original constructor default1.',f'Controlled slot98={value}; not a universal default claim.')
 exec(compile(code,'slot98_sampler_'+label,'exec'),{'__file__':str(R/'sample_knee_dynamic_dress.py'),'__name__':'slot98_comparison'})
a=json.loads((R/'native-dress-slot98_1-samples.json').read_text());b=json.loads((R/'native-dress-slot98_05-samples.json').read_text());clips=[]
for ca,cb in zip(a['clips'],b['clips']):
 maxpos=maxmat=0
 assert ca['name']==cb['name'] and len(ca['samples'])==len(cb['samples'])
 for fa,fb in zip(ca['samples'],cb['samples']):
  assert fa['time']==fb['time']
  for xa,xb in zip(fa['chains'],fb['chains']):maxpos=max(maxpos,float(np.max(abs(np.array(xa['positions'])-xb['positions']))))
  for key in fa['worlds']:maxmat=max(maxmat,float(np.max(abs(np.array(fa['worlds'][key])-fb['worlds'][key]))))
 clips.append({'clip':ca['name'],'frames':len(ca['samples']),'max_position_difference':maxpos,'max_skin_matrix_difference':maxmat})
 print('SOURCE',clips[-1],flush=True)
assert results[0]['max_position_difference']==0
assert positive[0]!=positive[1]
assert all(c['max_position_difference']==0 and c['max_skin_matrix_difference']==0 for c in clips)
old=json.loads((R/'native-knee-dynamic-dress-samples.json').read_text());baseline=max(float(np.max(abs(np.array(f['worlds'][key])-g['worlds'][key]))) for c,d in zip(old['clips'],a['clips']) for f,g in zip(c['samples'],d['samples']) for key in f['worlds']);assert baseline<1e-7
report={'exe_sha256':sha,'scope':'Isolated native routines, source root flags5/tip6, existing bounded graph feedback/zero force. Arithmetic-block sensitivity test is separate from full source configurations.','values_compared':[1,.5],'moving_anchor_fixtures':results,'arithmetic_block_positive_control':{'range':['0x4a21ef','0x4a222b'],'outputs':positive},'source_clips':clips,'baseline_reproduction_matrix_error':baseline,'interpretation':'Slot98 change has no effect in these source dress fixtures. Native read at0x4a21ef is guarded by config flag bit0; tip6 lacks that bit and root5 is constrained. An unmodified arithmetic-block positive control demonstrates sensitivity to slot98 when that block receives nonzero inputs. Does not establish universal parameter semantics or all force/collision behavior.'}
(R/'slot98-native-comparison.json').write_text(json.dumps(report,indent=2));print('PASS',flush=True)
