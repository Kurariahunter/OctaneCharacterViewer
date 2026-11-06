"""Original discrete clock configuration and delta-selection windows."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x24000000;u.mem_map(B,0x20000)
P=B+0x1000;S=B+0x18000;STOP=B+0x1F000
def put(a,x):u.mem_write(a,struct.pack('<I',x))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
configs=[];cases=[]
expected=[(0,None),(1,4),(1,3),(1,2),(1,1),(2,1),(2,2),(2,3),(2,4),(3,None)]
for selection,(mode,shift) in enumerate(expected):
    put(P,0xFE);put(P+4,0xFE)
    u.mem_write(S,struct.pack('<4I',STOP,selection,P,P+4))
    u.reg_write(UC_X86_REG_ESP,S);u.emu_start(0x6781A0,STOP,count=1000)
    assert u.reg_read(UC_X86_REG_EIP)==STOP
    assert get(P)==mode and get(P+4)==(0xFE if shift is None else shift)
    configs.append({'selection':selection,'mode':get(P),'shift_written':shift})
for mode in range(5):
 for shift in [1,4]:
  for delta in [0,1,16,100]:
   for one_shot in ([0,1] if mode==0 else [0]):
    u.mem_write(P,b'\0'*128);u.mem_write(S,b'\0'*128)
    put(P+0x28,mode);put(P+0x30,shift);put(P+0x34,50)
    put(P+0x18,1000);u.mem_write(P+0x44,struct.pack('<f',.5));u.mem_write(P+0x50,bytes([one_shot]))
    put(S+20,STOP)
    u.mem_write(STOP+0x100,b'\xDB\xE3\xD9\x05'+struct.pack('<I',0x1B245D0))
    u.emu_start(STOP+0x100,STOP+0x108,count=10)
    u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_EDI,delta);u.reg_write(UC_X86_REG_ESP,S)
    # Enter after transition flag was checked, before discrete mode dispatch.
    u.reg_write(UC_X86_REG_EAX,mode);u.reg_write(UC_X86_REG_EDX,0);u.emu_start(0x67B0E6,STOP,count=1000)
    assert u.reg_read(UC_X86_REG_EIP)==STOP
    result=get(P+0x10)
    expected_delta=[50 if one_shot else 0,max(1,delta>>shift),delta<<shift,delta,max(1,int(delta*.5))][mode]
    assert result==expected_delta,(mode,delta,result,expected_delta)
    assert get(P)==1 and get(P+0x18)==1000+result
    cases.append({'mode':mode,'shift':shift,'supplied_capped_ms':delta,'one_shot':one_shot,'effective_ms':result})
out=Path(__file__).parent/'ControllerState'
(out/'engine-clock-mode-validation.json').write_text(json.dumps({'pass':True,'exe_sha256':sha,'configurations':configs,'cases':cases,'scope':'Original configuration function and discrete mode/accumulation window. Incoming EAX/EDX dispatch registers, capped EDI delta, x87 constant and stack are fixture inputs; transition smoothing, OS timer, live defaults and scheduling are not tested.'},indent=2)+'\n',encoding='utf-8')
(out/'clock_mode_configuration.txt').write_text(disasm(0x6781A0,0xE6)+'\n'+disasm(0x678330,0x62),encoding='utf-8')
print(json.dumps({'pass':True,'configuration_cases':len(configs),'delta_cases':len(cases)}))
