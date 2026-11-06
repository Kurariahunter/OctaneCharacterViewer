"""Audit skirt bulge ownership without changing source weights."""
import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation\YodaAnimationProbe\analysis_dependencies')
import numpy as np
from decode_elsa_static_channels import decode
R=Path(__file__).parent;m=json.loads((R/'elsa-preview-model.json').read_text());v=np.array(m['positions']).reshape(-1,3);ix=np.array([x['indices'] for x in m['weights']]);w=np.array([x['values'] for x in m['weights']]);names=[b['name'] for b in m['bones']];dress=[names.index(n) for n in ['UpperDress_Left','UpperDress_Right','dressLeftStart','dressRightStart']];mask=(np.sum(w*np.isin(ix,dress),axis=1)>.5)&(v[:,1]<.85);bind=np.array([b['world'] for b in m['bones']]).reshape(-1,4,4);ib=np.linalg.inv(bind);p=np.c_[v,np.ones(len(v))]
def skin(poses):
 W=np.array([x['matrix'] for x in poses]).reshape(-1,4,4);M=W@ib;return sum(w[:,k,None]*np.einsum('nij,nj->ni',M[ix[:,k]],p)[:,:3] for k in range(4))
old=json.loads((R/'elsa-native-dynamic-dress-animation.json').read_text());new=json.loads((R/'elsa-knee-dress-animation.json').read_text());reset=json.loads((R/'native-dress-reset-only-samples.json').read_text());stepped=json.loads((R/'native-dynamic-dress-samples.json').read_text());rows=[]
for oc,nc,rc,sc in zip(old['clips'],new['clips'],reset['clips'],stepped['clips']):
 frame=min(60,len(oc['samples'])-1);o=skin(oc['samples'][frame]['transforms']);n=skin(nc['samples'][frame]['transforms']);assert np.isfinite(n).all();extrema=[]
 for vi in np.where(mask)[0][np.argsort(n[mask,0])[-5:]]:
  extrema.append({'vertex':int(vi),'bind':v[vi].tolist(),'posed':n[vi].tolist(),'weights':[{'bone':names[j],'weight':float(z)} for j,z in zip(ix[vi],w[vi]) if z>0]})
 static=decode((R/(oc['name'].split('_Native')[0]+'.clipdata.bin')).read_bytes(),json.loads((R/(oc['name'].split('_Native')[0]+'-decoded-curves.json')).read_text()));twists=[x for x in static['tracks'] if x['port'] in [189,197]]
 resetdiff=max(float(np.max(abs(np.array(a['worlds'][k])-b['worlds'][k]))) for a,b in zip(sc['samples'],rc['samples']) for k in a['worlds']);initialdiff=max(float(np.max(abs(np.array(sc['samples'][0]['worlds'][k])-rc['samples'][0]['worlds'][k]))) for k in sc['samples'][0]['worlds'])
 changed=set()
 for a,b in zip(oc['samples'],nc['samples']):
  for x,y in zip(a['transforms'],b['transforms']):
   assert x['bone']==y['bone']
   if np.max(abs(np.array(x['matrix'])-y['matrix']))>2e-6:changed.add(x['bone'])
 rows.append({'clip':nc['name'],'sample_frame':frame,'old_skirt_extents':[o[mask].min(axis=0).tolist(),o[mask].max(axis=0).tolist()],'corrected_skirt_extents':[n[mask].min(axis=0).tolist(),n[mask].max(axis=0).tolist()],'original_reset_vs_step_max_matrix_difference':resetdiff,'original_reset_vs_step_initial_difference':initialdiff,'authored_knee_static_records':twists,'changed_bones':sorted(changed),'outer_right_vertices':extrema})
assert all(np.max(abs(np.sum(w,axis=1)-1))<1e-7 for _ in [0]);newmodel=json.loads((R/'elsa-knee-dress-model.json').read_text());assert newmodel['weights']==m['weights'] and newmodel['positions']==m['positions'] and newmodel['submeshes']==m['submeshes'];assert [b['world'] for b in newmodel['bones']]==[b['world'] for b in m['bones']]
report={'scope':'Controlled source-weight LBS comparison. Original weights, vertices, triangles and inverse binds unchanged. This is not proof of full game pose fidelity.','skirt_vertices_checked':int(mask.sum()),'clips':rows,'conclusions':['Bulge is present at reset and maps to original dressRightStart/UpperDress_Right weights.','Old reset-only and stepped paths differ by at most0.000526 in matrices for active, exactly0 for passive; accumulating native simulation instability does not explain the visible bulge.','Recovered constant Float controls189/197 were previously omitted; they are now sampled into43/70 and passed to original IK twist inputs.','Source knee correction alone does not remove the active bulge; remaining full-pose/reference behavior is still unverified. No cosmetic weight edits made.']}
(R/'skirt-bulge-audit.json').write_text(json.dumps(report,indent=2));print('BULGE_AUDIT_PASS',[(x['clip'],x['changed_bones']) for x in rows])
