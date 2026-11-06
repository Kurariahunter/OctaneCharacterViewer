"""Run the constructor's field-default window, excluding containers and reset."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm,read
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_EBX,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x28000000;u.mem_map(B,0x20000);P=B+0x1000;S=B+0x18000
u.mem_write(P,b'\xCD'*256);u.mem_write(S,b'\0'*128)
u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_EBX,0);u.reg_write(UC_X86_REG_ESP,S)
u.emu_start(0x67A9C7,0x67A9FC,count=1000)
assert u.reg_read(UC_X86_REG_EIP)==0x67A9FC
def get(o):return struct.unpack('<I',u.mem_read(P+o,4))[0]
assert get(0x34)==100 and get(0x38)==0 and get(0x44)==0x3F800000
assert get(0x48)==get(0x4C)==30 and u.mem_read(P+0x52,3)==b'\0\0\0'
assert read(0x1AA4030,5)==b'\xB9\xF0\x18\x20\x02'
out=Path(__file__).parent/'ControllerState'
(out/'clock-default-validation.json').write_text(json.dumps({'pass':True,'exe_sha256':sha,'cap_ms':100,'smoothing_parameter':0,'custom_multiplier':1,'fields_48_4c':30,'scope':'Original 0x67A9C7..0x67A9FC window; singleton constructor caller statically verified. Container constructors, reset and runtime overrides excluded.'},indent=2)+'\n',encoding='utf-8')
(out/'clock_defaults.txt').write_text(disasm(0x67A9C7,0x3A)+'\n'+disasm(0x1AA4030,0xF)+'\n'+disasm(0x16AFC79,0x10),encoding='utf-8')
print('Clock defaults: PASS; cap=100ms, smoothing=0, multiplier=1')
