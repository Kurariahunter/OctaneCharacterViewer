"""Native Vector transform against matrix algebra, including signed scale."""
import json,random,math
from pathlib import Path
import numpy as np
from native_pc_eye_vector import transform
from native_pc_lean_ik import sha
from evaluate_pc_arms import quat
rng=random.Random(20261022);maximum=0.;translation_error=0.
for _ in range(100):
 q=[rng.uniform(-1,1) for _ in range(4)];length=math.sqrt(sum(v*v for v in q));q=[v/length for v in q]
 v=[rng.uniform(-3,3) for _ in range(3)];scale=rng.choice((-2.,-.5,0.,.5,1.,2.))
 converter=q+[rng.uniform(-10,10) for _ in range(3)]+[scale]
 actual=np.array(transform(v,converter));expected=quat(q)@np.array(v)*scale
 error=float(max(abs(actual-expected)));maximum=max(maximum,error);assert error<5e-6
 changed=transform(v,q+[100.,-200.,300.]+[scale]);delta=float(max(abs(actual-changed)));translation_error=max(translation_error,delta);assert delta==0.
report=dict(passed=True,exe_sha256=sha,cases=100,routine='0x4D3A50 -> 0x4C37D0',registration='0x501A43 -> factory0x4D3700 -> 0x4C36E0 -> constructor0x4B6B50 -> vtable0x1B2C3B4 execute+0x40',max_matrix_error=maximum,max_translation_influence=translation_error,scope='Original PC operation with explicit Vector/Dilation type selection and unit rotor, signed uniform scales including zero. Vector is rotated and scaled; converter translation has no effect. Not eye graph or game parity.')
(Path(__file__).parent/'ControllerState/eye-vector-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
