import sys,zipfile,json,collections
from pathlib import Path
sys.path.insert(0,'F:/DisneyInfinityPortalTest/TupleDecoderResearch')
from decode_tup_safe import decode
with zipfile.ZipFile('G:/Downloads/fro_elsa.zip') as z:
 for i in z.infolist():
  if i.filename.endswith(('.bent','.animtreeoverrides')):
   raw=z.read(i);print(i.filename,len(raw));doc=decode(raw);Path(Path(i.filename).name+'-decoded.json').write_text(json.dumps(doc,indent=2));print(collections.Counter(r['name'] for r in doc['records']).most_common(35))
   rec=doc['records']
   for j,r in enumerate(rec):
    if isinstance(r['value'],str) and ('idle_active' in r['value'] or 'idle_passive' in r['value']): print(json.dumps(rec[max(0,j-5):j+6]))
