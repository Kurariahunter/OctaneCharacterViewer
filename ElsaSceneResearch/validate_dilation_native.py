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

from unicorn.x86_const import UC_X86_REG_ECX
def native(a,b):
 proc=0x10001000;na=0x10002000;nb=0x10002100;out=0x10002200;meta=0x10003000;stack=0x10010000;stop=0x10000100
 u.mem_write(proc,b'\0'*256);u.mem_write(proc+0x18,struct.pack('<III',na,nb,out));u.mem_write(meta,b'\0'*64)
 for node,data in [(na,a),(nb,b),(out,[0,0,0,1,0,0,0,1])]:
  u.mem_write(node,b'\0'*128);u.mem_write(node+0x10,struct.pack('<I',meta));u.mem_write(node+0x1c,struct.pack('<I',meta));u.mem_write(node+0x34,struct.pack('<8f',*data))
 u.mem_write(0x21aee78,struct.pack('<I',0));u.mem_write(0x21aee7c,struct.pack('<I',0))
 u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc)
 u.emu_start(0x4d7440,stop,count=20000)
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('no return')
 return list(struct.unpack('<8f',u.mem_read(out+0x34,32)))
def matrix(a):
 m=np.eye(4);m[:3,:3]=quat(a[:4])*a[7];m[:3,3]=a[4:7];return m

if __name__=='__main__':
 rng=random.Random(20261015);cases=[]
 for i in range(100):
  vals=[]
  for j in range(2):
   q=np.array([rng.uniform(-1,1) for k in range(4)]);q/=np.linalg.norm(q)
   vals.append(list(q)+[rng.uniform(-2,2) for k in range(3)]+[rng.uniform(.5,2)])
  a,b=vals;o=native(a,b);expected=matrix(b)@matrix(a);err=float(np.max(abs(matrix(o)-expected)))
  if err>1e-5:raise ValueError(('native mismatch',err))
  cases.append(err)
 report={'exe_sha256':sha,'factory':'0x4d70c0','constructor':'0x4b74e0','vtable':'0x1b2ca74','execute':'0x4d7440','formula':'Moutput = Mconverter @ Minput, with transposed source quaternion matrices','cases':len(cases),'max_error':max(cases),'scope':'Isolated original processor execution including rotations, translations and positive uniform scales; no game launched.'}
 (ROOT/'dilation-native-validation.json').write_text(json.dumps(report,indent=2));print(report)
