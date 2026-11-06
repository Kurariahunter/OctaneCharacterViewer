from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import rpx_research as r
from capstone import Cs,CS_ARCH_PPC,CS_MODE_32,CS_MODE_BIG_ENDIAN
p=Path(__file__).parent;symbols=list(r.symbols());by_va={}
for s in symbols:
 if s['va']:by_va.setdefault(s['va'],s)
md=Cs(CS_ARCH_PPC,CS_MODE_32|CS_MODE_BIG_ENDIAN);md.skipdata=True;coverage=[];manifest=[]
for f in sorted(p.glob('0*.txt')):
 va=int(f.stem,16);s=by_va[va];data=r.read(va,s['size']);ins=list(md.disasm(data,va));assert sum(x.size for x in ins)==len(data);lines=[];calls=[]
 for x in ins:
  line=f'{x.address:08x} {x.mnemonic} {x.op_str}'
  if x.mnemonic in ('b','bl'):
   try:
    target=int(x.op_str,16)
    if target in by_va:
     line+=' ; '+by_va[target]['name'];calls.append({'site':hex(x.address),'kind':x.mnemonic,'target':hex(target),'symbol':by_va[target]['name']})
   except ValueError:pass
  lines.append(line)
 f.write_text('\n'.join(lines));coverage.append({'address':hex(va),'size':len(data),'decoded_bytes':sum(x.size for x in ins),'undecoded_data_records':sum(x.id==0 for x in ins)});manifest.append({**s,'sha256':hashlib.sha256(data).hexdigest(),'calls':calls})
(p/'disassembly-coverage.json').write_text(json.dumps(coverage,indent=2));(p/'function-evidence-manifest.json').write_text(json.dumps({'source_rpx_sha256':json.loads((p.parent/'RPX/sections.json').read_text())['sha256'],'scope':'Static inspection; generic PPC disassembler has paired-single decode limitations.','functions':manifest},indent=2));print('Saved full-byte disassembly and fingerprints for',len(manifest),'functions')
