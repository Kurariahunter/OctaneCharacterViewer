"""Bounded replay coverage over all source skin outputs; unsupported paths fail closed."""
import json,collections,traceback,numpy as np
import evaluate_wiiu_head_fixture as h
bindings=json.loads((h.P/'wiiu-skin-associations.json').read_text())
assert len(bindings)==64
results=[]
influences={h.get(n,'Name'):n for n in h.walk(h.r)if n['name']=='Influence'}
for b in bindings:
 p,_=h.producers[b['matrix_node']];typ=h.get(p,'Type');source=h.refs(p)['Input'];samples=[];error=None
 for frame in h.frames:
  e=h.Eval(frame)
  try:
   value=e.run(source)
   if typ=='DilationToMatrix4x4VariantProcessor':packed,m=h.native_matrix(value);m=m.tolist()
   elif typ=='TransformToMatrix4x4VariantProcessor':m=h.matrix_from_transform(value)
   else:raise ValueError('Unsupported matrix producer '+typ)
   assert np.isfinite(m).all()and abs(np.linalg.det(m))>1e-8
   inv=np.array(h.get(influences[b['bone']],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T
   samples.append({'time':frame['time'],'matrix':m,'skin_matrix':(np.array(m)@inv).tolist(),'defaults':e.defaults,'processors':e.operations})
  except (ValueError,AssertionError,KeyError)as ex:
   location=traceback.extract_tb(ex.__traceback__)[-1]
   error=type(ex).__name__+': '+(str(ex)or location.line);break
 results.append({**b,'source_node':source,'matrix_processor':typ,'status':'evaluated'if error is None else 'blocked','blocking_reason':error,'samples':samples})
counts=dict(collections.Counter(r['blocking_reason']for r in results if r['status']=='blocked'))
report={'scope':'Coverage of current bounded PC-helper replay against all 64 Wii U source associations. Evaluated means three source-default clip snapshots, not native Wii U execution, actor initialization or visual parity. Unsupported operations do not fall back to stored outputs.','total':64,'evaluated':sum(r['status']=='evaluated'for r in results),'blocking_reasons':counts,'outputs':results}
(h.P/'wiiu-skin-output-coverage.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items()if k!='outputs'}))
