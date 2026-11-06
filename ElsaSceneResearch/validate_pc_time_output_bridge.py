"""Native local-time emission and clip time getter, plus captured node links."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x22000000;u.mem_map(B,0x20000)
P=B+0x1000;N=B+0x2000;META=B+0x3000;VT=B+0x4000;CLIP=B+0x5000;S=B+0x18000;STOP=B+0x1F000;VALUE=STOP+0x100
def put(a,v):u.mem_write(a,struct.pack('<I',v))
rows=[]
for time in [0.,.125,1.,1.8333333730697632]:
 for status in [0,1,0x98,0x103]:
    u.mem_write(P,b'\0'*128);u.mem_write(N,b'\0'*128);u.mem_write(S,b'\0'*128)
    u.mem_write(P+0x18,struct.pack('<HBB',0x64,2,1));put(P+0x6C,N)
    u.mem_write(P+0x3C,struct.pack('<2f',0.,2.));u.mem_write(P+0x54,struct.pack('<2f',time,.75))
    u.mem_write(P+0x60,struct.pack('<H',status));put(N+0x1C,META);u.mem_write(META+0x20,struct.pack('<H',123))
    u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_ESP,S)
    u.emu_start(0x5340DA,0x53411A,count=10000)
    assert u.reg_read(UC_X86_REG_EIP)==0x53411A
    payload=struct.unpack('<4fH',u.mem_read(N+0x34,18))
    assert payload==(time,0.,2.,.75,status)
    assert struct.unpack('<H',u.mem_read(N+0x20,2))[0]==123
    # Native typed payload getter 0x504030 returns a 0x14-byte record at node+0x34.
    # Virtual table is prebuilt for this fixture; it is not a captured vtable assertion.
    put(N,VT);put(VT+0x50,0x504030);put(CLIP+0x18,N);put(S,STOP)
    u.reg_write(UC_X86_REG_ESP,S);u.reg_write(UC_X86_REG_ECX,CLIP)
    u.emu_start(0x528A70,STOP,count=10000)
    assert u.reg_read(UC_X86_REG_EIP)==STOP
    u.mem_write(STOP,b'\xD9\x1D'+struct.pack('<I',VALUE));u.emu_start(STOP,STOP+6,count=10)
    sampled=struct.unpack('<f',u.mem_read(VALUE,4))[0]
    assert sampled==time
    rows.append({'local_time':time,'status':status,'sample_time':sampled})
captures=[]
for p in sorted((Path(__file__).parent.parent/'OctaneLiveInspector/Captures').glob('ce_controllerstate_20261019_*.jsonl')):
    matches=checked=0;types={}
    for line in p.read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        for c in event.get('contributions',{}).values():
            state=c.get('controller_state',{});h=state.get('state_header_hex128');r=state.get('resolved_header_hex128')
            if not h or not r:continue
            h=bytes.fromhex(h);r=bytes.fromhex(r);offset=struct.unpack_from('<H',h,0x18)[0];inputs=h[0x1A];outputs=h[0x1B]
            slot=offset+4*inputs
            if outputs<1 or slot+4>len(h):continue
            outnode=struct.unpack_from('<I',h,slot)[0];innode=struct.unpack_from('<I',r,0x18)[0]
            checked+=1;matches+=int(outnode!=0 and outnode==innode)
            key=state.get('resolved_rtti_candidate','unknown');types[key]=types.get(key,0)+1
    captures.append({'capture':p.name,'checked_links':checked,'matching_links':matches,'resolved_types':types})
out=Path(__file__).parent/'ControllerState'
report={'pass':True,'exe_sha256':sha,'native_cases':rows,'captured_links':captures,
        'scope':'Original output emission tail and complete ClipProcessor time getter execute. Cached output metadata and virtual payload-getter table are prebuilt. Does not invoke full sampler or clock producer; captured pointer agreement independently checks the runtime wiring.'}
(out/'time-output-bridge-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'native_cases':len(rows),'captured_links':captures}))
