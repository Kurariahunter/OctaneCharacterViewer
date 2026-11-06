"""Native rotor/Euler round trips and native scalar products for overlays."""
import json,random,math,struct
from pathlib import Path
from native_pc_forearm_twist import euler
from native_pc_clip_math import rotation
from native_pc_dress_math import call
from native_pc_lean_ik import sha
from evaluate_pc_arms import quat
import numpy as np
rng=random.Random(20261022);maximum=0.;product_error=0.
fixtures=[[0.,0.,0.],[math.pi/2,0.,0.],[-math.pi/2,0.,0.]]
fixtures += [[rng.uniform(-math.pi,math.pi) for _ in range(3)] for _ in range(100)]
for angles in fixtures:
 q=rotation(angles);out=euler(q);recovered=rotation(out)
 error=float(np.max(abs(quat(q)-quat(recovered))));maximum=max(maximum,error)
 assert error<1e-4,(angles,out,error)
 a,b=rng.uniform(-100,100),rng.uniform(-2,2)
 f=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
 actual=call(0x52d540,[[a],[b]],'array',1)[0];expected=f(f(a)*f(b));delta=abs(actual-expected);product_error=max(product_error,delta);assert delta==0.
report=dict(passed=True,exe_sha256=sha,roundtrip_cases=len(fixtures),max_rotation_matrix_error=maximum,max_float_product_error=product_error,rotor_execute='0x4DF750 -> 0x40D8B0',multiply_execute='0x52D540',scope='Original PC rotor-to-Euler variant and existing native convention2 Euler-to-rotor round trips, plus explicit two-input FloatMultiply fixtures. Tests orientation equivalence, not identical Euler angles or runtime scene parity.')
(Path(__file__).parent/'ControllerState/forearm-twist-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
