"""Execute complete PC normalized parameter getter and track delegation; finite synthetic fixtures."""
import struct,json,math,hashlib
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ESI
from exe_reader import read,disasm
BASE=0x17000000;u.mem_map(BASE,0x10000)
TRACK=BASE+0x1000;PARAM=BASE+0x2000;STACK=BASE+0x8000;STOP=BASE+0x100;OUT=BASE+0x300
u.mem_write(STOP,b'\xd9\x1d'+struct.pack('<I',OUT))
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def call(entry,obj):
    u.mem_write(STACK,struct.pack('<I',STOP));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,obj)
    u.emu_start(entry,STOP,count=1000)
    if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('Native getter did not return')
    u.emu_start(STOP,STOP+6,count=5)
    return struct.unpack('<f',u.mem_read(OUT,4))[0]
rows=[]
for current in [-3.,-1.,0.,.125,.5,1.,2.,5.]:
 for origin in [-1.,0.,1.]:
  for span in [-2.,-.25,-0.,0.,.25,2.]:
   u.mem_write(PARAM,b'\x7f'*64);u.mem_write(PARAM+0x10,struct.pack('<3f',current,origin,span));before=bytes(u.mem_read(PARAM,64))
   expected=1. if span==0 else min(1.,max(0.,f32(f32(current-origin)/span)))
   direct=call(0x59d3c0,PARAM)
   u.mem_write(TRACK,b'\0'*64);u.mem_write(TRACK+0xc,struct.pack('<If',PARAM,.37));delegated=call(0x59d500,TRACK)
   if direct!=expected or delegated!=expected:raise ValueError(('Normalized getter mismatch',current,origin,span,direct,delegated,expected))
   if bytes(u.mem_read(PARAM,64))!=before:raise ValueError('Getter changed source object')
   rows.append(dict(field10=current,field14=origin,field18=span,expected=expected,direct=direct,track_delegated=delegated))
constant=[]
for value in [-2.,0.,.25,1.,3.]:
 u.mem_write(TRACK+0xc,struct.pack('<If',0,value));actual=call(0x59d500,TRACK)
 if actual!=value:raise ValueError('Constant getter changed')
 constant.append(dict(stored=value,actual=actual))
setter_cases=[]
for origin in [-2.,0.,1.]:
 for span in [-2.,0.,.25,3.]:
  for fraction in [-1.,0.,.25,.5,1.,2.]:
   u.mem_write(PARAM,b'\x00'*64);u.mem_write(PARAM+0x10,struct.pack('<3f',99.,origin,span));u.mem_write(STACK,struct.pack('<If',STOP,fraction));u.reg_write(UC_X86_REG_ECX,PARAM);u.reg_write(UC_X86_REG_ESP,STACK)
   u.emu_start(0x59d9d0,STOP,count=1000)
   if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('Setter did not return')
   actual=struct.unpack('<f',u.mem_read(PARAM+0x10,4))[0];expected=f32(origin+f32(span*min(1.,max(0.,fraction))))
   if actual!=expected:raise ValueError(('Normalized setter mismatch',fraction,origin,span,actual,expected))
   setter_cases.append(dict(origin=origin,span=span,input=fraction,stored=actual))
window_cases=[];RANGE=BASE+0x3000;CLIP=BASE+0x4000
for low,high in [(-1.,1.),(0.,.6),(1.,3.),(3.,1.),(2.,2.)]:
 for current in [-1.,0.,.25,.5,1.,2.]:
  u.mem_write(PARAM,b'\0'*64);u.mem_write(PARAM+0x10,struct.pack('<3f',current,0.,1.));u.mem_write(RANGE,b'\0'*128);u.mem_write(RANGE+0x34,struct.pack('<2f',low,high))
  u.mem_write(CLIP,b'\0'*128);u.mem_write(CLIP+0x24,struct.pack('<II',PARAM,RANGE));u.mem_write(STACK,b'\0'*64);u.reg_write(UC_X86_REG_ESI,CLIP);u.reg_write(UC_X86_REG_ESP,STACK)
  u.emu_start(0x59fc2e,0x59fc5f,count=3000)
  if u.reg_read(UC_X86_REG_EIP)!=0x59fc5f:raise ValueError('Clip time window boundary')
  actual=struct.unpack('<f',u.mem_read(STACK+0x14,4))[0];expected=f32(f32(low)+f32(f32(high)-f32(low))*min(1.,max(0.,current)))
  if abs(actual-expected)>2e-7:raise ValueError(('Clip time window mismatch',low,high,current,actual,expected))
  window_cases.append(dict(range34=low,range38=high,current=current,clip_time=actual))
# Null normalized-source pointer leaves the caller's existing clip time untouched.
u.mem_write(CLIP+0x24,struct.pack('<I',0));u.mem_write(STACK+0x14,struct.pack('<f',.375));u.reg_write(UC_X86_REG_ESI,CLIP);u.reg_write(UC_X86_REG_ESP,STACK);u.emu_start(0x59fc2e,0x59fc5f,count=1000)
if struct.unpack('<f',u.mem_read(STACK+0x14,4))[0]!=.375:raise ValueError('Null parameter altered time')
report=dict(pass_=True,exe_sha256=sha,function='0x59d3c0',bytes_sha256=hashlib.sha256(read(0x59d3c0,0x58)).hexdigest(),delegating_getter='0x59d500',formula='if field18 == 0: 1; otherwise clamp01(float32(float32(field10-field14)/field18))',parameter_field_names='Numeric offsets only: semantic ownership/time units not established',finite_cases=len(rows),constant_cases=constant,cases=rows,scope='Complete unmodified native functions on synthetic finite object fields, including signed zero/negative denominators, plus track pointer delegation. No callbacks stubbed; no live actor state, loader interpretation, nonfinite behavior or scheduling parity asserted.')
report['normalized_setter']={'function':'0x59d9d0','formula':'field10 = field14 + field18 * clamp01(input)','callback_pointer_at_8':'null fixture: original callback path not exercised','cases':setter_cases};report['clip_time_remap']={'window':['0x59fc2e','0x59fc5f'],'formula':'range34 + normalizedParameter * (range38-range34)','real_range_getters':['0x503c10','0x76bef0'],'null_pointer_preserves_existing_time':True,'cases':window_cases};report['pass']=report.pop('pass_');Path(__file__).with_name('pc-normalized-parameter-validation.json').write_text(json.dumps(report,indent=2))
Path(__file__).with_name('pc-normalized-parameter-disassembly.txt').write_text(disasm(0x59d3c0,0x58)+'\n\n'+disasm(0x59d500,0x21))
print(json.dumps({k:v for k,v in report.items()if k not in ('cases','normalized_setter','clip_time_remap')},indent=2))
