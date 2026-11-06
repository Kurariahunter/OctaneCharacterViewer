from pc_skin_palette import *
from pc_finger_controls import prepare_fingers
from evaluate_pc_feedback_dress import FeedbackDressEval
from native_pc_transform_scale import compose
from evaluate_pc_raw_transform import affine
c=Clip(next((R/'InstalledGameAssetCheck/RunMotions').rglob('grl_bm_run_upbody_add.oct')),PC_RIG)
e=FeedbackDressEval(ChainStates(),0,1/60);apply(e,c.sample(0));prepare_fingers(e)
rows=[]
for node in [176,201,204,207,210,213,216,219]:
 m=e.cache[node];q=rotor(m[:3,:3]);native=affine(compose(q,m[:3,3].tolist(),[1]*4,[1]*4));err=float(np.max(abs(m-native)));rows.append({'node':node,'path':PC_RIG.paths[node],'quaternion':q,'position':m[:3,3].tolist(),'native_point_matrix_error':err});print(node,'matrix error',err)
(R/'pc-index-coordinate-audit.json').write_text(json.dumps(rows,indent=2))
