import json,numpy as np
from pathlib import Path
from evaluate_native_skin import *
r=Path('.');d=json.loads((r/'elsa-knee-dress-control-samples.json').read_text());old=json.loads((r/'native-skin-clip-validation.json').read_text());rows=[]
for c in d['clips']:
 frames=[]
 for f in c['samples']:
  e=FootEval();e.overrides={int(k):v for k,v in f['controls'].items()};n=NativeSkinEval(e);world={}
  for name,i in [('UpperDress_Left',650),('UpperDress_Right',655)]:world[name]=(np.diag([-1,1,1,1])@affine(n.run(i))@np.diag([-1,1,1,1])).flatten().tolist()
  frames.append({'time':f['time'],'worlds':world})
 rows.append({'name':c['name'],'duration':c['duration'],'samples':frames})
for c in rows:
 print(c['name'],[(k,max(float(np.max(abs(np.array(f['worlds'][k])-np.array(c['samples'][0]['worlds'][k])))) for f in c['samples'])) for k in c['samples'][0]['worlds']])
(r/'native-knee-upper-dress-samples.json').write_text(json.dumps({'scope':'Source UpperDress world outputs only. Dynamic lower dress intentionally excluded.','clips':rows},separators=(',',':')))
