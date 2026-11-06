import json
import numpy as np
from pathlib import Path
p=Path('live-upper-dress-comparison.json');d=json.loads(p.read_text());rows=[]
for j,live in enumerate(d['live_samples']):
 matches=[]
 for clip in d['source_clips']:
  choices=[(sum(float(np.max(abs(np.array(live[s]['matrix'])-np.array(f[s])))) for s in ['Left','Right']),k) for k,f in enumerate(clip['frames'])]
  score,k=min(choices);matches.append({'clip':clip['name'],'source_time':clip['frames'][k]['time'],'score':score})
 rows.append({'sample':j,'nearest_candidates':matches})
d['all_sample_nearest_pose_diagnostics']=rows
summary=[]
for i,c in enumerate(d['source_clips']):
 vals=[x['nearest_candidates'][i]['score'] for x in rows];summary.append({'clip':c['name'],'min_score':min(vals),'median_score':float(np.median(vals)),'max_score':max(vals),'samples_below_0_01':sum(v<.01 for v in vals)})
d['nearest_pose_summary']=summary;p.write_text(json.dumps(d,indent=2));print(summary)
