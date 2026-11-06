"""Execute original loader argument packing, constructor store and identifier hash."""
import json,struct,hashlib
from pathlib import Path
import native_transition_processor as t
import exe_reader as e
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_ESI,UC_X86_REG_EDX,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
rows=[]
t.u.mem_write(t.B,bytes(0x20000));t.u.reg_write(UC_X86_REG_ESP,t.STACK)
t.u.emu_start(0x144cc9c,0x144cd05,count=1000)
default_duration=struct.unpack('<f',t.u.mem_read(t.STACK+0xc8,4))[0]
assert default_duration==-1.
for value in (-1.,0.,3.,7.):
 t.u.mem_write(t.B,bytes(0x20000));node=t.B+0x6000
 # Original XML loader holds parsed EaseDuration at its frame+0xC8.
 t.u.mem_write(t.STACK+0xc8,struct.pack('<f',value))
 t.u.reg_write(UC_X86_REG_ESP,t.STACK);t.u.reg_write(UC_X86_REG_EAX,node)
 t.u.emu_start(0x144cf53,0x144cfc8,count=1000)
 assert t.u.reg_read(UC_X86_REG_EIP)==0x144cfc8
 packed=t.u.reg_read(UC_X86_REG_ESP)
 assert struct.unpack('<f',t.u.mem_read(packed+44,4))[0]==value
 # Constructor entry includes return address; ESI is established before store window.
 t.u.reg_write(UC_X86_REG_ESP,packed-8);t.u.reg_write(UC_X86_REG_ESI,node)
 t.u.emu_start(0x1446683,0x144669a,count=1000)
 assert struct.unpack('<f',t.u.mem_read(node+0x14,4))[0]==value
 rows.append(dict(ease_duration=value,constructor_argument=12,parameter_offset=20,exact=True))
names={}
for name in ('IDLE_BREAKA','IDLE_BREAKB','IDLE_BREAKC'):
 t.u.mem_write(t.B,bytes(0x20000));s=t.B+0x9000;t.u.mem_write(s,name.encode()+b'\0')
 t.u.reg_write(UC_X86_REG_ESP,t.STACK);t.u.reg_write(UC_X86_REG_EDX,s)
 t.u.emu_start(0x1446704,0x1446724,count=10000)
 actual=t.u.reg_read(UC_X86_REG_EAX);expected=0
 for x in name.encode():expected=(expected*33+x)&0xffffffff
 assert actual==expected;names[name]=hex(actual)
assert names['IDLE_BREAKC']=='0x8db1fc45'
out=dict(passed=True,exe_sha256=t.sha,packing_cases=rows,native_identifier_hashes=names,parser_strings={hex(a):e.read(a,100).split(b'\0')[0].decode()for a in (0x1db2c08,0x1db2b9c,0x1db2be4)},scope='Original144CF53 argument packing,1446683 constructor store and1446704 identifier loop. XML lookup/float conversion and full constructor are not executed; synthetic parser locals are explicit.')
out['windows']=[[0x144cf53,0x144cfc8],[0x1446683,0x144669a],[0x1446704,0x1446724]]
out['absent_ease_duration_default']=default_duration
(R/'ElsaSceneResearch/ControllerState/node-parameter-loader-validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out))
