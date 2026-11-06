"""Compare live relationship inputs/outputs with extracted idle source and rig."""
import hashlib,json
from pathlib import Path
from pc_skin_palette import PC_RIG,N,DN,get,allnodes
from read_pc_idle_files import Clip
from native_pc_relationship import run
root=Path(__file__).parent
live=json.loads((root/'ControllerState/live-relationship-pose-analysis.json').read_text(encoding='utf-8'))
assert live['matched_pairs']>0 and live['pass']
catalog=json.loads((root.parent/'OctaneCharacterViewer/native-preview-profiles.json').read_text(encoding='utf-8'))
profile=next(p for p in catalog['profiles']if p['name']=='elsa_bm_idle_active')
assert hashlib.sha256(Path(profile['source']).read_bytes()).hexdigest()==profile['source_sha256']
records=Clip(profile['source'],PC_RIG).sample(0)
by_node={r['source_node']:r for r in records.values()if r['source_node']is not None}
rows=[]
for pair in live['pairs']:
 pid=pair['relationship_processor_in_file'];p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid)
 refs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
 inputs=[v for a,v in refs if a.startswith('Input[')];outputs=[v for a,v in refs if a.startswith('Output[')]
 values=[by_node[node]['channels']['10'][0]for node in inputs]
 assert values==pair['inputs'],'Active-idle phase-zero input mismatch'
 initial=[]
 for node in outputs:
  fields={c['name']:c['value']for c in next(c for c in DN[node]['children']if c['name']=='Data')['children']}
  initial.append(fields.get('Orientation',[0,0,0,1])+fields.get('Translation',[0,0,0])+[fields.get('Scale',1.)])
 v=get(DN[dict(refs)['RelationshipData']],'RelationshipDataBlock');blob=bytes(v)if isinstance(v,list)else bytes.fromhex(v['hex'])
 replay=run(blob,values,len(outputs),initial_outputs=initial)
 error=max(abs(a-b)for actual,expected in zip(pair['captured_outputs'],replay)for a,b in zip(actual,expected))
 assert error<=2e-5
 rows.append({'processor':pid,'entry_sequence':pair['entry_sequence'],'all_file_inputs_match':True,'rig_initialized_output_max_error':error})
report={'pass':True,'live_capture_sha256':live['sha256'],'source_sha256':profile['source_sha256'],'profile':profile['name'],'source_phase':0,
 'pairs':rows,'max_output_error':max(r['rig_initialized_output_max_error']for r in rows),
 'scope':'Active-idle phase-zero scalar pattern and relationship-local outputs only. Does not identify actor uniquely, compare world-space skinning, or validate run source/layer composition.'}
(root/'ControllerState/live-idle-relationship-comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'pairs':len(rows),'max_output_error':report['max_output_error']}))
