"""Source-backed skirt ownership inventory and bounded upper-dress checks."""
import json
from pathlib import Path
import numpy as np
from evaluate_elsa_head import T,N,DN,PROD,get,allnodes,Eval
from evaluate_native_skin import NativeSkinEval,affine
from evaluate_elsa_feet import FootEval
from native_leg_ik import sha
R=Path(__file__).parent
chains=[]
for p in allnodes(N,'ProcessorNode'):
 if get(p,'Type')!='DynamicChain':continue
 refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
 outputs={k:v for k,v in refs.items() if k.startswith('Position[')}
 for node in outputs.values():
  assert PROD[node][0] is p
  try:Eval().run(node)
  except ValueError as ex:assert 'unsupported DynamicChain' in str(ex)
  else:raise AssertionError('Dynamic output silently fell back to stored data')
 chains.append({'processor':int(p['value']),'outputs':outputs,'attributes':refs,'chain_data':DN[refs['ChainData']],'particles':[DN[v] for a,v in refs.items() if a.startswith('Particle[')]})
old=json.loads((R/'elsa-native-skin-animation.json').read_text());new=json.loads((R/'elsa-native-dress-animation.json').read_text());summary=[]
for a,b in zip(old['clips'],new['clips']):
 assert len(a['samples'])==len(b['samples']);changed=set();maxdiff=0
 for f,g in zip(a['samples'],b['samples']):
  assert abs(f['time']-g['time'])<1e-6
  for p,q in zip(f['transforms'],g['transforms']):
   assert p['bone']==q['bone'];error=float(np.max(abs(np.array(p['matrix'])-q['matrix'])))
   if error>1e-7:changed.add(p['bone']);maxdiff=max(maxdiff,error)
 assert changed<=set(['UpperDress_Left','UpperDress_Right','dressLeftStart','dressRightStart']),changed
 summary.append({'clip':b['name'],'samples':len(b['samples']),'changed_palette_bones':sorted(changed),'max_matrix_change_from_previous_preview':maxdiff})
# The four additional source controls must not perturb previously verified native feet.
oldcontrols=json.loads((R/'elsa-skin-control-samples.json').read_text());newcontrols=json.loads((R/'elsa-dress-control-samples.json').read_text());maxleg=0
for a,b in zip(oldcontrols['clips'],newcontrols['clips']):
 for j in [0,len(a['samples'])//2,len(a['samples'])-1]:
  ns=[]
  for c in [a,b]:
   e=FootEval();e.overrides={int(k):v for k,v in c['samples'][j]['controls'].items()};n=NativeSkinEval(e);ns.append([affine(n.run(i)) for i in [432,461,441,470]])
  maxleg=max(maxleg,max(float(np.max(abs(x-y))) for x,y in zip(*ns)))
assert maxleg<1e-7,maxleg
report={'exe_sha256':sha,'scope':'UpperDress clip sampling and DynamicChain ownership. No native lower-dress simulation yet. Stored lower-dress zero positions are rejected.','skin_outputs':{'UpperDress_Left':650,'UpperDress_Right':655,'dressLeftStart':733,'dressRightStart':748},'simulation_routines':{'factory':'0x4aa330','allocation_wrapper':'0x4a1ea0','node_wrapper':'0x49caf0','allocation':'0x493060','constructor':'0x48f110','vtable':'0x1b2aacc','execute':'0x4ae360','reset':'0x4acad0','step':'0x4acdb0','integration':'0x4a1f90','constraint_iterations':'0x4aaa10','particle_loader':'0x49fe90','chain_data_loader':'0x4a29e0'},'dynamic_chains':chains,'upper_dress_validation':summary,'old_leg_regression_cases':24,'max_old_leg_matrix_change':maxleg,'remaining':'Decode DynamicChain initialization, frame/delta-time and persistent state, particle variant layout and constraint inputs before producing simulated lower-dress animation.'}
(R/'dress-research-validation.json').write_text(json.dumps(report,indent=2));print('PASS',summary,'legs',maxleg,'dynamic_outputs_rejected',sum(len(c['outputs']) for c in chains))
