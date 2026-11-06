"""Compare native Dilation matrix output to viewer convention on captured inputs."""
import json,random,struct
from pathlib import Path
import numpy as np
from native_pc_skin_matrix import dilation_matrix,matrix
from evaluate_pc_arms import quat

R=Path(__file__).parent
capture=R.parent/'OctaneLiveInspector/Captures/ce_fingerworld_20261019_215028_80287281.jsonl'
cases=[]
for e in map(json.loads,capture.read_text().splitlines()):
    if e['event']=='finger_world_dilation':
        cases.append(('captured_world_dilation',list(struct.unpack('<8f',bytes.fromhex(e['output']['payload_hex'])))))
rng=random.Random(1927)
for _ in range(100):
    q=np.array([rng.uniform(-1,1)for _ in range(4)]);q/=np.linalg.norm(q)
    cases.append(('synthetic',q.tolist()+[rng.uniform(-100,100)for _ in range(3)]+[rng.uniform(.5,1.5)]))
rows=[]
for kind,v in cases:
    packed=dilation_matrix(v);m=np.eye(4);m[:3,:3]=np.array(packed[:9]).reshape(3,3).T;m[:3,3]=packed[9:]
    expected=np.eye(4);expected[:3,:3]=quat(v[:4])*v[7];expected[:3,3]=v[4:7]
    unit_assumption_error=float(np.max(abs(m-expected)))
    # Native helper48D9E0 uses the quadratic rotor formula, retaining norm drift.
    expected[:3,:3]+=np.eye(3)*(sum(x*x for x in v[:4])-1)*v[7]
    rows.append(dict(kind=kind,error=float(np.max(abs(m-expected))),unit_assumption_error=unit_assumption_error))
report=dict(execute='0x4DEE10',vtable='0x1B2F544',cases=len(rows),captured_inputs=sum(r['kind']=='captured_world_dilation'for r in rows),max_error=max(r['error']for r in rows),
    max_viewer_unit_assumption_error=max(r['unit_assumption_error']for r in rows),
    scope='Original native converter versus quadratic rotor matrix formula retaining quaternion norm drift on31 recorded world Dilation payloads and100 synthetic unit rotations/positive uniform scales. Unit-assumption viewer difference reported separately. Captured game matrix outputs from this variant are not yet available.',rows=rows)
report['pass']=report['max_error']<2e-5
(R/'ControllerState/dilation-skin-matrix-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='rows'}));assert report['pass']
