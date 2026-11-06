"""PC-only full dispatch/staged equivalence, moving-anchor response, and scalar evidence."""
import json,math,struct
from pathlib import Path
import numpy as np
from native_pc_chain_step import ChainStates
from evaluate_pc_arms import DN,N,allnodes,get,rotor,quat
from native_pc_dress_math import aim,inverse_vector,difference

R=Path(__file__).parent;runs=[]
for mode in ['full','staged']:
 state=ChainStates(mode);frames=[]
 for frame in range(120):
  time=frame/30;anchor=[0,0,0,1,.03*math.sin(time*2),0,0,1];container=anchor.copy();container[6]=.3010336757;constraint=[anchor[4],0,.01]
  pos,check=state.step(550,frame,1/30,anchor,container,constraint)
  q=aim(inverse_vector(difference(pos[1],pos[0]),anchor+[1]*8),[0,0,1],[0,1,0],[0,1,0]);state.feedback(550,q)
  frames.append({'positions':pos.tolist(),'check':check})
 runs.append(frames)
error=max(float(np.max(abs(np.array(a['positions'])-b['positions'])))for a,b in zip(*runs));lag=max(abs(f['positions'][1][0]-f['positions'][0][0])for f in runs[0]);assert error<1e-6 and lag>1e-5,(error,lag)
assert all(f['check']['native_last_frame']==i for i,f in enumerate(runs[0]))
capture=R.parent/'OctaneLiveInspector/Captures/octane_20261017_151848_1792264728047355700.json';d=json.loads(capture.read_text());checks=0
for sample in d['samples']:
 for pid,address in [(550,'0x1e07fdd0'),(551,'0x1e07fe74')]:
  chain=next(c for c in sample['chains']if c['address']==address);p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid);refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
  for index,particle in enumerate(chain['particles']):
   source=DN[refs[f'Particle[{index}]']];expected=[get(source,k)for k in ['InverseMass','DragCoefficient','DampingFactor','NaturalFrequency','ConstraintLength']]
   assert struct.pack('<5f',*expected)==struct.pack('<5f',*particle['scalars_raw5']) and get(source,'ConfigFlags')==particle['flags'];checks+=1
rejections=0
for pid,frame,dt in [(550,1,1/30),(550,0,0),(999,0,1/30)]:
 try:ChainStates().step(pid,frame,dt,[0,0,0,1,0,0,0,1],[0,0,0,1,0,0,0,1],[0,0,.01])
 except ValueError:rejections+=1
 else:raise AssertionError('invalid input accepted')
report={'scope':'PC source particle fixture. Full native dispatch vs staged reset/step with previous orientation feedback; zero force and no capsule scene. Scalar signature comparison to previously connected captures validates bounded field mapping, not exact live motion replay.','frames':120,'max_full_vs_staged_position_error':error,'max_tip_lag':lag,'captured_particle_scalar_matches':checks,'invalid_inputs_rejected':rejections,'full_native_frame_stamps_match':True,'frames_full':runs[0]}
(R/'pc-temporal-dress-harness-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='frames_full'})
