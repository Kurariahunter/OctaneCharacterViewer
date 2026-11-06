"""Native numeric FloatParameter configuration window and Filter float-array copy window."""
import json,struct,hashlib
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import read,disasm
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ESI,UC_X86_REG_EBX,UC_X86_REG_EIP
B=0x19000000;u.mem_map(B,0x20000);OBJ=B+0x1000;STACK=B+0x18000;SRC=B+0x3000;DST=B+0x6000
configs=[]
for phase in [-1.,0.,.25,1.,2.]:
 for origin in [-2.,0.,1.]:
  for span in [0.,.5,2.]:
   u.mem_write(OBJ,b'\0'*128);u.mem_write(STACK,b'\0'*128);u.mem_write(STACK+0xc,struct.pack('<3f',phase,origin,span));u.reg_write(UC_X86_REG_ESI,OBJ);u.reg_write(UC_X86_REG_ESP,STACK)
   u.emu_start(0x5a20cd,0x5a2113,count=3000)
   if u.reg_read(UC_X86_REG_EIP)!=0x5a2113:raise ValueError('Configuration window boundary')
   actual=struct.unpack('<4f',u.mem_read(OBJ+0x10,16));expected=(origin+span*min(1.,max(0.,phase)),origin,span,phase)
   if actual!=expected:raise ValueError(('FloatParameter config mismatch',actual,expected))
   configs.append(dict(DefaultPhase=phase,RangeStart=origin,RangeSize=span,fields10to1c=actual))
copy_cases=[]
for count in [0,1,3,62,707]:
 values=([0.,.25,1.,-.5,2.]*((count+4)//5))[:count];raw=struct.pack('<'+'f'*count,*values)
 u.mem_write(SRC,b'\xcd'*4096);u.mem_write(DST,b'\x7f'*4096);u.mem_write(SRC,raw);u.mem_write(OBJ,b'\0'*128);u.mem_write(OBJ+0x10,struct.pack('<I',DST));u.mem_write(STACK,b'\0'*128);u.mem_write(STACK+0x20,struct.pack('<I',SRC));u.reg_write(UC_X86_REG_ESI,OBJ);u.reg_write(UC_X86_REG_EBX,count);u.reg_write(UC_X86_REG_ESP,STACK)
 u.emu_start(0x4ce2ad,0x4ce2ca,count=200000)
 if u.reg_read(UC_X86_REG_EIP)!=0x4ce2ca:raise ValueError('Filter copy did not finish')
 if bytes(u.mem_read(DST,len(raw)))!=raw or bytes(u.mem_read(DST+len(raw),16))!=b'\x7f'*16:raise ValueError('Filter copy changed bounds/data')
 copy_cases.append(dict(count=count,bytes_copied=len(raw),preserves_values_without_clamping=True))
report=dict(pass_=True,exe_sha256=sha,config_window=['0x5a20cd','0x5a2113'],config_cases=configs,filter_copy_window=['0x4ce2ad','0x4ce2ca'],filter_cases=copy_cases,scope='Original instruction windows and native calls: name assignment/allocation completed before windows, callback pointer null, destination filter buffer preallocated. Original native memcpy executes without call-result stubs. This establishes float payload copying, not index-to-channel semantics or full filter creation/resolution.')
report['pass']=report.pop('pass_');Path(__file__).with_name('pc-parameter-config-filter-copy-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='config_cases'},indent=2))
