import json,random
from pathlib import Path
import numpy as np
from validate_foot_basis_native import native,matrix,SPECS
from native_leg_ik import sha
SPECS['InvertConcatenateChainDilation']=(0x4d2370,'array',8)
rng=random.Random(20261016);rows=[]
for j in range(200):
 vals=[]
 for k in range(2):
  q=np.array([rng.uniform(-1,1) for _ in range(4)]);q/=np.linalg.norm(q);vals.append(list(q)+[rng.uniform(-2,2) for _ in range(3)]+[rng.uniform(.8,1.2)])
 a,b=vals;actual=matrix(native('InvertConcatenateChainDilation',a,b));expected=np.linalg.inv(matrix(a))@np.linalg.inv(matrix(b));error=float(np.max(abs(actual-expected)))
 if error>1e-5:raise AssertionError((j,error,actual,expected))
 rows.append(error)
report={'exe_sha256':sha,'factory':'0x4f1600','wrapper':'0x4ea6c0','allocation':'0x4de320','constructor':'0x4ca6c0','vtable':'0x1b2efc4','execute':'0x4d2370','cases':len(rows),'max_error':max(rows),'formula':'inverse(Input0) @ inverse(Input1); positive uniform Dilation scales .8 to 1.2','scope':'Two-input processor fixtures; does not validate loader or nonuniform Transform metadata.'}
Path('inverse-dilation-native-validation.json').write_text(json.dumps(report,indent=2));print(report)
