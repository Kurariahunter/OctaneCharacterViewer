"""Strict same-stamp clip-time -> six scalar inputs -> four native local joints."""
import sys,json,hashlib,struct,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from read_pc_idle_files import Rig,Clip
from native_pc_relationship import run
def analyze(path):
 capture=Path(path).read_bytes()
 cfg=json.loads((ROOT/'OctaneLiveInspector/CheatEngine/idle-phase-sources.json').read_text())
 rig=Rig(ROOT/'ElsaSceneResearch/InstalledGameAssetCheck/fro_elsa/fro_elsa.oct')
 clips={};relations={r['processor']:r for r in cfg['relationships']};rows=[];boundaries=[]
 stops=[]
 for line in capture.decode('utf-8').splitlines():
  row=json.loads(line)
  if row.get('event')=='stop':stops.append(row)
  if row.get('event')!='pose':continue
  if row.get('boundary'):
   boundaries.append(dict(sequence=row['sequence'],reason=row['boundary']));continue
  clock=row['clock'];stamp=clock['stamp']
  nodes=[row['inputs'][f'slot_{i}']for i in range(6)]+[row['outputs'][f'slot_{i}']for i in range(4)]
  if row.get('clock_stamp_after')!=stamp or any(n['stamp']!=stamp for n in nodes):
   boundaries.append(dict(sequence=row['sequence'],reason='Different frame stamps'));continue
  name=row['source']
  if name not in clips:
   source=next(c for c in cfg['clips']if c['name']==name)
   try:clips[name]=Clip(source['path'],rig)
   except ValueError as exc:
    boundaries.append(dict(sequence=row['sequence'],reason='Unsupported clip: '+str(exc)));continue
  clip=clips[name];data=bytes.fromhex(row['source_payload'])
  assert hashlib.sha256(data).hexdigest()==clip.sha,'Complete clip payload mismatch'
  timing=struct.unpack('<5f',bytes.fromhex(clock['payload']))
  phase,lower,upper=timing[:3]
  if not 0<=phase<=clip.duration+1e-5 or abs(lower)>1e-5 or abs(upper-clip.duration)>1e-5:
   boundaries.append(dict(sequence=row['sequence'],reason='Clock range/clip duration differs'));continue
  sampled=clip.sample(phase);actual=[];expected=[];missing=[]
  for i in range(6):
   item=row['inputs'][f'slot_{i}'];port=item['port'];channel=sampled.get(port,{}).get('channels',{}).get('10')
   actual.append(struct.unpack('<f',bytes.fromhex(item['payload']))[0])
   if channel is None:missing.append(port)
   else:expected.append(channel[0])
  if missing:
   boundaries.append(dict(sequence=row['sequence'],reason='Missing scalar source ports',ports=missing));continue
  scalar_error=max(abs(a-b)for a,b in zip(actual,expected))
  relation=relations[row['file_processor']]
  native=run(bytes.fromhex(relation['blob_hex']),expected,4,initial_outputs=relation['initial'])
  captured=[struct.unpack('<8f',bytes.fromhex(row['outputs'][f'slot_{i}']['payload']))for i in range(4)]
  joint_error=max(abs(a-b)for x,y in zip(native,captured)for a,b in zip(x,y))
  actual_native=run(bytes.fromhex(relation['blob_hex']),actual,4,initial_outputs=relation['initial'])
  relationship_error=max(abs(a-b)for x,y in zip(actual_native,captured)for a,b in zip(x,y))
  rows.append(dict(sequence=row['sequence'],side=row['side'],source=name,time=phase,stamp=stamp,scalar_error=scalar_error,joint_error=joint_error,relationship_actual_input_error=relationship_error,pass_=scalar_error<=1e-5 and joint_error<=1e-5))
 result=dict(capture_sha256=hashlib.sha256(capture).hexdigest(),capture_bytes=len(capture),stop_records=stops,checked=len(rows),passed=sum(r['pass_']for r in rows),failed=sum(not r['pass_']for r in rows),relationship_actual_input_max_error=max((r['relationship_actual_input_error']for r in rows),default=None),rows=rows,boundaries=boundaries,scope='Same-stamp original file/time to six scalars and four local finger transforms. No world palette, GPU skinning, dress, face-event or full-animation parity claim.')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--output',required=True);a=p.parse_args();report=analyze(a.capture)
 Path(a.output).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k not in ('rows','boundaries')}))
