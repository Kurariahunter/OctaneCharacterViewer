"""Original playback duration conversion/argument forwarding windows.

Source selection and surrounding actor calls are excluded, not stubbed.
"""
import json,struct
from pathlib import Path
import native_transition_processor as t
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ESI,UC_X86_REG_EAX,UC_X86_REG_EIP
def f(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def fp(a,v):t.u.mem_write(a,struct.pack('<f',v))
def fl(a):return struct.unpack('<f',t.u.mem_read(a,4))[0]
rows=[]
for frames in [0,1,3,6,30,0x80000000,0xffffffff]:
 t.u.mem_write(t.B,bytes(0x20000));t.put(t.STACK+0x1c,frames);t.u.reg_write(UC_X86_REG_ESP,t.STACK)
 t.u.emu_start(0x4909ed,0x490a06,count=1000)
 assert t.u.reg_read(UC_X86_REG_EIP)==0x490a06
 # Diagnostic x87 result collection, not a replacement for a game call.
 collector=t.B+0x17000;result=t.B+0x17100
 t.u.mem_write(collector,b'\xd9\x1d'+struct.pack('<I',result));t.u.emu_start(collector,collector+6,count=10)
 duration=fl(result);assert duration==f(frames*f(1/30))
 # After successful source selection, playback wrappers forward arg4.
 owner=t.B+0x6000;controller=t.B+0x7000;t.put(owner+0x30,controller)
 t.u.reg_write(UC_X86_REG_ESI,owner);t.u.reg_write(UC_X86_REG_EAX,123)
 t.u.reg_write(UC_X86_REG_ESP,t.STACK);fp(t.STACK+0x14,duration);fp(t.STACK+0x10,.5);t.put(t.STACK+0xc,8)
 t.u.emu_start(0x789a0d,0x789a2f,count=1000)
 sp=t.u.reg_read(UC_X86_REG_ESP);assert fl(sp+0xc)==duration
 # The common playback method forwards its arg4 to controller arg5.
 t.u.reg_write(UC_X86_REG_ESP,t.STACK);t.u.reg_write(UC_X86_REG_ESI,owner)
 fp(t.STACK+0x1c,duration);fp(t.STACK+0x18,.5);t.put(t.STACK+0x14,8);fp(t.STACK+8,.25);fp(t.STACK+4,.75)
 t.u.emu_start(0x788f20,0x788f60,count=1000)
 assert t.u.reg_read(UC_X86_REG_EIP)==0x788f60
 sp=t.u.reg_read(UC_X86_REG_ESP);assert fl(sp+0x10)==duration
 rows.append(dict(unsigned_frame_units=frames,duration_seconds=duration,wrapper_arg4_exact=True,controller_arg5_exact=True))
r=dict(passed=True,exe_sha256=t.sha,cases=rows,scope='Native4909ED..490A06 unsigned frame conversion; native789A0D..789A2F and788F20..788F60 forwarding after explicit source-selection fixture. No full playback method, actor selection, actual live caller or default frame-count assignment claim.')
(Path(__file__).parent/'ControllerState/playback-duration-forwarding-validation.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows),three_frames=rows[2]['duration_seconds'])))
