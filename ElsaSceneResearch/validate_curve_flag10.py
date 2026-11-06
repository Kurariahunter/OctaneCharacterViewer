"""Bounded native validation for the runrf boundary flag, not all flag values."""
import hashlib,json,struct
from pathlib import Path
from read_pc_idle_files import tuple_decode
from pc_clip_decoder import decode
from native_pc_clip_math import curve
from exe_reader import disasm
R=Path(__file__).parent
p=next((R/'InstalledGameAssetCheck').rglob('grl_bm_runrf.oct'))
v=next(r['value']for r in tuple_decode(p.read_bytes())['records']if r['name']=='ClipDataBlock')
b=bytes(v)if isinstance(v,list)else bytes.fromhex(v['hex']);layout=decode(b)
n=struct.unpack_from('<H',b,10)[0];offsets=struct.unpack_from('<'+'I'*(n+2),b,12)
rows=[];rejected=0
for i,s in enumerate(offsets[2:]):
    kind=struct.unpack_from('<H',b,s)[0]
    if kind&1023!=0x10:continue
    end=offsets[i+3]if i+3<len(offsets)else offsets[0]
    block=b[s:end];alternate=bytearray(block);struct.pack_into('<H',alternate,0,(kind&~1023)|0x12)
    lo,hi=struct.unpack_from('<ff',block,4);dims=kind>>10;errors=[]
    for j in range(31):
        t=lo+(hi-lo)*j/30
        a=curve(block,t,dims);z=curve(bytes(alternate),t,dims)
        errors.append(max(abs(x-y)for x,y in zip(a,z)))
    observations=[dict(time=t,values=curve(block,t,dims))for t in (lo-.05,lo,hi,hi+.05)]
    rows.append(dict(curve=i,offset=s,kind=hex(kind),dimensions=dims,max_in_range_mode_comparison_error=max(errors),boundary_observations=observations))
    for flags in (8,0x3ff):
        bad=bytearray(b);struct.pack_into('<H',bad,s,(kind&~1023)|flags)
        try:decode(bytes(bad))
        except ValueError:rejected+=1
        else:raise AssertionError('Unsupported flag admitted')
assert rows and all(x['max_in_range_mode_comparison_error']==0 for x in rows)and rejected==2*len(rows)
report=dict(source=str(p.resolve()),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),clipdata_sha256=hashlib.sha256(b).hexdigest(),
    pass_=True,curves=rows,unsupported_flags_rejected=rejected,
    scope='Native522CF0 comparison on31 in-range points for observed0x10 curve versus established0x12, plus native boundary observations. Does not assert boundary modes identical outside range. Parser still rejects unverified flags.')
(R/'ControllerState/curve-flag10-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(R/'ControllerState/curve-flag10-native-boundaries.txt').write_text(disasm(0x522dc8,0x22)+'\n'+disasm(0x522f5f,0x23)+'\n')
print(json.dumps(report))
