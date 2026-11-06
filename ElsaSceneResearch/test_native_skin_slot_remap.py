"""Original PC geometry-copy slot resolution, after source identity lookup."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
BASE=0x35000000;u.mem_map(BASE,0x20000)
ID=BASE+0x4000;OLD=BASE+0x8000;ENTRY=BASE+0xa000;NEW=BASE+0xc000;META=BASE+0xd000;STACK=BASE+0x10000
def word(a,v):u.mem_write(a,struct.pack('<I',v))
def replay(case):
 u.mem_write(BASE,b'\0'*0x20000)
 word(STACK+0x18,OLD);word(STACK+0x14,0)
 word(0x21b725c,0 if case=='outside_registry' else 1)
 word(0x21af260,0 if case=='missing_entry' else ENTRY)
 # Native generation comparisons: source identity address bits against entry.
 word(ENTRY+8,0x20000000);word(ENTRY+12,0)
 word(ENTRY+16,NEW|1);word(NEW+16,META)
 word(0x21ae4cc,0xffffffff);word(0x21ae4c8,0)
 if case=='generation_mismatch':word(ENTRY+8,0)
 if case=='index_tag_mismatch':word(ENTRY+12,0x40000000)
 if case=='empty_replacement':word(ENTRY+16,1)
 if case=='type_mismatch':word(META,1)
 if case=='untagged_replacement':word(ENTRY+16,NEW)
 u.reg_write(UC_X86_REG_EAX,ID);u.reg_write(UC_X86_REG_ESP,STACK)
 u.emu_start(0x475f14,0x475fa5,count=2000)
 assert u.reg_read(UC_X86_REG_EIP)==0x475fa5
 actual=u.reg_read(UC_X86_REG_EAX)
 expected=OLD if case in ('outside_registry','missing_entry','generation_mismatch','index_tag_mismatch')else 0 if case in ('empty_replacement','type_mismatch')else NEW
 assert actual==expected,(case,hex(actual),hex(expected))
 return dict(case=case,actual=hex(actual),expected=hex(expected))
cases=[replay(c)for c in ('replacement','untagged_replacement','outside_registry','missing_entry','generation_mismatch','index_tag_mismatch','empty_replacement','type_mismatch')]
report=dict(passed=True,exe_sha256=sha,native_range='0x475F14..0x475FA5',cases=cases,scope='Original geometry-copy slot resolution after source identity helper. Explicit synthetic registry/type fixtures. Registry miss or identity mismatch retains old node; matching entry selects replacement, with pointer tag removal and type rejection. Does not validate registry population, whole geometry clone, active actor or GPU draw binding.')
(Path(__file__).parent/'ControllerState/native-skin-slot-remap-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
