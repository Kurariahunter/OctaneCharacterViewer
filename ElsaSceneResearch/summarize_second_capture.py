import json
from pathlib import Path
r=Path('F:/DisneyInfinityPortalTest/OctaneLiveInspector');d=json.loads((r/'Captures/octane_20261016_231004_1792206604342552700.json').read_text());rows=[]
for c in d['candidates']:
 s=[next((x for x in f['chains'] if x and x['address']==c['address']),None) for f in d['samples']];s=[x for x in s if x];lag=[x['frame_raw']-x['last_frame_raw'] for x in s]
 rows.append({'address':c['address'],'dress_signature':c['elsa_dress_shape_candidate'],'global_frame_first_last':[s[0]['frame_raw'],s[-1]['frame_raw']],'last_frame_first_last':[s[0]['last_frame_raw'],s[-1]['last_frame_raw']],'frame_lag_range':[min(lag),max(lag)],'output_position_span':max(max(x['output_positions'][j][k] for x in s)-min(x['output_positions'][j][k] for x in s) for j in range(2) for k in range(3))})
(r/'second-live-capture-summary.json').write_text(json.dumps({'capture':'octane_20261016_231004_1792206604342552700.json','samples':len(d['samples']),'scan':d['scan'],'chains':rows},indent=2));print(rows)
