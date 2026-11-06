from pathlib import Path
import json,numpy as np
p=Path(__file__).parent
report=[]
data=json.loads((p/'pc-run-hands-corrected-animation.json').read_text())
reference={}
for s in data['clips'][0]['samples']:
 poses={x['bone']:np.array(x['matrix']).reshape(4,4)for x in s['transforms']}
 for child,parent in [('hair01','hairStart'),('hair02','hair01')]:
  relative=np.linalg.inv(poses[parent])@poses[child]
  if child not in reference:reference[child]=relative
  error=float(np.max(abs(relative-reference[child])))
  if error>1e-8:raise ValueError('braid fallback discontinuity')
  report.append({'time':s['time'],'bone':child,'relative_matrix_error':error})
(p/'pc-braid-fallback-continuity-validation.json').write_text(json.dumps({'scope':'bind-relative continuity only; no dynamic braid parity','checks':len(report),'max_error':max(x['relative_matrix_error']for x in report)},indent=2))
print('PASS: braid segments retain constant authored offsets relative to the preceding segment')
