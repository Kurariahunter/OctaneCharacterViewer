"""Bounded exact-byte search of extracted assets; matches are not schema proof."""
import argparse,hashlib,json
from pathlib import Path

def scan(capture,root):
 rows=[json.loads(x)for x in Path(capture).read_text().splitlines()]
 request=next(x for x in rows if x.get('event')=='request'and x.get('selection'))
 payload=bytes.fromhex(request['selection']['parameter_hex80'])
 needles={'full_parameter_80':payload,'identifier_through_duration_24':payload[:24]}
 matches=[];files=total=0
 for p in sorted(Path(root).rglob('*')):
  if not p.is_file()or p.suffix.lower()not in {'.oct','.bent','.banm','.animtreeoverrides','.mtb'}:continue
  if p.stat().st_size>64*1024*1024:continue
  b=p.read_bytes();files+=1;total+=len(b)
  for label,needle in needles.items():
   offset=b.find(needle)
   while offset>=0:
    matches.append(dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),match=label,offset=offset))
    offset=b.find(needle,offset+1)
 return dict(capture=str(Path(capture).resolve()),root=str(Path(root).resolve()),files=files,bytes=total,matches=matches,scope='Exact 80/24-byte searches of selected extracted binary asset types, each at most64MiB. No hit does not exclude serialized, relocated or transformed parameter data; a hit alone is not schema proof.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('root');p.add_argument('--output',required=True);a=p.parse_args();r=scan(a.capture,a.root);Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
