"""Compare captured upper-dress matrices in their common anchor basis."""
import json,struct
from pathlib import Path
import numpy as np
from evaluate_dress import DressEval
from evaluate_native_skin import affine
from native_transform_scale import concat
R=Path(__file__).parent;live=json.loads(Path('F:/DisneyInfinityPortalTest/OctaneLiveInspector/Captures/octane_20261016_231644_1792207004521971800.json').read_text());source=json.loads((R/'elsa-knee-dress-control-samples.json').read_text())
def raw(g,node):return list(struct.unpack('<16f',bytes.fromhex(g['nodes'][node]['payload_prefix_hex64'])))
def input_node(g,node,i):return g['nodes'][node]['inputs'][i]['node']
live_rows=[];worst=0
for f in live['samples']:
 g=f['upstream'];rows={}
 for side,address in [('Left','0x1e07fdd0'),('Right','0x1e07fe74')]:
  root=next(x for x in g['roots'] if x['chain']==address);anchor=root['anchor'];upper=input_node(g,anchor,1);local=input_node(g,upper,0);base=input_node(g,upper,1)
  assert g['nodes'][upper]['operation']=='ConcatenateDilationTransform'
  child=raw(g,local)[:8]+[1]*8;parent=raw(g,base);actual=raw(g,upper);expected=concat(child,parent);err=float(np.max(abs(np.array(expected)-actual)));worst=max(worst,err)
  matrix=np.linalg.inv(affine(parent))@affine(actual)
  rows[side]={'upper_node':upper,'base_node':base,'matrix':matrix.tolist(),'compose_error':err}
 live_rows.append(rows)
source_rows=[]
for clip in source['clips']:
 frames=[]
 for s in clip['samples']:
  e=DressEval();e.overrides={int(k):v for k,v in s['controls'].items()};n=e.native;base=affine(n.run(13));inv=np.linalg.inv(base)
  frames.append({'time':s['time'],'Left':(inv@affine(n.run(650))).tolist(),'Right':(inv@affine(n.run(655))).tolist()})
 source_rows.append({'name':clip['name'],'frames':frames})
comparisons=[]
for clip in source_rows:
 scores=[]
 for j,frame in enumerate(clip['frames']):
  # This is a nearest-pose diagnostic, NOT a runtime clip identification.
  error=sum(float(np.max(abs(np.array(live_rows[0][side]['matrix'])-np.array(frame[side])))) for side in ['Left','Right'])
  scores.append((error,j))
 score,j=min(scores);per={}
 for side in ['Left','Right']:
  a=np.array(live_rows[0][side]['matrix']);b=np.array(clip['frames'][j][side]);ra=a[:3,:3]/np.linalg.norm(a[:3,:3],axis=0);rb=b[:3,:3]/np.linalg.norm(b[:3,:3],axis=0);angle=float(np.degrees(np.arccos(np.clip((np.trace(ra.T@rb)-1)/2,-1,1))))
  per[side]={'translation_distance':float(np.linalg.norm(a[:3,3]-b[:3,3])),'rotation_degrees':angle}
 comparisons.append({'clip':clip['name'],'nearest_source_time_for_first_live_sample':clip['frames'][j]['time'],'matrix_score_sum':score,'sides':per})
 print(comparisons[-1],flush=True)
report={'scope':'Output-alias-validated live upper-dress producer path and common-anchor matrix comparison. Captures non-atomic; nearest pose does not identify active clip, layers or time.','max_live_concat_raw_error':worst,'live_samples':live_rows,'source_clips':source_rows,'first_sample_nearest_pose_diagnostics':comparisons}
(R/'live-upper-dress-comparison.json').write_text(json.dumps(report,indent=2));print('LIVE COMPOSE MAX',worst,flush=True)
