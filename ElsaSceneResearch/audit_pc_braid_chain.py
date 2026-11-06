import json
from pc_skin_palette import *
rows=[]
for pid in [548,550,551]:
 p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid);refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
 rows.append({'processor':pid,'refs':refs,'authored_data':{key:DN[refs[key]]for key in ['ChainData','Particle[0]','Particle[1]']},'constraint_producer':PROD.get(refs['ConstraintPoint[0]'])})
(R/'pc-braid-chain-source-audit.json').write_text(json.dumps(rows,indent=2))
for row in rows:
 print('chain',row['processor'])
 for key,n in row['authored_data'].items():print(key,[(c['name'],c['value'])for c in n['children']if c['name']not in ('Header',)])
 print('constraint',row['constraint_producer'])
