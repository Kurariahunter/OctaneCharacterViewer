"""Feed mapped Wii U controls to existing PC evaluator only on matching closures."""
import json,sys,numpy as np
from wiiu_pc_graph_adapter import Adapter,P,PC_NODES,get,refs
from evaluate_pc_dress import DressEval
from pc_graph_controls import apply
from pc_finger_controls import prepare_fingers
from native_pc_transform_scale import point
from pc_skin_palette import worlds,parents,PC_RIG
adapter=Adapter();audit=adapter.audit();rows={r['source_node']:r for r in audit['rows']}
bindings=json.loads((P/'wiiu-skin-associations.json').read_text());continuous='--continuous'in sys.argv
suffix='-continuous'if continuous else ''
if continuous:
 from wiiu_clip_sampler import WiiUClip
 frames=WiiUClip().frames()
else:frames=json.loads((P/'elsa-control-quaternions.json').read_text())['samples']

def closure(source,visited=None):
 visited=set()if visited is None else visited
 if source in visited:return set()
 visited.add(source);r=rows.get(source)
 if r is None:return {'unmapped source node '+str(source)}
 issues=set()
 if not r['same_type']or not r['stored_data_equivalent']:issues.add('type/default mismatch '+str(source))
 if not r['processor_equivalent']:issues.add('processor mismatch '+str(source))
 if r['relationship_equivalence']and not r['relationship_equivalence']['byte_equal']:issues.add('relationship mismatch '+str(source))
 producer=adapter.producers.get(source)
 if producer:
  n,output=producer
  if get(n,'Type')=='DynamicChain':issues.add('temporal state not adapted '+str(source))
  for attr,node in refs(n).items():
   if not attr.startswith('Output')and attr!='Aggregate'and node!=source:issues|=closure(node,visited)
 return issues

results=[]
for binding in bindings:
 producer=adapter.producers[binding['matrix_node']][0];source=refs(producer)['Input'];issues=closure(source)
 results.append({**binding,'source_node':source,'pc_node':adapter.mapping.get(source),'closure_issues':sorted(issues),'samples':[],'status':'blocked graph difference'if issues else 'evaluated with existing PC evaluator'})
for frame_index,frame in enumerate(frames):
 e=DressEval();records=adapter.controls(frame);apply(e,records);prepare_fingers(e)
 for row in results:
  if row['status']!='evaluated with existing PC evaluator':continue
  target=row['pc_node']
  if get(PC_NODES[target],'Type')=='Transform':
   raw=e.raw.run(target);origin=point(raw,[0,0,0]);m=np.eye(4);m[:3,3]=origin
   for i in range(3):axis=[0,0,0];axis[i]=1;m[:3,i]=point(raw,axis)-origin
  else:m=np.array(e.run(target))
  assert m.shape==(4,4)and np.isfinite(m).all()
  row['samples'].append({'time':frame['time'],'matrix':m.tolist()})
 if frame_index%30==0:print('PROGRESS',frame_index+1,'/',len(frames),flush=True)
report={'scope':'Mapped Wii U source controls on unchanged existing PC DressEval/raw/finger evaluators from native viewer pipeline. Only matching typed/default/processor/relationship dependency closures admitted. No dynamics-state adaptation, full Wii U actor or renderer parity claim.','graph_nodes_mapped':len(adapter.mapping),'relationship_blobs_checked':sum(r['relationship_equivalence']is not None for r in audit['rows']),'evaluated_outputs':sum(r['status']=='evaluated with existing PC evaluator'for r in results),'outputs':results}
old=json.loads((P/'wiiu-skin-output-coverage.json').read_text());old_by={r['bone']:r for r in old['outputs']if r['status']=='evaluated'};checks=[]
for row in results:
 if row['status']=='evaluated with existing PC evaluator'and row['bone']in old_by:
  previous=old_by[row['bone']]['samples'];previous=[previous[0],previous[-1]]if continuous else previous
  error=max(float(np.max(abs(np.array(min(row['samples'],key=lambda a:abs(a['time']-b['time']))['matrix'])-np.array(b['matrix']))))for b in previous)
  assert error<1e-5,(row['bone'],error);checks.append({'bone':row['bone'],'maximum_error':error})
report['independent_wiiu_graph_crosschecks']=checks
report['sampling']={'samples':len(frames),'nominal_hz':30 if continuous else None,'curve_evaluation':'Original PC native routines on endian-adapted Wii U curves'if continuous else 'Previous approximate three-snapshot fixture','crosscheck_scope':'Only source endpoints compared with old approximate replay; interior uses native timing arithmetic'if continuous else 'All three snapshots'}
(P/('pc-evaluator-wiiu-adapter-check'+suffix+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
# Existing native viewer accepts this PC reference-rig cache without changing its loader.
# It is explicitly NOT a 64-bone Wii U mesh bake. Missing PC outputs inherit bind locals.
parent_map=dict(parents,hair01='hairStart',hair02='hair01');reflect=np.diag([-1,1,1,1]);samples=[]
passed={r['bone']:r for r in results if r['status']=='evaluated with existing PC evaluator'}
bindlocals={name:np.linalg.inv(worlds[parent_map[name]])@bind if parent_map[name]else bind for name,bind in worlds.items()}
for index,frame in enumerate(frames):
 out={name:np.array(row['samples'][index]['matrix'])for name,row in passed.items()};active=set()
 def world(name):
  if name in out:return out[name]
  assert name not in active;active.add(name);parent=parent_map[name]
  out[name]=(world(parent)if parent else np.eye(4))@bindlocals[name];active.remove(name);return out[name]
 transforms=[]
 for name in worlds:
  m=world(name);assert np.isfinite(m).all();transforms.append({'bone':name,'matrix':(reflect@m@reflect).flatten().tolist()})
 samples.append({'time':frame['time'],'transforms':transforms})
cache={'reference_rig_adapter':True,'model_sha256':PC_RIG.sha,'scope':'Wii U source-control adapter on PC reference mesh and unchanged existing PC evaluator. Matching dependency closures only; 49 evaluated shared bones, 13 PC bind-relative fallbacks. No full Wii U mesh or actor playback claim.','sampling':report['sampling'],'source_skin_nodes':{name:row['pc_node']for name,row in passed.items()},'fallback_parents':{name:parent_map[name]for name in worlds if name not in passed},'clips':[{'name':'WiiU_Elsa_Controls_PC_Reference_49_of_62'+suffix,'duration':frames[-1]['time'],'samples':samples}]}
(P/('wiiu-controls-pc-reference-viewer'+suffix+'.json')).write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
print('EXISTING PC EVALUATOR:',report['evaluated_outputs'],'of 64 Wii U output closures evaluated at',len(frames),'times')
for r in results:
 if r['status']=='blocked evaluator':print('BLOCK',r['bone'],r.get('reason'))
