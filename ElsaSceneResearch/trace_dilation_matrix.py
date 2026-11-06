"""Resolve the PC Dilation matrix processor through MSVC RTTI pointers."""
import json,struct,hashlib
from pathlib import Path
from exe_reader import b,base,sections,read,disasm

def va(offset):
    for r,s,p in sections:
        if p<=offset<p+s:return base+r+offset-p
    raise ValueError('Unmapped file offset')
def refs(value):
    needle=struct.pack('<I',value);pos=0;out=[]
    while True:
        pos=b.find(needle,pos)
        if pos<0:return out
        try:out.append(va(pos))
        except ValueError:pass
        pos+=1

name=b'.?AV?$VariantProcessor@VDilation3d@Types@@VXfrmTransMat@2@@Samurai@@'
at=b.find(name);assert at>=0
td=va(at)-8;rows=[]
for ref in refs(td):
    col=ref-12
    try:
        sig,off,cd,typ,hier=struct.unpack('<5I',read(col,20))
        if sig!=0 or off!=0 or cd!=0 or typ!=td:continue
        for loc in refs(col):
            vt=loc+4;slots=struct.unpack('<17I',read(vt,68))
            rows.append(dict(vtable=hex(vt),locator=hex(col),execute=hex(slots[16]),slots=[hex(x)for x in slots]))
    except ValueError:continue
report=dict(exe_sha256=hashlib.sha256(b).hexdigest(),type_descriptor=hex(td),name=name.decode(),candidates=rows)
Path(__file__).with_name('dilation-matrix-rtti.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
for row in rows:print(disasm(int(row['execute'],16),0x100))
