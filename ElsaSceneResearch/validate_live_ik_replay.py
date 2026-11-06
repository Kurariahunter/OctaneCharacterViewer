"""Replay captured updating IK inputs through the original native solver."""
import json,struct,math
from pathlib import Path
import numpy as np
from native_leg_ik import native_ik,sha
from evaluate_elsa_head import N,DN,get,allnodes
R=Path(__file__).parent;cap=Path('F:/DisneyInfinityPortalTest/OctaneLiveInspector/Captures/octane_20261017_000852_1792210132334652700.json');d=json.loads(cap.read_text());order=[12,2,1,10,3,8,9,7,6,5,4,0,11]
# Associate updating chain network references using captured anchor headers.
networks=set()
for c in d['samples'][0]['chains']:
 if c and c['frame_raw']-c['last_frame_raw'] in [0,1]:networks.add(hex(struct.unpack_from('<I',bytes.fromhex(c['anchor_node_header_hex']),0x1c)[0]))
rows=[]
for candidate in d['ik_candidates']:
 if not any(any(bytes.fromhex(x['payload_hex'])) for x in candidate['inputs'] if x['source_attribute']=='InputTargetTranslation'):continue
 matches=[]
 source_by_attr={x['source_attribute']:bytes.fromhex(x['payload_hex']) for x in candidate['inputs']}
 for p in allnodes(N,'ProcessorNode'):
  if get(p,'Type')!='IK2BRPLengthSquashZConstraint':continue
  checks=[]
  for attr,node in zip(get(p,'DataNodeAttributes')[:13],get(p,'DataNodeRefs')[:13]):
   if 'Initial' not in attr:continue
   val=get(DN[node],'Data');vals=val if isinstance(val,list) else [val]
   checks.append(source_by_attr[attr]==struct.pack('<'+'f'*len(vals),*vals))
  if checks and all(checks):matches.append(int(p['value']))
 samples=[]
 for index,frame in enumerate(d['samples']):
  c=next(x for x in frame['ik_processors'] if x and x['address']==candidate['address']);runtime=[list(struct.unpack('<'+'f'*x['float_count'],bytes.fromhex(x['payload_hex']))) for x in c['inputs']];source=[None]*13
  for slot,j in enumerate(order):source[j]=runtime[slot]
  result=native_ik(source,c['flags_raw']);actual=[list(struct.unpack('<4f',bytes.fromhex(x['payload_hex16']))) for x in c['outputs']];expected=[result[i] for i in [1,0,3,2]];errors=[]
  for j,(a,b) in enumerate(zip(expected,actual)):
   a=np.array(a);b=np.array(b)
   if j<2:
    err=float(min(np.max(abs(a-b)),np.max(abs(a+b))));dot=abs(float(np.dot(a/np.linalg.norm(a),b/np.linalg.norm(b))));angle=math.degrees(2*math.acos(min(1,dot)))
   else:err=float(np.max(abs(a-b)));angle=None
   errors.append({'runtime_output':j,'max_component_error':err,'rotation_angle_degrees':angle})
  samples.append({'sample':index,'twist':runtime[2][0],'target':runtime[0],'errors':errors})
 row={'address':candidate['address'],'shares_updating_chain_network':bool(set(x['network_reference_raw'] for x in candidate['outputs']) & networks),'matching_source_processors_by_initial_geometry':matches,'network_references':list(set(x['network_reference_raw'] for x in candidate['outputs'])),'samples':samples,'max_output_component_error':max(e['max_component_error'] for s in samples for e in s['errors']),'max_rotation_angle_degrees':max(e['rotation_angle_degrees'] for s in samples for e in s['errors'] if e['rotation_angle_degrees'] is not None),'twist_range':[min(s['twist'] for s in samples),max(s['twist'] for s in samples)]};rows.append(row);print({k:v for k,v in row.items() if k!='samples'},flush=True)
report={'capture':str(cap),'exe_sha256':sha,'scope':'Non-atomic live IK input/output replay through original native solver. Network references compared explicitly; lack of a shared reference leaves actor association unresolved. Source side candidates use exact initial geometry signatures. Does not identify clip name or prove synchronized frame snapshots.','updating_chain_networks':sorted(networks),'solvers':rows}
(R/'live-ik-replay-validation.json').write_text(json.dumps(report,indent=2))
