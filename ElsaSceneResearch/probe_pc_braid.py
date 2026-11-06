from pc_skin_palette import *
from evaluate_pc_braid import BraidEval
c=Clip(next((R/'InstalledGameAssetCheck/IdleMotions').rglob('elsa_bm_idle_passive.oct')),PC_RIG)
states=ChainStates(force=[0,-9.8100004196167,0],strict_types=True)
for frame in range(4):
 e=BraidEval(states,frame,1/60);apply(e,c.sample(0))
 for bone in ['hairStart','hair01','hair02']:
  node=skin[bone];out=e.raw.run(node)if get(DN[node],'Type')=='Transform'else e.run(node);print(frame,bone,out)
 print(e.dress_checks)
