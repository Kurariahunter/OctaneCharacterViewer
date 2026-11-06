from pc_skin_palette import *
from evaluate_pc_braid import BraidEval
c=Clip(next((R/'InstalledGameAssetCheck/IdleMotions').rglob('elsa_bm_idle_passive.oct')),PC_RIG)
def sequence(mode):
 states=ChainStates(mode=mode,force=[0,-9.8100004196167,0],strict_types=True);rows=[];checks=[]
 for frame in range(32):
  e=BraidEval(states,frame,1/60);apply(e,c.sample(min(frame/60,c.duration)))
  e.raw.run(skin['hair01']);e.run(skin['hair02']);rows.append(np.r_[e.cache[678],e.cache[683]]);checks+=e.dress_checks
 return np.array(rows),checks
full,checks=sequence('full');again,_=sequence('full');staged,_=sequence('staged')
repeat=float(np.max(abs(full-again)));split=float(np.max(abs(full-staged)))
if repeat>1e-8 or split>2e-5:raise ValueError(('braid dispatch mismatch',repeat,split))
rejected=[]
for pid,dt in [(999,1/60),(548,0),(548,float('nan'))]:
 try:ChainStates().step(pid,0,dt,[0,0,0,1,0,0,0,1],[0,0,0,1,0,0,0,1],[0,0,0])
 except ValueError:rejected.append([str(pid),str(dt)])
 else:raise ValueError('malformed chain input accepted')
report={'scope':'PC braid548 offline native fixtures, not live-game parity','frames':32,'repeat_max_error':repeat,'full_vs_staged_max_error':split,'max_root_error':max(x['root_error']for x in checks),'max_length_error':max(x['segment_length_error']for x in checks),'rejected':rejected,'checks':checks}
(R/'pc-braid-native-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='checks'}))
