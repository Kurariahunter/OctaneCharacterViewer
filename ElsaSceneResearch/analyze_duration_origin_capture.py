"""Validate source identities and observed playback request-to-duration write."""
import json,struct,hashlib,argparse
from pathlib import Path
from read_pc_idle_files import Rig,Clip
from native_transition_processor import resolve_duration
R=Path(__file__).resolve().parents[1]
def analyze(path):
 raw=Path(path).read_bytes();rows=[json.loads(l)for l in raw.decode().splitlines()]
 start=rows[0];base=int(start['module_base'],16);cfg=json.loads((R/'OctaneLiveInspector/CheatEngine/idle-phase-sources.json').read_text());sources={c['name']:c for c in cfg['clips']};cache={};events={};chains=[];boundaries=[]
 for row in rows:
  if row['event']not in ('request','controller','duration_set'):continue
  try:
   identity=row['identity'];name=identity['source']
   if name not in cache:cache[name]=Clip(sources[name]['path'],Rig(R/'ElsaSceneResearch/InstalledGameAssetCheck/fro_elsa/fro_elsa.oct')).sha
   assert hashlib.sha256(bytes.fromhex(identity['source_payload'])).hexdigest()==cache[name],'Source hash differs'
   if row['event']=='controller':
    request=events[row['request_order']]
    assert request['event']=='request'and request['identity']['controller']==identity['controller']and request['identity']['processor']==identity['processor'],'Request identity differs'
    assert int(request['stack'],16)-int(row['stack'],16)==60 and row['request_stack_delta']==60,'Request/controller frame differs'
    assert request['order']<row['order'],'Request order differs'
    assert bytes.fromhex(request['arguments_hex16'])[12:16]==bytes.fromhex(row['arguments_hex20'])[16:20],'Duration forwarding differs'
   elif row['event']=='duration_set':
    controller=events[row['controller_order']];request=events[row['request_order']]
    assert controller['request_order']==request['order']and request['order']<controller['order']<row['order'],'Chain order differs'
    for key in ('controller','processor','resolved','source'):assert controller['identity'][key]==identity[key],'Setter/controller identity differs'
    arg=bytes.fromhex(controller['arguments_hex20'])[16:20]
    h=bytes.fromhex(row['processor_header'])
    assert arg==bytes.fromhex(row['argument_hex4'])==bytes.fromhex(row['stored_hex4'])==h[0x24:0x28],'Setter argument/store differs'
    assert int(row['caller_return'],16)-base+0x400000==0x77038c,'Setter caller differs'
    assert int(controller['caller_return'],16)-base+0x400000==0x788f65,'Controller caller differs'
    old=struct.unpack('<f',bytes.fromhex(controller['duration_before_hex4']))[0];value=struct.unpack('<f',arg)[0]
    prior=bytearray(h);prior[0x24:0x28]=bytes.fromhex(controller['duration_before_hex4'])
    predicted=resolve_duration(prior,value);assert predicted[0x24:0x28]==arg,'Native negative-duration resolution differs'
    chains.append(dict(request_sequence=request['sequence'],controller_sequence=controller['sequence'],setter_sequence=row['sequence'],source_before=request['identity']['source'],source_after=identity['source'],playback_caller_preferred_va=hex(int(request['caller_return'],16)-base+0x400000),request_kind=request['kind'],requested_identifier_hex=hex(struct.unpack_from('<I',bytes.fromhex(request['arguments_hex16']))[0]),prior_duration=old,requested_duration=value,stored_duration=value,native_resolution_exact=True))
   events[row['order']]=row
  except (AssertionError,KeyError,ValueError,TypeError,struct.error)as exc:boundaries.append(dict(sequence=row.get('sequence'),reason=str(exc)))
 return dict(capture_sha256=hashlib.sha256(raw).hexdigest(),verified_chains=len(chains),chains=chains,boundaries=boundaries,stop_records=[x for x in rows if x['event']=='stop'],scope='Observed request/controller/setter argument chain and full PC source hashes. Pre-selection source may differ from selected source. Native fallback comparison uses captured prior duration and supplied argument, not an inferred default. No unique actor/thread or full scheduler/rendering claim.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--output',required=True);a=p.parse_args();r=analyze(a.capture);Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
