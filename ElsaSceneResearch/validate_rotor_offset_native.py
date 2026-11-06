"""Isolated original CommonBasisArrayProcessor<UnitRotor3d,OffsetPolicy> test."""
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
def native(a,b):
 proc=0x10001000;na=0x10002000;nb=0x10002100;out=0x10002200;metadata=0x10003000;stack=0x10010000;stop=0x10000100
 u.mem_write(proc,b'\0'*256);u.mem_write(proc+0x18,struct.pack('<HBB',0x40,2,1));u.mem_write(proc+0x40,struct.pack('<III',na,nb,out))
 u.mem_write(metadata,b'\0'*64)
 for node,q in [(na,a),(nb,b),(out,[0,0,0,0])]:
  u.mem_write(node,b'\0'*128);u.mem_write(node+0x1c,struct.pack('<I',metadata));u.mem_write(node+0x34,struct.pack('<4f',*q))
 u.mem_write(stack,struct.pack('<III',stop,proc,0));u.reg_write(UC_X86_REG_ESP,stack)
 u.emu_start(0x4bd400,stop,count=20000)
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('processor did not return')
 return list(struct.unpack('<4f',u.mem_read(out+0x34,16)))
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def unit(q):
 n=math.sqrt(sum(x*x for x in q));return list(struct.unpack('<4f',struct.pack('<4f',*[x/n for x in q])))
rng=random.Random(20261014);cases=[]
inputs=[([.3,-.4,.1,.8],[-.2,.15,.6,.7]),([1,0,0,0],[0,0,1,0]),([0,0,0,1],[.2,.3,.4,.5])]
inputs += [([rng.uniform(-1,1) for _ in range(4)],[rng.uniform(-1,1) for _ in range(4)]) for i in range(100)]
for a,b in inputs:
 a=unit(a);b=unit(b);q=native(a,b);expected=mul(b,a);opposite=mul(a,b)
 err=max(abs(x-y) for x,y in zip(q,expected));wrong=max(abs(x-y) for x,y in zip(q,opposite));m=quat(q);right=float(np.max(np.abs(m-quat(a)@quat(b))));left=float(np.max(np.abs(m-quat(b)@quat(a))))
 if err>2e-6 or right>2e-6 or not all(math.isfinite(x) for x in q):raise AssertionError('native mismatch')
 cases.append({'input_slot_0':a,'input_slot_1':b,'native_output':q,'slot1_hamilton_slot0_error':err,'slot0_hamilton_slot1_error':wrong,'source_matrix_input_then_offset_error':right,'source_matrix_offset_then_input_error':left})
report={'exe_sha256':sha,'factory_va':'0x4F2FF0','rtti_vtable_va':'0x1B2D3AC','vtable_execute_slot':16,'thunk_va':'0x4C18B0','runtime_va':'0x4BD400','formula':'Hamilton quaternion: output = slot1 * slot0; under the project transposed source quaternion-matrix convention, M_out = M_slot0 @ M_slot1.','interpretation':'Authored Elsa processor DataNodeAttributes list Input then Offset then Output. This selects the diagnostic OffsetRight candidate.','max_quaternion_error':max(x['slot1_hamilton_slot0_error'] for x in cases),'max_matrix_error':max(x['source_matrix_input_then_offset_error'] for x in cases),'discriminating_cases':sum(x['source_matrix_offset_then_input_error']>0.01 for x in cases),'case_count':len(cases),'cases':cases,'scope':'Direct isolated processor execution with two operand slots and one output. Does not validate bind-relative retargeting or remaining graph operators.'}
(ROOT/'rotor-offset-native-validation.json').write_text(json.dumps(report,indent=2));print({k:report[k] for k in ['case_count','max_quaternion_error','max_matrix_error','discriminating_cases','interpretation']})
