import hashlib,json
from pc_skin_palette import *
from native_pc_relationship import run
from read_pc_idle_files import Clip
rows=[]
for pid in [165,171,173,175]:
 p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid);pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')));refs=dict(pairs)
 raw=get(DN[refs['RelationshipData']],'RelationshipDataBlock');blob=bytes(raw)if isinstance(raw,list)else bytes.fromhex(raw['hex']);inputs=[v for a,v in pairs if a.startswith('Input[')];outs=[v for a,v in pairs if a.startswith('Output[')]
 cases=[]
 for value in [0,25,50,100]:
  vals=[value]*len(inputs);outputs=run(blob,vals,len(outs));cases.append({'inputs':vals,'outputs':outputs})
 rows.append({'processor':pid,'sha256':hashlib.sha256(blob).hexdigest(),'inputs':[{'node':i,'path':PC_RIG.paths[i],'default':get(DN[i],'Data')}for i in inputs],'outputs':outs,'cases':cases})
 print(pid,len(inputs),len(outs),'native cases passed')
clips=[]
for name,folder in [('elsa_bm_idle_passive','IdleMotions'),('grl_bm_runf','RunMotions'),('grl_bm_run_upbody_add','RunMotions')]:
 c=Clip(next((R/'InstalledGameAssetCheck'/folder).rglob(name+'.oct')),PC_RIG)
 tracks=[]
 for record in c.sample(0).values():
  if record['source_node'] in [291,292,293,294,295,296,311,312,313,314,315,316,330,335]:tracks.append(record)
 clips.append({'name':name,'finger_tracks':tracks})
(R/'pc-finger-native-probe.json').write_text(json.dumps({'scope':'Original native function synthetic scalar sweeps; not game pose validation','relationships':rows,'clips':clips},indent=2))
print(json.dumps(clips,indent=2))
