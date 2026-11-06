"""Resolve map property IDs using the EXE's original hash and audit PC Elsa."""
import hashlib
import json
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'TupleDecoderResearch'))
from decode_tup_safe import decode
from native_pc_lean_ik import u, sha
from exe_reader import disasm, read
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EIP, UC_X86_REG_EAX

ROOT=Path(__file__).parent
B=0x1D000000
u.mem_map(B,0x10000)
properties=[]
for name, expected, offset in [('LocalUsedDataNodeIndices',0xA517E168,0x10),
                               ('LocalToPortIndices',0xE3898215,0x28),
                               ('PortToLocalIndices',0x8229E18F,0x40)]:
    u.mem_write(B+0x100,name.encode('ascii')+b'\0')
    u.mem_write(B+0x8000,struct.pack('<II',B+0xF000,B+0x100))
    u.reg_write(UC_X86_REG_ESP,B+0x8000)
    u.emu_start(0x18261F0,B+0xF000,count=100000)
    assert u.reg_read(UC_X86_REG_EIP)==B+0xF000
    actual=u.reg_read(UC_X86_REG_EAX)
    assert actual==expected,(name,hex(actual))
    properties.append({'name':name,'native_hash':hex(actual),'structure_offset':hex(offset),
                       'payload_offset':hex(offset+0x10),'count_offset':hex(offset+0x14)})

path=ROOT/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct'
raw=path.read_bytes()
doc=decode(raw)
net=[];current=None
for r in doc['records']:
    if r['name']=='BaseDataNodeLinks':
        current={'record_offset':r['offset'],'instance':r['value'],'tables':{}}
        net.append(current)
    elif current is not None and r['name'] in [p['name'] for p in properties]:
        value=r['value']
        data=bytes.fromhex(value['hex']) if isinstance(value,dict) else bytes(value)
        assert len(data)%2==0
        current['tables'][r['name']]=list(struct.unpack('<'+'H'*(len(data)//2),data))
used=next(r['value'] for r in doc['records'] if r['name']=='ConnectionMapUsedDataNodes')
for n in net:
    tables=n['tables'];local=tables['LocalUsedDataNodeIndices'];ports=tables['LocalToPortIndices'];reverse=tables['PortToLocalIndices']
    assert len(local)==len(ports)
    rows=[]
    for slot,(used_index,port) in enumerate(zip(local,ports)):
        assert port<len(reverse)
        assert reverse[port]==slot,(slot,port,reverse[port])
        assert used_index<len(used)
        rows.append({'source_slot':slot,'connection_map_used_index':used_index,
                     'data_node_id':used[used_index],'filter_coefficient_index_port':port})
    n['rows']=rows
    n['counts']={'local':len(local),'ports':len(reverse),'connection_map_used_nodes':len(used)}
    n['reverse_non_sentinel_count']=sum(x!=65535 for x in reverse)
    n['forward_reverse_agree']=True

report={'pass':True,'exe_sha256':sha,'asset':str(path.resolve()),
        'asset_sha256':hashlib.sha256(raw).hexdigest(),'property_hashes':properties,'maps':net,
        'scope':'Original EXE hash routine executes without stubs. Offline PC asset table audit. Registration and copy instruction validation are separate tests; no live actor identity or full loader execution is implied.'}
capture=ROOT.parent/'OctaneLiveInspector/Captures/ce_blendexec_20261017_204631_310307171.jsonl'
capture_raw=capture.read_bytes()
pairs=[]
groups={}
for line in capture_raw.decode('utf-8').splitlines():
    event=json.loads(line)
    if event.get('event')!='blend':continue
    for contribution in event.get('contributions',{}).values():
        word=int(contribution['packed_word'],16)
        slot,port=word&0xFFF,(word>>12)&0xFFF
        table=net[0]['tables']['LocalToPortIndices']
        pairs.append({'source_slot':slot,'filter_index':port,
                      'matches_pc_elsa_table':slot<len(table) and table[slot]==port})
        key=(contribution['controller'],contribution['container'])
        group=groups.setdefault(key,{'controller':key[0],'container':key[1],
                                    'container_count':contribution['container_count'],
                                    'contributions':0,'matching':0,'pairs':set()})
        group['contributions']+=1
        group['matching']+=int(pairs[-1]['matches_pc_elsa_table'])
        group['pairs'].add((slot,port))
for group in groups.values():group['pairs']=sorted(group['pairs'])
report['existing_capture_comparison']={
    'sha256':hashlib.sha256(capture_raw).hexdigest(),'contributions':len(pairs),
    'matching':sum(p['matches_pc_elsa_table'] for p in pairs),
    'distinct_pairs':len({(p['source_slot'],p['filter_index']) for p in pairs}),
    'mismatches':[p for p in pairs if not p['matches_pc_elsa_table']],
    'by_controller':list(groups.values()),
    'limitation':'Table agreement alone does not identify the captured actor or establish which clip or filter was active.'}
out=ROOT/'RuntimeMapConstruction'
(out/'serialized-runtime-map-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
# Complete hash function ends just before lookup routine at 0x1826420.
(out/'native-property-name-hash.txt').write_text(disasm(0x18261F0,0x230)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'properties':properties,'maps':[n['counts'] for n in net],
                  'capture_comparison':report['existing_capture_comparison']}))
