"""PC file reader numerical and malformed-input checks."""
import json,struct
from pathlib import Path
from read_pc_idle_files import Rig,Clip,R
from pc_clip_decoder import decode,sample
from native_pc_clip_math import curve
rig=Rig(R/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct');cases=[];malformed=0;summary=[]
for name in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
 c=Clip(next((R/'InstalledGameAssetCheck/IdleMotions').rglob(name+'.oct')),rig)
 for ci,item in enumerate(c.layout['curves']):
  a=c.offsets[ci+2];z=c.offsets[ci+3]if ci+3<len(c.offsets)else c.offsets[0];regs=[i for i,r in enumerate(c.layout['registers'])if r['curve']==ci]
  for fraction in [0,.13,.37,.61,.89,1]:
   t=item['time_start']+(item['time_end']-item['time_start'])*fraction;actual=curve(c.b[a:z],t,len(item['metadata']));expected=[sample(c.layout,r,t)for r in regs];error=max(abs(x-y)for x,y in zip(actual,expected));cases.append({'clip':name,'curve':ci,'time':t,'error':error})
 for broken in [c.b[:20],c.b[:-1],c.b[:c.layout['float_pool_start']-1]]:
  try:decode(broken)
  except (ValueError,struct.error,IndexError):malformed+=1
  else:raise AssertionError('truncated payload accepted')
 for t in [-1,c.duration+1,float('nan')]:
  try:c.sample(t)
  except ValueError:malformed+=1
  else:raise AssertionError('invalid time accepted')
 frames=[c.sample(t)for t in [0,c.duration/2,c.duration]];moving=[]
 for port in frames[0]:
  if any(f[port]['channels']!=frames[0][port]['channels']for f in frames[1:]):moving.append({'port':port,'node':frames[0][port]['source_node'],'path':frames[0][port]['path']})
 summary.append({'name':name,'timed_unmapped':[r['port']for r in c.layout['commands']if r['port']not in rig.lookup],'moving_channels_three_time_check':moving})
report={'scope':'Independent Python-vs-original-native PC scalar curve checks. Does not validate full graph/loader or runtime blend state.','curve_cases':len(cases),'max_curve_error':max(x['error']for x in cases),'malformed_or_invalid_time_rejections':malformed,'clips':summary,'cases':cases}
(R/'pc-file-reader-validation.json').write_text(json.dumps(report,indent=2));print('CURVE_CASES',len(cases),'MAX_ERROR',report['max_curve_error'],'REJECTIONS',malformed);print([(c['name'],c['timed_unmapped'],len(c['moving_channels_three_time_check']))for c in summary]);assert report['max_curve_error']<0.00001;assert malformed==12
