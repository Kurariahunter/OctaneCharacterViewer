"""Assemble verified Elsa idle caches and forward locomotion fixture caches."""
from pathlib import Path
import json,numpy as np
P=Path(__file__).parent
base=json.loads((P/'wiiu-elsa-idles-full.json').read_text());reports=[]
for mode in ['run','walk']:
 data=json.loads((P/'ClipExpansion'/f'wiiu-{mode}-forward.animation.json').read_text());assert data['source_skin_nodes']==base['source_skin_nodes'];clip=data['clips'][0];previous=-1.
 for s in clip['samples']:
  assert previous<s['time']<=clip['duration']+.00001;previous=s['time'];assert len(s['transforms'])==64
  assert set(t['bone']for t in s['transforms'])==set(base['source_skin_nodes'])
  for t in s['transforms']:
   m=np.array(t['matrix']).reshape(4,4);assert np.isfinite(m).all()and np.linalg.det(m[:3,:3])>1e-8 and np.max(abs(m[3]-[0,0,0,1]))<1e-8
 base['clips'].append(clip);reports.append({'name':clip['name'],'samples':len(clip['samples']),'duration':clip['duration']})
base['scope']='Wii U Elsa: five idle/transition clips and two source-composed locomotion fixtures.64evaluated outputs; explicit warmup,passive initializer,layer assignments and native PC numerical helpers; no collision or full game parity.'
base['fixture_assumptions']=['Hair/dress120tickphasezerowarmup,PCgravity,60Hzschedule,nocollision.','Locomotion source group tracks use passive phase-zero initialization,unit lower/upper assignments,normalized phase and native additive lean with authored .5walk/1runweight.','Runtime actor scheduling,filter coefficients and live layer arbitration remain unreconstructed.','Preview textures reuse matching PC material images.']
(P/'wiiu-elsa-motion-pack-full.json').write_text(json.dumps(base,separators=(',',':')),encoding='utf-8');(P/'ClipExpansion/locomotion-pack-validation.json').write_text(json.dumps({'pass':True,'total_clips':len(base['clips']),'added':reports,'palette_outputs':64,'previous_idles_unchanged':True},indent=2),encoding='utf-8');print(reports)
