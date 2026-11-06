"""Record actual evaluator dependencies and omitted clip bindings; no pose edits."""
import json
from pathlib import Path
from evaluate_dress import DressEval
from evaluate_elsa_head import DN,PROD,get
R=Path(__file__).parent
source=json.loads((R/'elsa-knee-dress-control-samples.json').read_text())
mapping=json.loads((R/'elsa-control-mapping.json').read_text())
rows=[]
for clip in source['clips']:
 e=DressEval();e.overrides={int(k):v for k,v in clip['samples'][0]['controls'].items()}
 seen=set();edges=[];stack=[]
 def wrap(fn,kind):
  def run(i):
   seen.add(i)
   if stack:edges.append([stack[-1],i,kind])
   stack.append(i)
   try:return fn(i)
   finally:stack.pop()
  return run
 e.run=wrap(e.run,'graph');e.native.run=wrap(e.native.run,'native')
 outputs={}
 for i in [650,655,660,668,738,753]:outputs[str(i)]=list(e.native.run(i))
 bindings=[x for x in mapping['rows'] if x['data_node'] in seen]
 missing=[x for x in bindings if x['data_node'] not in e.overrides]
 producers=[]
 for i in sorted(seen):
  p=PROD.get(i)
  producers.append({'node':i,'type':get(DN[i],'Type'),'producer':int(p[0]['value']) if p else None,'operation':get(p[0],'Type') if p else None,'attribute':p[1] if p else None})
 rows.append({'clip':clip['name'],'visited':sorted(seen),'edges':edges,'bindings':bindings,'unselected_bindings':missing,'nodes':producers,'outputs':outputs})
 print(clip['name'],'visited',len(seen),'unselected',[(x['port'],x['data_node'],x['basis']) for x in missing])
(R/'dress-reference-dependency-audit.json').write_text(json.dumps({'scope':'Actual first-frame evaluator call dependencies, not full runtime graph scheduling. No source modifications.','clips':rows},indent=2))
