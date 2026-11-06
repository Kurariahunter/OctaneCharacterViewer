from evaluate_pc_legs import *
from native_pc_transform_scale import point
from read_pc_idle_files import Clip
from pc_graph_controls import apply
clip=Clip(next((ROOT/'InstalledGameAssetCheck/IdleMotions').rglob('elsa_bm_idle_passive.oct')),PC_RIG);e=LegEval();apply(e,clip.sample(0))
for i,target in [(422,488),(450,479)]:
 try:
  v=point(e.raw.run(i),[0,0,0]);goal=point(e.raw.run(398),e.run(target));print(i,v.tolist(),goal.tolist(),float(np.linalg.norm(v-goal)))
 except Exception as ex:print(i,str(ex))
for i in [634,638,636,640]:
 try:print(i,e.run(i).tolist())
 except Exception as ex:print('FAIL',i,str(ex))
