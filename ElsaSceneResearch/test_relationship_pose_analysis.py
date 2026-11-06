"""Synthetic native-generated captures test replay and rejection paths."""
import copy,json,struct
from pathlib import Path
from pc_skin_palette import N,DN,get,allnodes
from native_pc_relationship import run
from analyze_relationship_pose_capture import analyze,FLOAT_VT,DILATION_VT
out=Path(__file__).parent/'ControllerState/RelationshipReplayFixtures';out.mkdir(exist_ok=True)
events=[{'event':'start','schema':'di3_relationship_pose_v1','module_base':'0x00400000'}];seq=0
for pid in (165,171,173,175):
 p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid);pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')));refs=dict(pairs)
 blob=get(DN[refs['RelationshipData']],'RelationshipDataBlock');blob=bytes(blob)if isinstance(blob,list)else bytes.fromhex(blob['hex'])
 inputs=[v for a,v in pairs if a.startswith('Input[')];outputs=[v for a,v in pairs if a.startswith('Output[')]
 vals=[-46.9,0.,-46.9,-46.9,0.,-46.9]if len(inputs)==6 else[-14.9]
 vals=[struct.unpack('<f',struct.pack('<f',v))[0]for v in vals]
 initial=[]
 for node in outputs:
  fields={c['name']:c['value']for c in next(c for c in DN[node]['children']if c['name']=='Data')['children']}
  initial.append(fields.get('Orientation',[0,0,0,1])+fields.get('Translation',[0,0,0])+[fields.get('Scale',1.)])
 computed=run(blob,vals,len(outputs),initial_outputs=initial)
 for stage,rows in [('relationship_entry',initial),('relationship_exit',computed)]:
  seq+=1;snapshot={'header_hex104':bytes(104).hex(),'input_count':len(inputs),'output_count':len(outputs),'relationship_blob_hex':blob.hex(),'inputs':{},'outputs':{}}
  for i,v in enumerate(vals):snapshot['inputs']['slot_'+str(i)]={'node':hex(0x100000+i*256),'vtable':hex(FLOAT_VT),'payload_hex':struct.pack('<f',v).hex(),'node_stamp':1,'metadata_stamp':1}
  for i,row in enumerate(rows):snapshot['outputs']['slot_'+str(i)]={'node':hex(0x200000+i*256),'vtable':hex(DILATION_VT),'payload_hex':struct.pack('<8f',*row).hex()}
  events.append({'event':stage,'sequence':seq,'pair_key':str(pid),'snapshot':snapshot})
events.append({'event':'stop','reason':'synthetic'})
def test(name,rows):
 p=out/(name+'.jsonl');p.write_text('\n'.join(json.dumps(e)for e in rows)+'\n',encoding='utf-8');return analyze(p,out/(name+'-analysis.json'))
normal=test('normal',events);assert normal['pass']and normal['matched_pairs']==4 and normal['max_component_error']==0
bad=copy.deepcopy(events)
for e in bad:
 if e['event']=='relationship_exit':e['snapshot']['outputs']['slot_0']['vtable']=hex(FLOAT_VT)
wrong=test('wrong-output-type',bad);assert not wrong['pass']and wrong['matched_pairs']==0
bad=copy.deepcopy(events)
for e in bad:
 if e['event']=='relationship_exit':
  b=bytes.fromhex(e['snapshot']['outputs']['slot_0']['payload_hex']);v=list(struct.unpack('<8f',b));v[4]+=1;e['snapshot']['outputs']['slot_0']['payload_hex']=struct.pack('<8f',*v).hex()
changed=test('changed-output',bad);assert not changed['pass']and changed['matched_pairs']==4
report={'pass':True,'native_generated_pairs':4,'max_normal_component_error':normal['max_component_error'],'rejects_wrong_types':True,'detects_output_changes':True,'scope':'Synthetic fixtures generated and replayed with original EXE evaluator. Self-consistency/tooling validation, not a live game comparison.'}
(out.parent/'relationship-replay-analyzer-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
