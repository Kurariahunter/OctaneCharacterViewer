"""Isolated original Elsa two-bone leg IK; controlled targets, not recovered clips."""
import sys,struct,json,hashlib,math,random
from pathlib import Path
ROOT=Path(__file__).parent
sys.path.insert(0,'C:/Users/Kurar/.codex/visualizations/2026/09/19/01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1/DI3ConverterValidation/YodaAnimationProbe/analysis_dependencies')
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP
import numpy as np
from evaluate_elsa_head import quat
EXE=Path('F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/DisneyInfinity3.exe');sha=hashlib.sha256(EXE.read_bytes()).hexdigest()
assert sha=='f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705'
pe=pefile.PE(str(EXE));base=pe.OPTIONAL_HEADER.ImageBase;u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image());u.mem_map(0x10000000,0x20000)

from unicorn.x86_const import UC_X86_REG_ECX

from evaluate_elsa_head import DN,get,allnodes,N
from unicorn.x86_const import UC_X86_REG_ECX
def native_ik(values,flags=30):
 if len(values)!=13 or any(not math.isfinite(x) for v in values for x in v):raise ValueError("Invalid IK inputs")
 if flags!=30:raise ValueError("Only authored Elsa flag configuration is validated")
 proc=0x10001000;meta=0x10003000;stack=0x10010000;stop=0x10000100
 u.mem_write(proc,b'\0'*512);u.mem_write(proc+0x18,struct.pack('<HBBB',0x80,13,4,flags));u.mem_write(meta,b'\0'*64)
 values=[values[i] for i in [12,2,1,10,3,8,9,7,6,5,4,0,11]]
 nodes=[0x10004000+i*256 for i in range(17)];u.mem_write(proc+0x80,struct.pack('<17I',*nodes))
 for node,vals in zip(nodes,values+[[0,0,0,1]]*4):
  u.mem_write(node,b'\0'*128);u.mem_write(node+0x1c,struct.pack('<I',meta));u.mem_write(node+0x34,struct.pack('<'+'f'*len(vals),*vals))
 u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc)
 try:u.emu_start(0x53b620,stop,count=500000)
 except Exception as ex:raise RuntimeError(hex(u.reg_read(UC_X86_REG_EIP))+' '+str(ex))
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('no return')
 raw=[list(struct.unpack('<4f',u.mem_read(n+0x34,16))) for n in nodes[13:]]
 return [raw[i] for i in [1,0,3,2]]

def authored_inputs(processor):
 values=[]
 for i in get(processor,'DataNodeRefs')[:13]:
  value=get(DN[i],'Data')
  if value is None:
   # The two authored twist connections start at zero in this isolated test.
   if i not in (676,692):raise ValueError('missing authored input '+str(i))
   value=0.0
  values.append(value if isinstance(value,list) else [value])
 return values
if __name__=='__main__':
 rng=random.Random(20261015);cases=[];neutral=[];frames=[]
 for p in allnodes(N,'ProcessorNode'):
  if get(p,'Type')!='IK2BRPLengthSquashZConstraint':continue
  offset=get(p,'NetworkBufferOffsets')[0];buf=bytes(next(allnodes(N,'NetworkBuffer'))['value']);assert struct.unpack_from('<I',buf,offset)[0]==23
  values=authored_inputs(p);ids=get(p,'DataNodeRefs');a=np.array(values[3]);b=np.array(values[8]);c=np.array(values[9]);l1=float(np.linalg.norm(b-a));l2=float(np.linalg.norm(c-b))
  # Analytic fixture: authored initial ankle and zero pole, not decoded clip targets.
  values[12]=list(c);values[2]=[0,0,0];out=native_ik(values)
  errors=[float(np.max(abs(quat(out[j])-quat(get(DN[ids[13+j]],'Data'))))) for j in range(2)]
  if max(errors)>5e-6:raise AssertionError('neutral rotor mismatch')
  neutral.append({'processor':int(p['value']),'matrix_errors':errors})
  for k in range(100):
   target=c+np.array([rng.uniform(-.07,.07),rng.uniform(-.07,.07),rng.uniform(-.20,-.02)])
   distance=np.linalg.norm(target-a)
   if not abs(l1-l2)+.01<distance<l1+l2-.001:raise ValueError('fixture outside reachable range')
   values[12]=list(target);out=native_ik(values);r1=quat(out[1]);r2=quat(out[0]);mid=a+r1@np.array([0,0,l1]);end=mid+r1@r2@np.array([0,0,l2]);error=float(np.linalg.norm(end-target))
   if not np.isfinite(error) or error>5e-5:raise AssertionError(('endpoint mismatch',error))
   for q in out[:2]:
    if abs(sum(x*x for x in q)-1)>1e-5:raise AssertionError('nonunit output')
   if np.max(abs(np.array(out[2:])-1))>1e-6:raise AssertionError('unexpected reachable scale')
   cases.append({'processor':int(p['value']),'target':list(target),'endpoint':list(end),'endpoint_error':error,'rotations':out[:2]})
  # Four-second controlled bend cycle for a native-solver visualization.
  for k in range(121):
   time=k/30;wave=(1-math.cos(time*math.pi/2))/2;target=c+np.array([.025*math.sin(time*math.pi/2),0,-.18*wave]);values[12]=list(target);out=native_ik(values);r1=quat(out[1]);r2=quat(out[0]);mid=a+r1@np.array([0,0,l1]);end=mid+r1@r2@np.array([0,0,l2]);frames.append({'processor':int(p['value']),'time':time,'start':list(a),'mid':list(mid),'end':list(end),'target':list(target)})
 report={'exe_sha256':sha,'factory':'0x54b880','execute':'0x53b620','network_buffer_value':23,'runtime_flags':30,'input_reorder':[12,2,1,10,3,8,9,7,6,5,4,0,11],'output_reorder':[1,0,3,2],'neutral_tests':neutral,'case_count':len(cases),'max_endpoint_error':max(c['endpoint_error'] for c in cases),'scope':'Original executable solver emulated on both authored leg geometries, using controlled reachable targets and zero pole/twist. Full motion foot-target RelationshipProcessor, other flags, unreachable targets and squash edge cases are NOT validated. Not decoded original clips.','cases':cases}
 (ROOT/'leg-ik-native-validation.json').write_text(json.dumps(report,indent=2));(ROOT/'leg-ik-controlled-demo.json').write_text(json.dumps({'scope':report['scope'],'frames':frames},separators=(',',':')));print({k:report[k] for k in ['case_count','max_endpoint_error','neutral_tests','scope']})

