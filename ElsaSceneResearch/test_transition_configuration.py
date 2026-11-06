"""Native config-row getter -> duration conversion -> Transition activation window."""
import json,struct
from pathlib import Path
import native_transition_processor as t
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).parent
header=bytes.fromhex(json.loads((R/'ControllerState/live-fade-producer-identity.json').read_text())[2]['hex'])
def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]
rows=[]
for units in [-1,0,1,3,6,30,16777217]:
 for parameter in [.25,1.]:
  t.prepare(header,10.,0.)
  c,h,o,row=[t.B+x for x in (0x6000,0x7000,0x8000,0x9000)]
  for a,v in [(c+0x64,t.P),(c+0x78,h),(h+0x24,o),(h+0x28,0),(o+0x24,row),(o+0x28,1)]:t.put(a,v)
  t.u.mem_write(row+0x24,struct.pack('<if',units,parameter));t.u.mem_write(0x220190c,struct.pack('<f',0.))
  t.u.reg_write(UC_X86_REG_ESI,c);t.u.reg_write(UC_X86_REG_ESP,t.STACK)
  t.u.emu_start(0x77017e,0x7701c9,count=500000)
  assert t.u.reg_read(UC_X86_REG_EIP)==0x7701c9
  after=bytes(t.u.mem_read(t.P,96));duration=struct.unpack_from('<f',after,0x24)[0]
  actual_parameter=struct.unpack_from('<f',after,0x28)[0]
  expected=f(f(units)*f(1/30))
  assert duration==expected and actual_parameter==parameter
  assert after[0x54]==0
  rows.append(dict(units=units,parameter=parameter,duration=duration,completion_cleared=True))
out=dict(passed=True,exe_sha256=t.sha,cases=rows,scope='Original instruction window77017E..7701C9, native row getter76D1A0/76CC50 and76CD90/52D9B0 activation. Synthetic row/clock and zero global clock offset; earlier source/type gates, actor selection and callbacks excluded. Negative sentinel conversion preserved, not normalized to an invented duration.')
(R/'ControllerState/transition-configuration-native-validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows),three_unit_duration=next(x['duration']for x in rows if x['units']==3))))
