"""Interpret entry-state snapshots; do not mistake observed order for thread causality."""
import json,struct,hashlib,sys
from pathlib import Path
from collections import Counter
from exe_reader import disasm
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def decode(e):
 h=bytes.fromhex(e['clock_hex88']);assert len(h)==88
 def ui(o):return struct.unpack_from('<I',h,o)[0]
 def fl(o):return struct.unpack_from('<f',h,o)[0]
 return {'token':ui(0),'raw_delta_ms':ui(4),'effective_delta_ms':ui(0x10),'total_ms':ui(0x18),'seconds':fl(0x24),'delta_seconds':fl(0x1c),'mode':ui(0x28),'cap_ms':ui(0x34),'smoothing_parameter':fl(0x38),'transition':h[0x51]}
results=[]
for arg in sys.argv[1:]:
 p=Path(arg);raw=p.read_bytes();es=[json.loads(l) for l in raw.decode('utf-8').splitlines() if l.strip()]
 assert es[0]['schema']=='di3_clock_order_v1'
 base=int(es[0]['module_base'],16);clock=[];curve=[];last=None;checks=[]
 for e in es:
  kind=e['event']
  if kind not in ('clock_update','curve_update','run'):continue
  state=decode(e)
  assert state['seconds']==f32(state['total_ms']*.001)
  assert state['delta_seconds']==f32(state['effective_delta_ms']*f32(.001))
  if kind=='clock_update':
   assert e['is_shared_clock'] and int(e['ecx'],16)==base+0x22018f0-0x400000
   clock.append((e,state));last=state
  elif kind=='curve_update':
   h=bytes.fromhex(e['controller_state_hex128']);assert len(h)==128
   cached_clock=struct.unpack_from('<f',h,0x50)[0];cached_token=struct.unpack_from('<I',h,0x5c)[0]
   curve.append({'sequence':e['sequence'],'state_pointer':e['ecx'],'clock':state,'cached_seconds':cached_clock,'cached_token':cached_token,'frozen':bool(h[0x63]&1),
                 'after_observed_clock_entry':last is not None,'token_advance_since_clock_entry':None if last is None else (state['token']-last['token'])&0xffffffff})
 for (_,a),(_,b) in zip(clock,clock[1:]):
  check={'token_increment':(b['token']-a['token'])&0xffffffff,'accumulation_matches':b['total_ms']==((a['total_ms']+b['effective_delta_ms'])&0xffffffff),
         'normal_delta_matches':b['effective_delta_ms']==min(b['raw_delta_ms'],b['cap_ms']) if b['mode']==3 and not b['transition'] else None}
  assert check['token_increment']==1 and check['accumulation_matches'] and check['normal_delta_matches'] is True
  checks.append(check)
 results.append({'capture':str(p.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'counts':dict(Counter(e['event'] for e in es)),
  'returns':{k:dict(Counter(e.get('return_preferred') for e in es if e['event']==k)) for k in ('clock_update','curve_update','run')},
  'clock_states':[s for _,s in clock],'clock_transition_checks':checks,'curve_observations':curve,
  'curve_token_advances':dict(Counter(str(c['token_advance_since_clock_entry']) for c in curve)),
  'unique_curve_states':len(set(c['state_pointer'] for c in curve)),'stop':es[-1],
  'limitations':'Entry state only; no thread ID. Per-site caps remove clock/curve breakpoints independently. RUN zero hits applies only to bounded captures, not all gameplay paths.'})
out=Path(__file__).parent/'ControllerState'
(out/'clock-order-capture-analysis.json').write_text(json.dumps({'pass':True,'captures':results},indent=2)+'\n',encoding='utf-8')
(out/'active_clock_and_lazy_getter.txt').write_text(disasm(0x43E930,0x75)+'\n'+disasm(0x48D2B0,0x23),encoding='utf-8')
print(json.dumps([{'capture':Path(r['capture']).name,'counts':r['counts'],'clock_pairs':len(r['clock_transition_checks']),'curve_token_advances':r['curve_token_advances'],'unique_states':r['unique_curve_states']} for r in results]))
