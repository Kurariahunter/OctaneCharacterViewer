"""Native no-offset scaled connection and actual PC facial graph smoke tests."""
import json,random,math,struct
from pathlib import Path
from native_pc_scaled_connection import connect,sha
R=Path(__file__).parent;rng=random.Random(20261022);maximum=0.
f=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
for i in range(100):
 q=[rng.uniform(-1,1)for _ in range(4)];length=math.sqrt(sum(x*x for x in q));q=[v/length for v in q]
 scale=[rng.uniform(.2,3)for _ in range(4)];unscale=[rng.uniform(.2,3)for _ in range(3)]+[1.]
 value=q+[rng.uniform(-3,3)for _ in range(3)]+[scale[3]]+scale+[1.]*4
 initial=[0.,0.,0.,1.,9.,8.,7.,1.]+[1.]*4+unscale
 actual=connect(value,initial);expected=[f(v)for v in value[:12]+unscale];err=max(abs(a-b)for a,b in zip(actual,expected));maximum=max(maximum,err);assert err<1e-6
from pc_skin_palette import PC_RIG,Clip,skin,ChainStates,apply
from evaluate_pc_braid import BraidEval
from native_pc_skin_matrix import matrix
bones=['BrowCenter','BrowLeft','BrowRight','Jaw','CornerLipLeft','CornerLipRight','LowerLip','UpperLip'];clip=Clip(R/'InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions/elsa_bm_idle_specific03.oct',PC_RIG);checks=[]
for phase in (0.,clip.duration/2,clip.duration):
 e=BraidEval(ChainStates(force=[0,-9.8100004196167,0],strict_types=True),0,1/60);apply(e,clip.sample(phase))
 for bone in bones:
  value=e.raw.run(skin[bone]);packed=matrix(value);assert len(value)==16 and all(math.isfinite(x)for x in packed);checks.append(dict(phase=phase,bone=bone,finite_native_matrix=True))
report=dict(passed=True,exe_sha256=sha,synthetic_cases=100,max_component_error=maximum,pc_facial_graph_checks=checks,routine='0x4D9F50 -> 0x4C7750 -> 0x4BD920',scope='Original PC scaled connection, observed Transform input/output and no optional offsets. Copies input TRS while preserving destination Unscale. Eight actual facial source paths evaluate at three clip phases; finite matrices are smoke checks, not live facial parity.')
(R/'ControllerState/scaled-facial-connection-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,synthetic_cases=100,facial_paths=len(checks),max_error=maximum)))
