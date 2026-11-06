"""Bounded native finger relationship outputs for the verified PC Elsa rig."""
import hashlib
from pc_skin_palette import *
from native_pc_relationship import run as native_relationship
from native_pc_lean_ik import u

def prepare_fingers(e,diagnostics=None):
 for pid in (165,171,173,175):
  p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid)
  pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')));refs=dict(pairs)
  blob=get(DN[refs['RelationshipData']],'RelationshipDataBlock');blob=bytes(blob)if isinstance(blob,list)else bytes.fromhex(blob['hex'])
  expected=next(r['sha256']for r in json.loads((R/'pc-finger-native-probe.json').read_text())['relationships']if r['processor']==pid)
  if hashlib.sha256(blob).hexdigest()!=expected:raise ValueError('finger relationship source changed')
  inputs=[];input_audit=[]
  for a,node in pairs:
   if not a.startswith('Input['):continue
   value=e.overrides.get(node,{}).get('Value',get(DN[node],'Data'))
   if isinstance(value,list):value=value[0]
   value=float(value)
   if not np.isfinite(value)or abs(value)>100:raise ValueError('finger input outside bounded range')
   inputs.append(value)
   if diagnostics is not None:
    input_audit.append({'attribute':a,'node':node,'path':PC_RIG.paths.get(node),
                        'value':value,'source':'composed_override' if 'Value' in e.overrides.get(node,{}) else 'rig_default'})
  outputs=[node for a,node in pairs if a.startswith('Output[')]
  initial=[]
  for node in outputs:
   fields={c['name']:c['value']for c in next(c for c in DN[node]['children']if c['name']=='Data')['children']}
   initial.append(fields.get('Orientation',[0,0,0,1])+fields.get('Translation',[0,0,0])+[fields.get('Scale',1.)])
  output_audit=[]
  for node,raw in zip(outputs,native_relationship(blob,inputs,len(outputs),initial_outputs=initial)):
   # Preserve the original rotor, including norm drift, for native downstream calls.
   e.raw.cache[node]=list(raw)
   matrix=np.eye(4);matrix[:3,:3]=quat(raw[:4])*raw[7];matrix[:3,3]=raw[4:7];e.cache[node]=matrix
   if diagnostics is not None:
    output_audit.append({'node':node,'path':PC_RIG.paths.get(node),'quaternion':list(map(float,raw[:4])),
                         'translation':list(map(float,raw[4:7])),'scale':float(raw[7]),
                         'quaternion_norm':float(np.linalg.norm(raw[:4]))})
  if diagnostics is not None:
   diagnostics.append({'processor':pid,'relationship_sha256':expected,'inputs':input_audit,'outputs':output_audit,
                       'scope':'Inputs after current preview composition; native relationship output before downstream hierarchy. Initial outputs use serialized rig values. No proof of active game inputs.'})
