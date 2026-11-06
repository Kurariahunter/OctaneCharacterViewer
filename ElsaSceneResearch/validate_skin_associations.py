"""Resolve explicit source skin associations; fail closed on ambiguous names."""
import sys,json
from pathlib import Path
R=Path(__file__).parent
sys.path.insert(0,str(Path(r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation\YodaAnimationProbe\analysis_dependencies')))
from evaluate_elsa_head import T,N,DN,PROD,get,allnodes,stored
from decode_header_paths import paths
import numpy as np
labels=get(N,'HeaderStrings');indices=get(N,'HeaderStringIndices')
names={i:labels[indices[get(n,'Header')-1]] for i,n in DN.items() if get(n,'Header')}
bones=json.loads((R/'elsa-preview-model.json').read_text())['bones'];rows=[]
for a in allnodes(T,'Association'):
 if get(a,'Type')!='SkinInfluence':continue
 path=get(a,'NodeName');parts=path.split('|');typ,name=parts[-2:]
 candidates=[i for i,n in DN.items() if paths.get(i)==path]
 row={'association':a['value'],'source_path':path,'influence_refs':get(a,'InfluenceRefs'),'candidate_nodes':candidates}
 if len(candidates)==1:
  i=candidates[0];row['data_node']=i;row['data_type']=get(DN[i],'Type');assert row['data_type'] in ('Transform','Dilation')
  p=PROD.get(i);row['producer']=None if p is None else {'type':get(p[0],'Type'),'attributes':get(p[0],'DataNodeAttributes'),'refs':get(p[0],'DataNodeRefs')}
  for influence in row['influence_refs']:
   b=bones[influence];row['bone_name']=b['name'];row['stored_world_bind_max_error']=float(np.max(np.abs(stored(DN[i])-np.array(b['world']).reshape(4,4))))
 rows.append(row)
report={'scope':'Complete HeaderLayout ancestry decoded; exact Association NodeName matched. Transform is a header group name, not a requirement that the resolved payload type is Transform; 19 skin outputs are Dilation. Stored world values are not evaluated animation or bind transforms.','associations':rows,'unique_matches':sum(len(x['candidate_nodes'])==1 for x in rows),'total':len(rows)}
(R/'skin-association-validation.json').write_text(json.dumps(report,indent=2))
print('unique',report['unique_matches'],'total',len(rows))
for x in rows:
 if any(s in x['source_path'] for s in ('Knee_','Ankle_','Hips|')):print(json.dumps(x))
