"""Independently replay activation/update snapshots; expose unobserved changes."""
import argparse,json,struct,hashlib
from pathlib import Path
from native_transition_processor import activate,step
R=Path(__file__).resolve().parents[1]
def f(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def scalar(n):return struct.unpack_from('<f',bytes.fromhex(n['payload']))[0]
def analyze(path):
 raw=Path(path).read_bytes();cfg=json.loads((R/'OctaneLiveInspector/CheatEngine/idle-phase-sources.json').read_text())
 clips={c['name']:c for c in cfg['clips']};rows=[];boundaries=[];last={};activations={}
 fields=list(range(0x1c,0x38,4))+[0x48,0x4c,0x50]
 for line in raw.decode().splitlines():
  row=json.loads(line)
  if row.get('event')not in ('activation','update'):continue
  try:
   identity=row['identity'];clip=clips[identity['source']]
   data=bytes.fromhex(identity['source_payload']);assert len(data)==clip['bytes']and data[:128]==bytes.fromhex(clip['prefix_hex']),'Source identity differs'
   # Match full bytes against the original decoded ClipData source.
   from read_pc_idle_files import Rig,Clip
   if 'decoded_sha'not in clip:
    rig=Rig(R/'ElsaSceneResearch/InstalledGameAssetCheck/fro_elsa/fro_elsa.oct');clip['decoded_sha']=Clip(clip['path'],rig).sha
   assert hashlib.sha256(data).hexdigest()==clip['decoded_sha'],'Full source hash differs'
   before,after=row['before'],row['after'];h=bytes.fromhex(before['header']);actual=bytes.fromhex(after['header'])
   assert row['before_order']<row['order'],'Callback order differs'
   assert before['clock']['address']==after['clock']['address']and before['output']['address']==after['output']['address'],'Node aliases differ'
   assert before['output']['producer']==after['output']['producer']==identity['processor'],'Producer differs'
   item=dict(sequence=row['sequence'],event=row['event'],source=identity['source'],processor=identity['processor'])
   previous=last.get(identity['processor'])
   if previous:
    item['unobserved_changes_since_previous']=[hex(o)for o in fields if previous[o:o+4]!=h[o:o+4]]
    if previous[0x54]!=h[0x54]:item['unobserved_changes_since_previous'].append('0x54')
   if row['event']=='activation':
    duration,parameter=struct.unpack('<2f',bytes.fromhex(row['arguments_hex8']));offset=struct.unpack('<f',bytes.fromhex(row['global_clock_offset_hex4']))[0]
    config=bytes.fromhex(row['config_hex64']);units,p=struct.unpack_from('<if',config,0x24)
    assert duration==f(f(units)*f(1/30))and parameter==p,'Configuration/argument mismatch'
    predicted=activate(h,scalar(after['clock']),duration=duration,curve_parameter=parameter,clock_offset=offset)
    item.update(config_units=units,duration_argument=duration,parameter=parameter,clock_offset=offset)
    activations[row['before_order']]=identity['processor']
   else:
    assert activations.get(row['activation_order'])==identity['processor'],'Missing linked activation'
    value,predicted=step(h,scalar(after['clock']),scalar(before['output']))
    item.update(predicted_factor=value,captured_factor=scalar(after['output']),factor_exact=struct.pack('<f',value)==bytes.fromhex(after['output']['payload']))
   differences=[hex(o)for o in fields if predicted[o:o+4]!=actual[o:o+4]]
   item.update(numeric_field_differences=differences,completion_exact=predicted[0x54]==actual[0x54],pass_=not differences and predicted[0x54]==actual[0x54]and item.get('factor_exact',True))
   rows.append(item);last[identity['processor']]=actual
  except (AssertionError,KeyError,ValueError,TypeError,struct.error)as exc:boundaries.append(dict(sequence=row.get('sequence'),reason=str(exc)))
 return dict(capture_sha256=hashlib.sha256(raw).hexdigest(),checked=len(rows),exact=sum(x['pass_']for x in rows),continuous_numeric_chain=not boundaries and bool(rows)and not any(x.get('unobserved_changes_since_previous')for x in rows),rows=rows,boundaries=boundaries,scope='Independent numeric activation/update replay with captured prior state and empty external callback fixture. Unobserved intervening state writes are reported; no continuous actor lifecycle or rendering parity claim.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--output',required=True);a=p.parse_args();r=analyze(a.capture);Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
