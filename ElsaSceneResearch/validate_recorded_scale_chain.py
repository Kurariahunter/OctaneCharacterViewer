"""Recorded source targets, native Transform helpers, explicit segment compensation fixture."""
import json,numpy as np
from pathlib import Path
from native_transform_scale import compose,concat,point
from evaluate_elsa_feet import rotor
ROOT=Path(__file__).parent
src=json.loads((ROOT/'elsa-foot-target-samples.json').read_text());reports=[]
for clip in src['clips']:
 frames=[];cases=[]
 for frame in clip['samples']:
  for leg in frame['legs']:
   A=np.array(leg['upper_matrix']).reshape(4,4);B=np.array(leg['knee_matrix']).reshape(4,4);s1,s2=leg['native_scale_payloads'];R1=A[:3,:3]/np.array(leg['scales'][0]);R2=B[:3,:3]/np.array(leg['scales'][1]);q1=rotor(R1);q2=rotor(R2)
   parent=compose(q1,A[:3,3],s1,[1]*4)
   # Explicit fixture: local child translation is multiplied by parent's Scale,
   # while native concatenate preserves child's Scale on the composed geometry.
   # Original skin hierarchy's metadata assignment remains to be traced.
   child=compose(q2,B[:3,3],s2,s1)
   world=concat(child,parent);mid=point(parent,B[:3,3]);end=point(world,[0,0,0.41155261]);target=np.array(leg['target_hip_space']);error=float(np.linalg.norm(end-target));origin=point(parent,[0,0,0]);errmid=float(np.linalg.norm(np.array(world[4:7])-mid))
   if not np.isfinite(error) or error>5e-5 or errmid>5e-6:raise ValueError(('recorded scale fixture failure',clip['name'],frame['time'],error,errmid))
   cases.append({'time':frame['time'],'side':leg['side'],'error':error,'native_mid_consistency_error':errmid})
   frames.append({'processor':412 if leg['side']=='Left' else 408,'time':frame['time'],'start':origin.tolist(),'mid':mid.tolist(),'end':end.tolist(),'target':target.tolist()})
 name='passive' if 'idle_passive' in clip['name'] else 'active';scope='SOURCE '+name.upper()+' IDLE TARGETS - PARTIAL LEG GRAPH. Native IK + native Transform helpers with explicit child Unscale=parent Scale fixture. Original skin metadata assignment and full animation not validated.'
 (ROOT/('original-leg-targets-'+name+'.json')).write_text(json.dumps({'scope':scope,'frames':frames},separators=(',',':')))
 reports.append({'clip':name,'times':len(clip['samples']),'leg_cases':len(cases),'max_endpoint_error':max(c['error'] for c in cases),'max_mid_consistency_error':max(c['native_mid_consistency_error'] for c in cases),'cases':cases})
report={'scope':'Recorded targets through native Transform helpers using explicit child Unscale=parent Scale fixture. Establishes this fixture numerically closes scale discrepancy; does NOT establish the original skin hierarchy assigns that metadata or that exported Elsa skin is correct. Lower-segment length0.41155261 is rounded from authored geometry.','clips':reports}
(ROOT/'recorded-scale-chain-validation.json').write_text(json.dumps(report,indent=2));print([{k:v for k,v in c.items() if k!='cases'} for c in reports])
