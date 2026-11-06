"""Execute original source-asset and layer-row getter chains."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EAX
B=0x20000000;u.mem_map(B,0x20000)
C,H,D,W,A,O,R,S,T=[B+x for x in [0x1000,0x2000,0x3000,0x4000,0x5000,0x6000,0x7000,0x18000,0x1F000]]
def put(a,v):u.mem_write(a,struct.pack('<I',v))
cases=[]
for missing in ['none','handle','descriptor','wrapper','asset','row_owner','row_out_of_bounds']:
    u.mem_write(B,b'\0'*0x20000)
    put(C+0x78,H);put(H+0x20,D);put(D+0x10,W);put(W+0xC,A)
    put(H+0x24,O);put(H+0x28,1);put(O+0x24,R);put(O+0x28,2)
    if missing=='handle':put(C+0x78,0)
    elif missing=='descriptor':put(H+0x20,0)
    elif missing=='wrapper':put(D+0x10,0)
    elif missing=='asset':put(W+0xC,0)
    elif missing=='row_owner':put(H+0x24,0)
    elif missing=='row_out_of_bounds':put(H+0x28,2)
    actual=[]
    for entry in [0x76D180,0x76D1A0]:
        put(S,T);u.reg_write(UC_X86_REG_ESP,S);u.reg_write(UC_X86_REG_ECX,C)
        u.emu_start(entry,T,count=10000)
        assert u.reg_read(UC_X86_REG_EIP)==T
        actual.append(u.reg_read(UC_X86_REG_EAX))
    expected_source=0 if missing in ['handle','descriptor','wrapper','asset'] else A
    expected_row=0 if missing in ['handle','row_owner','row_out_of_bounds'] else R+64
    assert actual==[expected_source,expected_row],(missing,actual)
    cases.append({'case':missing,'source_present':bool(actual[0]),'selected_row_present':bool(actual[1])})
out=Path(__file__).parent/'ControllerState';out.mkdir(exist_ok=True)
report={'pass':True,'exe_sha256':sha,'cases':cases,
        'source_chain':['controller+0x78','handle+0x20','descriptor+0x10','wrapper+0x0C'],
        'scope':'Original complete getter chains with synthetic pointer graphs. Source result and selected row are independently resolved. No actor identity, asset-name layout, clip-time or scheduler semantics inferred.'}
(out/'source-link-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for name,va,size in [('controller_source_getter',0x76D180,0x1A),('controller_row_getter',0x76D1A0,0xF),('descriptor_source_getter',0x76C900,0xF),('reference_getter',0x6148D0,4),('controller_state_getter',0x19368D0,4)]:
    (out/(name+'.txt')).write_text(disasm(va,size)+'\n',encoding='utf-8')
print(json.dumps(report))
