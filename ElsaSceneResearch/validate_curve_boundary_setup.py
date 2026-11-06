"""Original configuration-byte application and range recomputation window."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x2C000000;u.mem_map(B,0x20000);P=B+0x1000;ROW=B+0x2000;S=B+0x18000
cases=[]
for flags in [0x58,0x0e]:
 for lo,hi in [(0.,.6),(.25,1.75),(0.,6.166666507720947)]:
  u.mem_write(P,b'\0'*128);u.mem_write(ROW,b'\0'*64);u.mem_write(S,b'\0'*128)
  for off,value in [(0x2c,lo),(0x30,hi),(0x34,lo),(0x38,hi)]:u.mem_write(P+off,struct.pack('<f',value))
  u.mem_write(ROW+0x3c,bytes([flags]));u.mem_write(P+0x63,b'\x03')
  u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_EDI,ROW);u.reg_write(UC_X86_REG_ESP,S)
  u.emu_start(0x774427,0x774443,count=10000)
  assert u.reg_read(UC_X86_REG_EIP)==0x774443
  assert u.mem_read(P+0x62,2)==bytes([flags|0xa0,3])
  actual=struct.unpack('<2f',u.mem_read(P+0x3c,8));expected=struct.unpack('<2f',struct.pack('<2f',lo,hi));assert actual==expected
  cases.append({'config_boundary':flags,'applied_boundary':flags|0xa0,'lower':actual[0],'upper':actual[1],'state_byte63':3})
out=Path(__file__).parent/'ControllerState'
(out/'curve-boundary-setup-validation.json').write_text(json.dumps({'pass':True,'exe_sha256':sha,'cases':cases,'scope':'Original 0x774427..0x774443 calls full native range recomputation 0x525830 twice. Prebuilt row/state ranges; skips source/controller getters and earlier setup. Does not prove selected live actor identity or implement resulting boundary semantics.'},indent=2)+'\n',encoding='utf-8')
(out/'curve_boundary_configuration.txt').write_text(disasm(0x774360,0xe6),encoding='utf-8')
print(json.dumps({'pass':True,'native_setup_cases':len(cases)}))
