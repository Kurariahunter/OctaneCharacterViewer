"""Bounded live entry ordering and normal clock arithmetic checks."""
import hashlib,json,struct,sys
from pathlib import Path
from collections import Counter
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def clock(e):
 h=bytes.fromhex(e['clock_hex88']);assert len(h)==88
 def ui(o):return struct.unpack_from('<I',h,o)[0]
 def fl(o):return struct.unpack_from('<f',h,o)[0]
 s={'token':ui(0),'raw_ms':ui(4),'effective_ms':ui(0x10),'total_ms':ui(0x18),'seconds':fl(0x24),'delta_seconds':fl(0x1c),'mode':ui(0x28),'cap_ms':ui(0x34),'smoothing':fl(0x38),'transition':h[0x51]}
 assert s['seconds']==f32(s['total_ms']*.001)
 assert s['delta_seconds']==f32(s['effective_ms']*f32(.001))
 return s
p=Path(sys.argv[1]);raw=p.read_bytes();es=[json.loads(l)for l in raw.decode('utf-8').splitlines() if l.strip()]
assert es[0]['schema']=='di3_publication_order_v1'
base=int(es[0]['module_base'],16);latest_clock=None;latest_pub=None;pubs=[];curves=[];clocks=[]
for e in es:
 kind=e['event']
 if kind not in ('clock_update','publish_dispatch','curve_update'):continue
 s=clock(e)
 ret=int(e['return_address'],16)-base+0x400000
 assert ret==int(e['return_preferred'],16)
 if kind=='clock_update':
  assert e['is_shared_clock'] and int(e['ecx'],16)==base+0x22018f0-0x400000
  assert ret==0x43e954
  if clocks:
   a=clocks[-1]['state'];assert (s['token']-a['token'])&0xffffffff==1
   assert s['total_ms']==(a['total_ms']+s['effective_ms'])&0xffffffff
  latest_clock={'sequence':e['sequence'],'state':s};clocks.append(latest_clock)
 elif kind=='publish_dispatch':
  assert ret==0x13955ef and latest_clock is not None
  a=latest_clock['state'];assert (s['token']-a['token'])&0xffffffff==1
  assert s['total_ms']==(a['total_ms']+s['effective_ms'])&0xffffffff
  assert s['mode']==3 and not s['transition'] and s['effective_ms']==min(s['raw_ms'],s['cap_ms'])
  latest_pub={'sequence':e['sequence'],'state':s,'preceding_clock_entry':latest_clock['sequence'],'return_preferred':e['return_preferred']};pubs.append(latest_pub)
 else:
  assert ret==0x48d2ce and latest_pub is not None
  assert s==latest_pub['state']
  h=bytes.fromhex(e['controller_state_hex128']);assert len(h)==128
  cached_token=struct.unpack_from('<I',h,0x5c)[0]
  curves.append({'sequence':e['sequence'],'state_pointer':e['ecx'],'preceding_publication_entry':latest_pub['sequence'],'token':s['token'],'cached_token':cached_token,'cached_seconds':struct.unpack_from('<f',h,0x50)[0],'frozen':bool(h[0x63]&1)})
report={'pass':True,'capture':str(p.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'counts':dict(Counter(e['event']for e in es)),
 'clock_entry_pairs':len(clocks)-1,'publication_checks':len(pubs),'curve_publication_matches':len(curves),'publications':pubs,'curve_observations':curves,'unique_curve_states':len(set(c['state_pointer']for c in curves)),
 'stop':es[-1],'scope':'Entry observation ordering only; no thread ID or publication-exit snapshot. Per-site caps censor later events. Full shared-clock arithmetic checked at captured publication states; no frame-rate inference.'}
out=Path(__file__).parent/'ControllerState/publication-order-capture-analysis.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k]for k in ('pass','counts','clock_entry_pairs','publication_checks','curve_publication_matches','unique_curve_states')}))
