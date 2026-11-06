"""Native initializer window and complete mode/transition setter (logging off)."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x27000000;u.mem_map(B,0x20000)
P=B+0x1000;S=B+0x18000;STOP=B+0x1F000
def put(a,x):u.mem_write(a,struct.pack('<I',x))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def fl(a):return struct.unpack('<f',u.mem_read(a,4))[0]
u.mem_write(P,b'\xCD'*128)
u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_EBX,0)
u.emu_start(0x6787F0,0x678844,count=1000)
assert u.reg_read(UC_X86_REG_EIP)==0x678844
assert get(P+4)==17 and get(P+0x10)==17 and get(P+0x28)==get(P+0x2C)==3
assert fl(P+0x1C)==struct.unpack('<f',struct.pack('<f',.017))[0]
assert fl(P+0x44)==1 and get(P+0x34)==0xCDCDCDCD and get(P+0x38)==0xCDCDCDCD
rows=[]
scales=[0.,.0625,.125,.25,.5,2.,4.,8.,16.,1.]
for selection,target in enumerate(scales):
 for requested in [0,1]:
  u.mem_write(P,b'\0'*128);u.mem_write(S,b'\0'*128)
  put(P+0x10,17);put(P+0x28,3);put(P+0x2C,3)
  u.mem_write(P+0x38,struct.pack('<f',.25));u.mem_write(P+0x44,struct.pack('<f',1.))
  u.mem_write(S,struct.pack('<III',STOP,selection,requested))
  u.mem_write(STOP+0x100,b'\xDB\xE3');u.emu_start(STOP+0x100,STOP+0x102,count=10)
  u.reg_write(UC_X86_REG_ECX,P);u.reg_write(UC_X86_REG_ESP,S)
  u.emu_start(0x6788C0,STOP,count=10000)
  assert u.reg_read(UC_X86_REG_EIP)==STOP
  assert get(P+0x10)==17 and u.mem_read(P+0x51,1)[0]==requested
  if requested:assert fl(P+0x3C)==1. and fl(P+0x40)==target
  rows.append({'selection':selection,'smooth_requested':requested,'transition_active':u.mem_read(P+0x51,1)[0],'retained_effective_ms':get(P+0x10),'current_scale':fl(P+0x3C),'target_scale':fl(P+0x40)})
out=Path(__file__).parent/'ControllerState'
(out/'clock-setup-validation.json').write_text(json.dumps({'pass':True,'exe_sha256':sha,'initializer_window':'0x6787F0..0x678844; excludes raw timer/logging','initializer_effective_ms':17,'initializer_mode':3,'cap_and_smoothing_parameter_written_by_window':False,'setter_cases':rows,'scope':'Original full setter with logging disabled and controlled prior normal mode; initializer instruction window only. Does not establish live cap, smoothing parameter, call order or all other parent writers.'},indent=2)+'\n',encoding='utf-8')
(out/'clock_setup.txt').write_text(disasm(0x6787E0,0x80)+'\n'+disasm(0x678860,0xD0),encoding='utf-8')
print(json.dumps({'pass':True,'initializer_windows':1,'setter_cases':len(rows)}))
