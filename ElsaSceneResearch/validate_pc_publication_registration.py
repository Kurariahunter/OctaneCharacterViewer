"""Execute the original three lifecycle callback registrations."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import read,disasm
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x29000000;u.mem_map(B,0x20000);S=B+0x18000;STOP=B+0x1F000
u.mem_write(S,struct.pack('<I',STOP));u.reg_write(UC_X86_REG_ESP,S)
u.emu_start(0x1AA4340,STOP,count=1000)
assert u.reg_read(UC_X86_REG_EIP)==STOP
rows=[]
for a,name,fn in [(0x2012EE8,'INITIALIZE',0x6A7A10),(0x2012F00,'RUN',0x6A0740),(0x2012F18,'TERMINATE',0x6A1920)]:
 nameptr=struct.unpack('<I',u.mem_read(a,4))[0]
 assert read(nameptr,32).split(b'\0')[0].decode('ascii')==name
 callback=struct.unpack('<4I',u.mem_read(a+8,16))
 assert callback==(fn,0,0,0)
 rows.append({'entry':hex(a),'name':name,'callback':hex(fn),'extra_callback_words':list(callback[1:])})
out=Path(__file__).parent/'ControllerState'
(out/'publication-registration-validation.json').write_text(json.dumps({'pass':True,'exe_sha256':sha,'entries':rows,'scope':'Original startup registration routine only. Does not execute dispatch, lifecycle callbacks or establish global clock/animation ordering.'},indent=2)+'\n',encoding='utf-8')
(out/'publication_registration.txt').write_text(disasm(0x1AA4340,0x93),encoding='utf-8')
print(json.dumps({'pass':True,'registered_callbacks':rows}))
