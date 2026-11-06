"""Record file declarations and live flags without inferring profile identity."""
import hashlib,json,struct
from pathlib import Path
from collections import Counter
from read_pc_idle_files import R,tuple_decode,tree,walk
ROOT=R.parent
bent=R/'InstalledGameAssetCheck/Bent/fro_elsa/fro_elsa.bent'
root=tree(tuple_decode(bent.read_bytes())['records'])
selected={n['value']:n for n in walk(root)if n['name']=='File' and n.get('value')in ('STANCE','STANCE_PASSIVE','WALKRUN')}
profiles=[]
for p in json.loads((ROOT/'OctaneCharacterViewer/native-preview-profiles.json').read_text(encoding='utf-8'))['profiles']:
 raw=Path(p['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==p['source_sha256']
 records=tuple_decode(raw)['records']
 ranges={name:[r['value']for r in records if r['name']==name] for name in ('MinTime','MaxTime')}
 assert all(len(v)==1 for v in ranges.values())
 names=sorted(set(r['name']for r in records))
 hints=[n for n in names if any(t in n.lower()for t in ('loop','cycle','boundary','wrap','repeat'))]
 entry={'elsa_bm_idle_active':'STANCE','elsa_bm_idle_passive':'STANCE_PASSIVE','grl_bm_walkf':'WALKRUN','grl_bm_runf':'WALKRUN'}[p['name']]
 benthints=[{'name':n['name'],'value':n.get('value')}for n in walk(selected[entry]) if any(t in n['name'].lower()for t in ('loop','cycle','boundary','wrap','repeat'))]
 profiles.append({'profile':p['name'],'source_sha256':p['source_sha256'],'range':ranges,'clip_boundary_name_hints':hints,'bent_entry':entry,'bent_boundary_name_hints':benthints,'boundary_mode_verified':False,
                  'scope':'Name-based declaration audit only; encoded fields or controller defaults can supply flags. No live actor/profile identity join.'})
live=ROOT/'OctaneLiveInspector/Captures/ce_publicationorder_20261019_104217_40197328.jsonl';groups=Counter()
for line in live.read_text(encoding='utf-8').splitlines():
 e=json.loads(line)
 if e['event']=='curve_update':
  h=bytes.fromhex(e['controller_state_hex128']);lo,hi=struct.unpack_from('<2f',h,0x3c)
  groups[(e['ecx'],lo,hi,h[0x62],h[0x63])]+=1
report={'profiles':profiles,'bent_sha256':hashlib.sha256(bent.read_bytes()).hexdigest(),'live_capture_sha256':hashlib.sha256(live.read_bytes()).hexdigest(),
 'live_states':[{'pointer':p,'lower':lo,'upper':hi,'boundary_byte':flags,'state_byte63':state,'observations':n}for (p,lo,hi,flags,state),n in groups.items()],
 'conclusion':'Do not auto-enable boundary byte 0x0E for these four profiles. Live low-nibble configurations include 0x8 and 0xE; high bits and frozen flags also occur. Trace controller configuration/default loader next.'}
(R/'ControllerState/preview-time-boundary-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'profiles_audited':len(profiles),'auto_enable_verified':0,'live_boundary_bytes':sorted(set(k[3]for k in groups))}))
