"""Validate typed write sites and real setter return slots, not a stack scan."""
import hashlib, json, struct, sys
from collections import Counter
from pathlib import Path
from exe_reader import read, disasm, b

p=Path(sys.argv[1]); raw=p.read_bytes()
events=[json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
base=int(events[0]['module_base'],16)
spec={'float_clock':(0x4913BF,0x496B24,'<f',0x4913BC,b'\xD9\x5E\x34'),
      'uint_update_token':(0x49156C,0x496B86,'<I',0x491569,b'\x89\x4E\x34')}
groups={}
for e in events:
    if e['event']!='clock_write':continue
    kind=e['kind']
    # Logger names its integer watch uint_clock/update_token depending on version.
    key='float_clock' if kind=='float_clock' else 'uint_update_token'
    post,ret,fmt,write,opcode=spec[key]
    assert int(e['eip_after_write'],16)-base+0x400000==post
    stack=bytes.fromhex(e['stack_hex128'])
    assert struct.unpack_from('<I',stack,4)[0]-base+0x400000==ret
    assert struct.unpack_from('<I',stack,8)[0]==int(e['eax'],16)
    assert int(e['watched'],16)==int(e['esi'],16)+0x34
    assert read(write,len(opcode))==opcode
    value=struct.unpack(fmt,bytes.fromhex(e['value_hex4']))[0]
    groups.setdefault(key,[]).append({'sequence':e['sequence'],'elapsed_ms':e['elapsed_ms'],'value':value})
out=Path(__file__).parent/'ControllerState'
report={'capture':str(p.resolve()),'capture_sha256':hashlib.sha256(raw).hexdigest(),
        'exe_sha256':hashlib.sha256(b).hexdigest(),'event_counts':dict(Counter(e['event'] for e in events)),
        'pass':True,'groups':groups,'stop':events[-1],
        'scope':'All write EIPs, node payload addresses and setter return/argument slots validated. Stack offset +4 is justified by each setter pushing ESI before its payload write. No general stack unwind or FPS inference.'}
(out/'clock-writer-capture-analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
for name,a,n in [('host_clock_bridge',0x496B00,0xA9),('engine_clock_update',0x67AFF0,0x1C8),('clock_raw_timer',0x40D590,0x6D)]:
    (out/(name+'.txt')).write_text(disasm(a,n)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'counts':report['event_counts'],'writes':{k:len(v) for k,v in groups.items()}}))
