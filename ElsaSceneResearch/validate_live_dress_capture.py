"""Check animated live dress capture using original native inverse/Aim operators."""
import json,math
from pathlib import Path
import numpy as np
from evaluate_elsa_head import DN,get,quat
from native_dress_math import aim,inverse_vector,difference
from native_leg_ik import sha
r=Path('F:/DisneyInfinityPortalTest/OctaneLiveInspector');capture=r/'Captures/octane_20261016_231004_1792206604342552700.json';d=json.loads(capture.read_text());rows=[]
for side,address,axis,up,upref in [('Left','0x1e07fdd0',727,726,725),('Right','0x1e07fe74',742,741,740)]:
 samples=[]
 for index,f in enumerate(d['samples']):
  c=next(x for x in f['chains'] if x and x['address']==address);anchor=c['anchor_raw16'];pos=np.array(c['output_positions']);q=c['cached_orientation']['quaternion'];delta=difference(pos[1],pos[0]);local=inverse_vector(delta,anchor);expected=aim(local,get(DN[axis],'Data'),get(DN[up],'Data'),get(DN[upref],'Data'),initial=q)
  # Sign-invariant quaternion comparison; normalize captured values for angle only.
  qa=np.array(q);qb=np.array(expected);dot=abs(float(np.dot(qa/np.linalg.norm(qa),qb/np.linalg.norm(qb))));angle=math.degrees(2*math.acos(min(1,dot)))
  samples.append({'sample':index,'global_frame':c['frame_raw'],'chain_last_frame':c['last_frame_raw'],'frame_lag':c['frame_raw']-c['last_frame_raw'],'root_vs_anchor_error':float(np.linalg.norm(pos[0]-anchor[4:7])),'length_error':abs(float(np.linalg.norm(pos[1]-pos[0]))-.37*anchor[7]),'native_aim_vs_cached_degrees':angle,'cached_q_norm_error':abs(float(np.linalg.norm(qa))-1),'native_aim_q':expected,'cached_q':q})
 row={'side':side,'address':address,'samples':samples,'max_root_vs_anchor_error':max(x['root_vs_anchor_error'] for x in samples),'max_length_error':max(x['length_error'] for x in samples),'max_native_aim_vs_cached_degrees':max(x['native_aim_vs_cached_degrees'] for x in samples),'median_native_aim_vs_cached_degrees':float(np.median([x['native_aim_vs_cached_degrees'] for x in samples]))};rows.append(row);print({k:v for k,v in row.items() if k!='samples'})
report={'source_capture':str(capture),'exe_sha256':sha,'scope':'Non-atomic live snapshots. Original native Aim/inverse operators applied to captured positions, anchor Transform and cached local quaternion; source-side assignment based on exact parameter signature from previous capture. No precise clip/time match or runtime ownership traversal.','chains':rows}
(r/'animated-live-dress-validation.json').write_text(json.dumps(report,indent=2))
