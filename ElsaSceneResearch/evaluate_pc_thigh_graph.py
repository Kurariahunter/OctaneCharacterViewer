"""Installed-PC lean outputs -> bounded source thigh/dress driver graph.

This bridges cached runtime inputs, not decoded clip channels. Optional runtime
inputs stay numeric; input factory semantic mapping is deliberately incomplete.
"""
import json,struct,hashlib
from pathlib import Path
from native_pc_lean_ik import replay,sha
R=Path(__file__).parent
MODEL=R/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct'
assert hashlib.sha256(MODEL.read_bytes()).hexdigest()=='38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d'
def walk(n):
 yield n
 for c in n.get('children',[]):yield from walk(c)
def child(n,k):return next(c for c in n['children'] if c['name']==k)
def get(n,k):return child(n,k)['value']
root=json.loads((R/'installed-elsa-model-graph.json').read_text());dn={int(n['value']):n for n in walk(root) if n['name']=='DataNode'};procs=[n for n in walk(root) if n['name']=='ProcessorNode']
def floats(item,count):return list(struct.unpack('<'+'f'*count,bytes.fromhex(item['payload_prefix_hex64'])[:count*4]))
def identify(snapshot):
 matches=[]
 for p in procs:
  if get(p,'Type')!='IkLean2LinkProcessor':continue
  attrs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
  if all(struct.pack('<3f',*get(dn[attrs[name]],'Data'))==bytes.fromhex(snapshot['inputs'][slot]['payload_prefix_hex64'])[:12] for slot,name in enumerate(['StartPosition','MidPosition','EndPosition'])):matches.append((p,attrs))
 if len(matches)!=1:raise ValueError('Ambiguous/non-PC source geometry')
 return matches[0]
def evaluate(snapshot):
 p,attrs=identify(snapshot);raw=replay(snapshot)
 # Output 0 feeds UnitRotor3dConnection on the traced thigh path. Output 1
 # matches source MidOrientation in the inactive bind instance. Float output
 # is Scale (consumed by ShrinkingVolumeScaleZ in the authored source graph).
 values={attrs['StartOrientation']:list(raw[0]),attrs['MidOrientation']:list(raw[1]),attrs['Scale']:raw[2][0]}
 for op in procs:
  if get(op,'Type')!='UnitRotor3dConnection':continue
  refs=dict(zip(get(op,'DataNodeAttributes'),get(op,'DataNodeRefs')))
  if refs['Input'] in values:values[refs['Output']]=values[refs['Input']][:]
 for op in procs:
  if get(op,'Type')!='DilationComponentProcessorCompose':continue
  refs=dict(zip(get(op,'DataNodeAttributes'),get(op,'DataNodeRefs')))
  if set(refs)!= {'Orientation','Aggregate'} or refs['Orientation'] not in values:continue
  bind=child(dn[refs['Aggregate']],'Data')
  values[refs['Aggregate']]=values[refs['Orientation']]+get(bind,'Translation')+[get(bind,'Scale')]
 return int(p['value']),values
if __name__=='__main__':
 cap=R.parent/'OctaneLiveInspector/Captures/octane_20261017_151848_1792264728047355700.json';d=json.loads(cap.read_text());rows=[];stats={}
 for index,sample in enumerate(d['samples']):
  graph=sample['upstream']['nodes']
  for snapshot in sample['pc_lean_ik_processors']:
   # Require actual membership at a captured dress upstream boundary.
   boundary=next((n for n in graph.values() if n.get('producer_candidate')==snapshot['address'] and n['address']==snapshot['outputs'][0]['node']),None)
   if not boundary:continue
   source,values=evaluate(snapshot);start=identify(snapshot)[1]['StartOrientation']
   connection=next(op for op in procs if get(op,'Type')=='UnitRotor3dConnection' and get(op,'DataNodeRefs')[0]==start);connout=get(connection,'DataNodeRefs')[1]
   liveconn=next(n for n in graph.values() if n.get('operation')=='UnitRotorConnection_4c83f0' and n['inputs'][0]['node']==boundary['address'])
   # Orientation must flow from this exact solver output through the captured
   # rotor connection; then find its validated aggregate compose consumer.
   aggregate=next((n for n in graph.values() if any(x.get('node')==liveconn['address'] for x in n.get('inputs',[])) and n.get('operation')=='DilationComponentVariant'),None)
   target=floats(liveconn,4);q=values[connout];err=min(max(abs(a-b) for a,b in zip(q,target)),max(abs(a+b) for a,b in zip(q,target)))
   cached=floats(boundary,4);observed=floats(snapshot['outputs'][0],4)
   bridge_error=min(max(abs(a-b) for a,b in zip(cached,target)),max(abs(a+b) for a,b in zip(cached,target)))
   separate_error=min(max(abs(a-b) for a,b in zip(cached,observed)),max(abs(a+b) for a,b in zip(cached,observed)))
   row={'same_graph_connection_error':bridge_error,'separate_snapshot_output_error':separate_error,'sample':index,'time_monotonic':sample['time_monotonic'],'runtime_processor':snapshot['address'],'source_processor':source,'source_values':values,'live_rotor_connection':liveconn['address'],'rotation_component_error':err}
   if aggregate:
    aid=next(i for i,v in values.items() if isinstance(v,list) and len(v)==8);actual=floats(aggregate,8);prediction=values[aid];row.update(source_dilation=aid,live_dilation=aggregate['address'],dilation_component_error=max(abs(a-b) for a,b in zip(actual,prediction)),same_graph_dilation_error=max(abs(a-b) for a,b in zip(actual,cached+prediction[4:])))
   rows.append(row)
 for source in sorted({r['source_processor'] for r in rows}):
  group=[r for r in rows if r['source_processor']==source];stats[source]={'samples':len(group),'exact_rotor_samples':sum(r['rotation_component_error']==0 for r in group),'max_rotation_component_error':max(r['rotation_component_error'] for r in group),'max_same_graph_connection_error':max(r['same_graph_connection_error'] for r in group),'max_same_graph_dilation_error':max(r.get('same_graph_dilation_error',0) for r in group),'separate_snapshot_mismatches':sum(r['separate_snapshot_output_error']!=0 for r in group),'aggregate_comparisons':sum('dilation_component_error'in r for r in group),'max_dilation_component_error':max((r.get('dilation_component_error',0) for r in group),default=0)}
 report={'capture':str(cap),'exe_sha256':sha,'scope':'Bounded source adapter: installed-PC native IK -> source rotor connections -> orientation-only Dilation compose preserving authored translation/scale. Uses live cached numeric input slots, not original clip decoding. No full dress anchors, skinning, or Unity clip export. Live reads non-atomic. Runtime optional input factory meanings still unverified.','summary':stats,'rows':rows}
 (R/'pc-thigh-graph-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(stats,indent=2));assert len(rows)==120
 assert all(r['same_graph_connection_error']==0 for r in rows)
 assert all('dilation_component_error' in r for r in rows)
 assert max(r['same_graph_dilation_error'] for r in rows)<0.0002
