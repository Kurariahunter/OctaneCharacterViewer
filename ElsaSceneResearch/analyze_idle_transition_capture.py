"""Inspect ordered sampling/source/factor traces; never infer missing fade rules."""
import sys,json,struct,hashlib,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from read_pc_idle_files import Rig,Clip
def analyze(path):
 cfg=json.loads((ROOT/'OctaneLiveInspector/CheatEngine/idle-phase-sources.json').read_text())
 rig=Rig(ROOT/'ElsaSceneResearch/InstalledGameAssetCheck/fro_elsa/fro_elsa.oct');cache={};checked=[];boundaries=[]
 def scalar(n):return struct.unpack_from('<f',bytes.fromhex(n['payload']))[0]
 def factor(n):return 1. if n.get('default_one')else scalar(n)
 raw=Path(path).read_bytes();schema=None
 for line in raw.decode().splitlines():
  row=json.loads(line)
  if row.get('event')=='start':schema=row.get('schema')
  if row.get('event')!='pose':continue
  try:
   assert not row.get('boundary'),row.get('boundary')
   name=row['source']
   if name not in cache:cache[name]=Clip(next(c['path']for c in cfg['clips']if c['name']==name),rig)
   clip=cache[name];assert hashlib.sha256(bytes.fromhex(row['source_payload'])).hexdigest()==clip.sha,'Source payload differs'
   clock_time=scalar(row['clock']);details=[]
   stamp=row['clock']['stamp']
   assert row['clock_stamp_after']==stamp,'Clock stamp changed during capture'
   assert all(row['outputs'][f'slot_{j}']['stamp']==stamp for j in range(4)),'Joint output stamps differ'
   for i in range(6):
    item=row['inputs'][f'slot_{i}'];trace=item['final_scalar_trace'];sample=trace['actual_sample']
    assert item['stamp']==stamp,'Relationship input/clock stamps differ'
    assert trace['controller']==row['controller']and trace['resolved']==row['resolved'],'Controller/resolved differs'
    assert trace['mapped_port']==item['port']and trace['output']['address']==item['address'],'Port/output alias differs'
    assert trace['output']['payload']==item['payload'],'Final scalar changed since return'
    assert trace['output']['stamp']==trace['source']['stamp']==sample['clock']['stamp']==stamp,'Different sample/scalar stamps'
    assert sample['order']<=trace['order']<row['order'],'Callback order differs'
    assert sample['resolved']==row['resolved']and sample['source']==name,'Sample source/resolved differs'
    assert bytes.fromhex(sample['prefix'])==clip.b[:128],'Sample prefix differs'
    phase=struct.unpack('<f',bytes.fromhex(sample['time_hex4']))[0]
    assert 0<=phase<=clip.duration+1e-5,'Actual sample time outside clip'
    expected=clip.sample(phase)[item['port']]['channels']['10'][0]
    actual=scalar(trace['source']);output=scalar(item)
    coefficient=1. if trace['filter_default_one']else struct.unpack('<f',bytes.fromhex(trace['filter_coefficient_hex4']))[0]
    details.append(dict(port=item['port'],actual_sample_time=phase,clock_observed_later=clock_time,file_scalar=expected,source_scalar=actual,source_error=abs(actual-expected),final_scalar=output,source_to_final_difference=output-actual,factor2c=factor(trace['factor2c']),factor30=factor(trace['factor30']),filter_coefficient=coefficient,priority=struct.unpack('<f',bytes.fromhex(trace['priority_hex4']))[0],flag39=int(trace['flag39_hex1'],16),packed=trace['packed']))
    if schema=='di3_idle_transition_v2':
     entry=trace['entry']
     assert entry['processor']==trace['processor']and entry['output']['address']==item['address'],'Entry processor/output differs'
     assert entry['order']<trace['order'],'Entry/return order differs'
     info=details[-1]
     info.update(previous_output=scalar(entry['output']),previous_factor=struct.unpack('<f',bytes.fromhex(entry['previous_factor_hex4']))[0],processor_flags=int.from_bytes(bytes.fromhex(entry['flags_hex4']),'little'))
     # Unit source weighting leaves no residual default-network contribution.
     if info['factor2c']==1 and coefficient==1 and info['flag39']==0:
      from native_pc_blend_replay import blend
      native=blend([dict(values=[actual]+[0.]*15,priority=info['priority'],flag=0,weight=None,factor2c=None,factor30=info['factor30'])],scalar=True,previous_output=info['previous_output'],previous_factor=info['previous_factor'],bypass_fade=bool(info['processor_flags']&0x80000000))[0]
      info.update(native_final_scalar=native,native_final_error=abs(native-output))
   result=dict(sequence=row['sequence'],side=row['side'],source=name,time=clock_time,details=details,max_source_error=max(d['source_error']for d in details))
   if all('native_final_scalar'in d for d in details):
    from native_pc_relationship import run
    relation=next(r for r in cfg['relationships']if r['processor']==row['file_processor'])
    native=run(bytes.fromhex(relation['blob_hex']),[d['native_final_scalar']for d in details],4,initial_outputs=relation['initial'])
    captured=[struct.unpack('<8f',bytes.fromhex(row['outputs'][f'slot_{j}']['payload']))for j in range(4)]
    result['native_joint_error']=max(abs(a-b)for x,y in zip(native,captured)for a,b in zip(x,y))
   checked.append(result)
  except (AssertionError,KeyError,ValueError,TypeError,StopIteration,struct.error)as exc:
   boundaries.append(dict(sequence=row.get('sequence'),reason=str(exc)))
 native_rows=[r for r in checked if all('native_final_error'in d for d in r['details'])]
 return dict(capture_sha256=hashlib.sha256(raw).hexdigest(),checked=len(checked),exact_source_rows=sum(r['max_source_error']==0 for r in checked),native_final_checked_rows=len(native_rows),native_final_exact_rows=sum(all(d['native_final_error']==0 for d in r['details'])for r in native_rows),native_joint_exact_rows=sum(r.get('native_joint_error')==0 for r in native_rows),rows=checked,boundaries=boundaries,scope='Ordered latest-record links checked by source/controller/port/stamp and exact output payload; not thread/call-stack identity. Source values compared at actual sampling time. V2 replays original native Float-blend instructions only for single unflagged contributors with unit filter/factor2c and captured prior state, then native local finger relationships. No world/skinning/rendering parity or pose correction.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--output',required=True);a=p.parse_args();r=analyze(a.capture);Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in r.items()if k not in ('rows','boundaries')}))
