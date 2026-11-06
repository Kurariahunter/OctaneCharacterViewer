"""Typed cached finger values, inverse mapping and source-pattern comparison."""
import json,hashlib,struct,sys
from pathlib import Path
from collections import Counter
from analyze_runtime_map_capture import analyze
from read_pc_idle_files import Clip
from pc_skin_palette import PC_RIG
def fl(s):return struct.unpack('<f',bytes.fromhex(s))[0] if s else None
def table(t):
 assert t['complete'];b=bytes.fromhex(t['hex']);assert len(b)==2*t['count']
 return struct.unpack('<'+'H'*t['count'],b)
p=Path(sys.argv[1]);raw=p.read_bytes();es=[json.loads(l)for l in raw.decode('utf-8').splitlines()if l.strip()]
assert es[0]['schema']=='di3_finger_inputs_v1'
mapping=analyze(es);maps={e['map_key']:e for e in es if e['event']=='runtime_map'}
groups={};boundaries=Counter();checked=0
for e in es:
 for c in e.get('contributions',{}).values():
  for label,row in c.get('finger_ports',{}).items():
   if not isinstance(row,dict):continue
   if 'payload_hex4'not in row:boundaries[row.get('boundary','no payload')]+=1;continue
   assert row['node_rtti_candidate']=='.?AV?$TypedDataNode@M@Samurai@@'
   m=maps[c['mapping_key']];forward=table(m['tables']['LocalToPortIndices']);reverse=table(m['tables']['PortToLocalIndices'])
   port,index=row['port'],row['source_index'];assert reverse[port]==index and forward[index]==port
   checked+=1;key=(c['controller'],label)
   g=groups.setdefault(key,{'controller':key[0],'label':label,'port':port,'mapping_key':c['mapping_key'],'observations':0,'fresh':0,'stale':0,'values':set(),'fresh_values':set(),'factor2c':set(),'factor30':set(),'filter_coefficients':set()})
   value=fl(row['payload_hex4']);fresh=row.get('node_stamp')is not None and row.get('metadata_stamp')is not None and row['node_stamp']==row['metadata_stamp']
   g['observations']+=1;g['fresh'if fresh else'stale']+=1;g['values'].add(value)
   if fresh:g['fresh_values'].add(value)
   g['factor2c'].add(1. if c.get('factor_2c_default_one')else fl(c.get('factor_2c_hex4')))
   g['factor30'].add(1. if c.get('factor_30_default_one')else fl(c.get('factor_30_hex4')))
   g['filter_coefficients'].add(1. if row.get('filter_default_one')else fl(row.get('filter_coefficient_hex4')))
for g in groups.values():
 for k,v in list(g.items()):
  if isinstance(v,set):g[k]=sorted(v,key=lambda x:(x is None,x or 0))
catalog=json.loads((Path(__file__).parent.parent/'OctaneCharacterViewer/native-preview-profiles.json').read_text(encoding='utf-8'))
patterns=[]
ports=sorted({g['port']for g in groups.values()})
for profile in catalog['profiles']:
 clip=Clip(profile['source'],PC_RIG);sample=clip.sample(0)
 patterns.append({'profile':profile['name'],'source_sha256':profile['source_sha256'],'phase_zero_scalars':{str(port):sample.get(port,{}).get('channels',{}).get('10')for port in ports}})
report={'capture':str(p.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'counts':dict(Counter(e['event']for e in es)),
 'existing_map_checks':{'checked':mapping['checked_contributions'],'matching':mapping['matching'],'errors':mapping['errors']},
 'typed_port_map_checks':checked,'boundaries':dict(boundaries),'groups':list(groups.values()),'phase_zero_file_patterns':patterns,'stop':es[-1],
 'scope':'Cached source snapshots, not final scalar blend outputs. Equal metadata stamps checked separately from stale snapshots. File-pattern equality is not unique actor/source identity. Current-factor presence at a different output port does not prove complete finger contribution scheduling.'}
(Path(sys.argv[2])if len(sys.argv)>2 else Path(__file__).parent/'ControllerState/live-finger-input-analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'typed_port_map_checks':checked,'groups':len(groups),'fresh':sum(g['fresh']for g in groups.values()),'stale':sum(g['stale']for g in groups.values()),'map_checks':report['existing_map_checks'],'boundaries':dict(boundaries)}))
