import sys,json,hashlib,struct
from pathlib import Path
sys.path.insert(0,'F:/DisneyInfinityPortalTest/TupleDecoderResearch')
from decode_tup_safe import decode
rows=[]
for p in Path('InstalledGameAssetCheck/IdleMotions').rglob('elsa_bm_idle*.oct'):
 doc=decode(p.read_bytes());blocks=[bytes.fromhex(x['value']['hex']) for x in doc['records'] if x['name']=='ClipDataBlock'];old=Path(p.stem+'.clipdata.bin');oldb=old.read_bytes() if old.exists() else None
 rows.append({'file':str(p),'blocks':[{'bytes':len(x),'sha256':hashlib.sha256(x).hexdigest(),'duration_header':struct.unpack_from('<f',x,4)[0],'matches_downloaded_clipdata':x==oldb} for x in blocks]})
Path('installed-idle-payload-comparison.json').write_text(json.dumps(rows,indent=2));print(rows)
p=next(Path('InstalledGameAssetCheck/Bent').rglob('fro_elsa.bent'));doc=decode(p.read_bytes());Path('installed-elsa-bent-decoded.json').write_text(json.dumps(doc,indent=2));print('Installed BENT',len(p.read_bytes()),'records',len(doc['records']))
