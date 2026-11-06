"""Validate exact source/destination slot tables from geometry-copy capture."""
import argparse,collections,hashlib,json,struct
from pathlib import Path
def analyze(path):
 path=Path(path);events=[json.loads(l)for l in path.read_text().splitlines()if l.strip()];assert events[0]['schema']=='di3_skin_remap_v1'
 groups=collections.defaultdict(list)
 for e in events:
  if e['event']=='skin_remap':groups[(e['source_object'],e['destination_object'])].append(e)
 results=[]
 for (source,destination),rows in groups.items():
  assert len(rows)==62 and {e['index']for e in rows}==set(range(62))
  rows.sort(key=lambda e:e['index']);ss=int(rows[0]['source_slot'],16);ds=int(rows[0]['destination_slot'],16)
  for e in rows:
   assert int(e['source_slot'],16)==ss+e['index']*4 and int(e['destination_slot'],16)==ds+e['index']*4
   for key in ('source','destination'):
    b=bytes.fromhex(e[key]['header_hex112']);assert len(b)==112
    assert struct.unpack_from('<I',b,24)[0]==int(e[key]['producer'],16)
    assert struct.unpack_from('<H',b,32)[0]==e[key]['stamp']
   assert e['same_node']==(e['source']['address']==e['destination']['address'])
  results.append(dict(source_object=source,destination_object=destination,source_slot_start=hex(ss),destination_slot_start=hex(ds),influences=62,replaced=sum(not e['same_node']for e in rows),registry_counts=sorted(set(e['registry_count']for e in rows)),source_nodes=[e['source']['address']for e in rows],destination_nodes=[e['destination']['address']for e in rows]))
 assert results and events[-1]['event']=='stop' and events[-1]['breakpoints_released']
 return dict(passed=True,capture=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),groups=results,shared_destination_palette=len({tuple(g['destination_nodes'])for g in results})==1,stop=events[-1],scope='Complete62-slot post-assignment geometry-copy tables and node-header identities. Bone labels require separate source/graph association. Identical palettes across copied geometry objects are recorded, not treated as an error. No GPU draw-time proof.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--output',required=True);a=p.parse_args();r=analyze(a.capture);Path(a.output).write_text(json.dumps(r,indent=2));print(json.dumps(dict(passed=r['passed'],groups=[{k:v for k,v in g.items()if k not in ('source_nodes','destination_nodes')}for g in r['groups']],shared_destination_palette=r['shared_destination_palette'])))
