"""Summarize scene-load bindings and bounded source-initialized hand replays."""
import argparse,collections,hashlib,json,struct
from pathlib import Path
from native_pc_relationship import run
from evaluate_pc_arms import DN,N,allnodes,get
def analyze(path):
 path=Path(path);events=[json.loads(l) for l in path.read_text().splitlines() if l.strip()]
 assert events[0]['schema']=='di3_skin_binding_v1'
 groups=collections.defaultdict(list)
 for e in events:
  if e['event']=='skin_binding':groups[e['binding']['object']].append(e)
 catalog={}
 for p in allnodes(N,'ProcessorNode'):
  if int(p['value']) not in (165,171):continue
  pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')));refs=dict(pairs)
  blob=bytes.fromhex(get(DN[refs['RelationshipData']],'RelationshipDataBlock')['hex']);initial=[]
  for a,node in pairs:
   if not a.startswith('Output['):continue
   f={c['name']:c['value'] for c in next(c for c in DN[node]['children']if c['name']=='Data')['children']}
   initial.append(f.get('Orientation',[0,0,0,1])+f.get('Translation',[0,0,0])+[f.get('Scale',1.)])
  catalog[hashlib.sha256(blob).hexdigest()]=(int(p['value']),initial)
 replays=[]
 for e in events:
  if e['event']!='relationship_seed':continue
  blob=bytes.fromhex(e['relationship_blob_hex']);digest=hashlib.sha256(blob).hexdigest();pid,initial=catalog[digest]
  stamps={x['node_stamp'] for x in list(e['inputs'].values())+list(e['outputs'].values())};assert len(stamps)==1
  values=[struct.unpack('<f',bytes.fromhex(e['inputs'][f'slot_{i}']['payload_hex']))[0] for i in range(6)]
  actual=[struct.unpack('<8f',bytes.fromhex(e['outputs'][f'slot_{i}']['payload_hex']))for i in range(4)]
  expected=run(blob,values,4,initial_outputs=initial);error=max(abs(a-b)for row,other in zip(actual,expected)for a,b in zip(row,other))
  replays.append(dict(sequence=e['sequence'],file_processor=pid,live_processor=e['processor'],inputs=values,stamp=next(iter(stamps)),max_component_error=error,passed=error<2e-5))
 return dict(capture=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),events=dict(collections.Counter(e['event'] for e in events)),objects=[dict(object=k,bindings=len(v),indices=sorted(set(e['binding']['influence_index']for e in v)),matrix_stamps=sorted(set(e['matrix']['node_stamp']for e in v)))for k,v in groups.items()],hand_replays=replays,hand_replays_passed=bool(replays)and all(r['passed']for r in replays),stop=events[-1],scope='Scene-load slot associations and coherent captured relationship outputs. Replays use serialized PC rig output initialization, not paired runtime entry state. Neither load-time identity matrices nor relationship agreement proves the moving rig is linked to the rendered mesh or GPU draw-time inputs.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--output',required=True);a=p.parse_args();r=analyze(a.capture);Path(a.output).write_text(json.dumps(r,indent=2));print(json.dumps(dict(events=r['events'],objects=len(r['objects']),hand_replays_passed=r['hand_replays_passed'],max_error=max(x['max_component_error']for x in r['hand_replays']))))
