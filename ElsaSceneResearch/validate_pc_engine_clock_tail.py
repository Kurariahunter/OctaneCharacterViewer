"""Execute original clock accumulation tail with selected millisecond deltas."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x23000000;u.mem_map(B,0x20000)
P=B+0x1000;S=B+0x18000;STOP=B+0x1F000
rows=[]
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
for total in [0,123456,0x7FFFFFF0,0xFFFFFFF0]:
 for delta in [0,1,16,100]:
    u.mem_write(P,b'\0'*128);u.mem_write(S,b'\0'*128)
    u.mem_write(P,struct.pack('<I',123));u.mem_write(P+0x10,struct.pack('<I',delta))
    u.mem_write(P+0x18,struct.pack('<I',total));u.mem_write(P+0x24,struct.pack('<f',9.5))
    # At tail entry EDI/ESI and 12 local bytes remain on stack. Seed x87
    # with the exact float 0.001 loaded by the original update prologue.
    u.mem_write(S,struct.pack('<IIIII',0,0,0,0,0)+struct.pack('<I',STOP))
    u.mem_write(STOP+0x100,b'\xDB\xE3\xD9\x05'+struct.pack('<I',0x1B245D0))
    u.emu_start(STOP+0x100,STOP+0x108,count=10)
    u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_ESP,S)
    u.emu_start(0x67B169,STOP,count=1000)
    assert u.reg_read(UC_X86_REG_EIP)==STOP
    result=struct.unpack('<I',u.mem_read(P+0x18,4))[0]
    seconds=struct.unpack('<f',u.mem_read(P+0x24,4))[0]
    dt=struct.unpack('<f',u.mem_read(P+0x1C,4))[0]
    assert result==(total+delta)&0xFFFFFFFF
    assert seconds==f32(result*0.001)
    assert dt==f32(delta*f32(.001))
    assert struct.unpack('<I',u.mem_read(P,4))[0]==124
    assert struct.unpack('<f',u.mem_read(P+0x20,4))[0]==9.5
    rows.append({'prior_ms':total,'delta_ms':delta,'total_ms':result,'seconds':seconds,'delta_seconds':dt})
report={'pass':True,'exe_sha256':sha,'cases':rows,'scope':'Original 0x67B169..0x67B1B6 accumulation tail only. Delta/mode selection and OS timer are not executed. x87 incoming constant and stack are prebuilt.'}
(Path(__file__).parent/'ControllerState/engine-clock-tail-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'native_cases':len(rows)}))
