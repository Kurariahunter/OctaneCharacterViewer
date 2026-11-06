"""Recompare retained coherent game index matrices with current full-palette run."""
import hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
capture=R/'ElsaSceneResearch/ControllerState/active-run-index-palette-comparison.json'
preview=R/'OctaneCharacterViewer/NativePreviews/native-run-full-palette.json'
c=json.loads(capture.read_text());p=json.loads(preview.read_text());assert c['matched_running_pose']
reflect=np.diag([-1.,1.,1.,1.])
def matrix(values):
 assert len(values)==12
 m=np.eye(4);m[:3,:3]=np.array(values[:9]).reshape(3,3).T;m[:3,3]=values[9:]
 return reflect@m@reflect
rows=[]
for hand in c['last']:
 assert hand['coherent'] and len({n['stamp'] for n in hand['nodes'].values()})==1
 side=hand['side'];nodes=hand['nodes'];base=matrix(nodes['Hand']['values'])
 observed=[np.linalg.inv(base)@matrix(nodes[k]['values']) for k in ('Index1','Index2')]
 errors=[]
 for sample in p['clips'][0]['samples']:
  matrices={t['bone']:np.array(t['matrix']).reshape(4,4) for t in sample['transforms']}
  actual=[np.linalg.inv(matrices['Hand_'+side])@matrices[k+'_'+side] for k in ('Index1','Index2')]
  errors.append(dict(time=sample['time'],max_matrix_component_error=max(float(np.max(abs(a-b))) for a,b in zip(observed,actual))))
 maximum=max(r['max_matrix_component_error'] for r in errors)
 assert maximum<1e-5,(side,maximum)
 rows.append(dict(side=side,stamp=nodes['Hand']['stamp'],min_error=min(r['max_matrix_component_error'] for r in errors),max_error=maximum,samples=errors))
report=dict(passed=True,capture=str(capture),capture_sha256=hashlib.sha256(capture.read_bytes()).hexdigest(),preview=str(preview),preview_sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),hands=rows,scope='Historical coherent per-hand game matrices compared in hand-relative space with every pose in the current full-palette forward-run bake. Finger controls are constant through this run; no synchronized body phase or fresh game observation is claimed. Close matrix agreement does not establish mesh/bind/weights or rendered hand parity.')
(R/'ElsaSceneResearch/ControllerState/latest-run-index-capture-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,hands=[dict(side=r['side'],max_error=r['max_error']) for r in rows])))
