import json
from pc_skin_palette import *
from evaluate_pc_arms import Eval
rows=[]
for bone in worlds:
 if not any(s in bone.lower() for s in ['hair','thumb','index','middle']):continue
 node=skin[bone];seen=set();pending=[node];deps=[]
 while pending:
  i=pending.pop()
  if i in seen:continue
  seen.add(i)
  if i in PROD:
   p,a=PROD[i];deps.append({'node':i,'type':get(p,'Type'),'output':a});pending += [v for a,v in zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')) if v!=i and not a.startswith('Output')]
 try:
  m=Eval().run(node);result={'shape':list(m.shape)}
 except Exception as e:result={'error':str(e)}
 rows.append({'bone':bone,'node':node,'path':PC_RIG.paths[node],'evaluation':result,'dependencies':deps,'leaf_controls':[{'node':i,'path':PC_RIG.paths.get(i),'type':get(DN[i],'Type')}for i in sorted(seen)if i not in PROD]})
(R/'pc-hand-hair-audit.json').write_text(json.dumps(rows,indent=2))
for row in rows:print(row['bone'],row['node'],row['evaluation'])
print('related paths')
for i,path in PC_RIG.paths.items():
 if any(s in path.lower() for s in ['finger','thumb','index','middle','hair']):print(i,path)
