"""Regression: native residual is preserved; corrupted ankle remains rejected."""
import numpy as np
from pc_skin_palette import *
from evaluate_pc_braid import BraidEval
from native_pc_ik_endpoint import witness
base=Clip(ROOT/'InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions/elsa_bm_idle_passive.oct',PC_RIG)
c=Clip(ROOT/'InstalledGameAssetCheck/TurnMotions/fro_elsa/characters/class_girl/motions/grl_bm_turn90r.oct',PC_RIG)
e=BraidEval(ChainStates(force=[0,-9.8100004196167,0],strict_types=True),121,c.duration/36)
apply(e,base.sample(0));apply(e,c.sample(c.duration/36),allow_transform_scale=True)
rows=[]
for ankle,target,pid in ((422,488,405),(450,479,411)):
 actual=point(e.raw.run(ankle),[0,0,0]);w=witness(e.solvers[pid],e.run(400))
 error=float(np.linalg.norm(actual-w['world']));assert error<1e-6
 assert np.linalg.norm((actual+np.array([.001,0,0]))-w['world'])>1e-5
 rows.append(dict(ankle=ankle,native_output_error=error,target_residual=w['native_target_residual']))
assert rows[1]['target_residual']>1e-5
try:witness(e.solvers[411],np.diag([2.,1,1,1]))
except ValueError:pass
else:raise AssertionError('Nonrigid root accepted')
print(json.dumps(dict(passed=True,checks=rows,corrupted_endpoint_rejected=True,nonrigid_root_rejected=True)))
