"""Bounded native constructor-field initialization and constant track-weight getter."""
import struct,json
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP
BASE=0x15000000;u.mem_map(BASE,0x10000);TRACK=BASE+0x1000;STACK=BASE+0x8000;STOP=BASE+0x100;OUT=BASE+0x200
u.mem_write(TRACK,b'\x7f'*128);u.reg_write(UC_X86_REG_ECX,TRACK);u.reg_write(UC_X86_REG_ESP,STACK)
u.emu_start(0x5a2260,0x5a228f,count=1000)
if u.reg_read(UC_X86_REG_EIP)!=0x5a228f:raise ValueError('constructor window boundary')
mode,expression=struct.unpack('<II',u.mem_read(TRACK+8,8));weight,time=struct.unpack('<ff',u.mem_read(TRACK+0x10,8))
if (mode,expression,weight,time)!=(0,0,1.,0.):raise ValueError('constructor defaults mismatch')
rows=[]
for expected in [-1.,0.,.25,.5,1.,2.]:
 u.mem_write(TRACK+0xc,struct.pack('<If',0,expected));u.mem_write(STACK,struct.pack('<I',STOP));u.reg_write(UC_X86_REG_ECX,TRACK);u.reg_write(UC_X86_REG_ESP,STACK)
 u.emu_start(0x59d500,STOP,count=1000)
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('getter did not return')
 u.mem_write(STOP,b'\xd9\x1d'+struct.pack('<I',OUT));u.emu_start(STOP,STOP+6,count=5)
 actual=struct.unpack('<f',u.mem_read(OUT,4))[0]
 if actual!=expected:raise ValueError('getter mismatch')
 rows.append({'stored_weight':expected,'returned_weight':actual})
report={'exe_sha256':sha,'scope':'Original base constructor instruction window before nested member constructor; full constant-weight getter with expression pointer null. Not full loader/state-machine validation.','constructor_fields':{'mode':mode,'expression_pointer':expression,'constant_weight':weight,'time_offset':time},'constructor_window':['0x5a2260','0x5a228f'],'getter':'0x59d500','cases':rows,'unresolved':'Expression-backed weights, numeric property parsing and identified actor active layer values are not exercised.'}
Path(__file__).with_name('pc-track-weight-default-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
