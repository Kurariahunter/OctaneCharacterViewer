"""Walk boundary flags: independent curve math versus native in-range samples."""
import json,struct
from pathlib import Path
from read_pc_idle_files import Rig,Clip,R
from pc_clip_decoder import decode,sample
from native_pc_clip_math import curve

rig=Rig(R/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct')
p=next((R/'InstalledGameAssetCheck/WalkMotions').rglob('grl_bm_walkf.oct'));c=Clip(p,rig)
assert not c.unmapped
rows=[]
for ci,item in enumerate(c.layout['curves']):
    a=c.offsets[ci+2];z=c.offsets[ci+3]if ci+3<len(c.offsets)else c.offsets[0]
    regs=[i for i,r in enumerate(c.layout['registers'])if r['curve']==ci]
    for fraction in (0,.13,.37,.61,.89,1):
        t=c.duration*fraction;actual=curve(c.b[a:z],t,len(item['metadata']))
        expected=[sample(c.layout,r,t)for r in regs]
        rows.append(dict(curve=ci,boundary_flags=item['boundary_flags'],fraction=fraction,
            error=max(abs(x-y)for x,y in zip(actual,expected))))
broken=bytearray(c.b);offset=c.offsets[2];kind=struct.unpack_from('<H',broken,offset)[0]
struct.pack_into('<H',broken,offset,(kind&~0x3ff)|0x3ff)
try:decode(bytes(broken))
except ValueError:pass
else:raise AssertionError('unknown boundary flags accepted')
summary=dict(source=str(p),clipdata_sha256=c.sha,duration=c.duration,unmapped_ports=c.unmapped,
    curve_cases=len(rows),max_error=max(r['error']for r in rows),
    flags=sorted({r['boundary_flags']for r in rows}),unknown_flags_rejected=True)
(R/'pc-walk-file-reader-validation.json').write_text(json.dumps(dict(summary=summary,rows=rows),indent=2))
print(json.dumps(summary,indent=2))
assert summary['max_error']<1e-5
