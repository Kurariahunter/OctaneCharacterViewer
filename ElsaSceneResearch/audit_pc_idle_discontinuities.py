"""Locate flagged PC idle curve boundaries and replay original native evaluation."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from read_pc_idle_files import Rig,Clip
from native_pc_clip_math import curve,sha
rig=Rig(ROOT/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct')
rows=[]
for number in range(1,4):
 name=f'elsa_bm_idle_specific{number:02}'
 clip=Clip(ROOT/f'InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions/{name}.oct',rig)
 flagged=[]
 for ci,c in enumerate(clip.layout['curves']):
  for component,error in enumerate(c['continuity_error_quantization_units']):
   if error<=3:continue
   registers=[i for i,r in enumerate(clip.layout['registers']) if r==dict(curve=ci,component=component)]
   refs=[]
   for command in clip.layout['commands']:
    for fields in command['descriptors']:
     if fields[0]&0xf000==0x1000:
      used=[fields[i+1] for i,shift in enumerate((4,2,0)) if ((fields[0]>>shift)&3)==1]
     else:used=fields[1:2]
     if set(used)&set(registers):
      node=rig.lookup.get(command['port'])
      refs.append(dict(port=command['port'],node=node,path=rig.paths.get(node),descriptor=fields))
   k=max(range(len(c['segments'])-1),key=lambda k:abs(c['segments'][k][component][-1]-c['segments'][k+1][component][0]))
   tick=c['knots'][k+1];dt=(c['time_end']-c['time_start'])/65535
   t=c['time_start']+tick*dt
   start=clip.offsets[ci+2];end=clip.offsets[ci+3] if ci+3<len(clip.offsets) else clip.offsets[0]
   samples=[dict(time=t+offset*dt,value=curve(clip.b[start:end],t+offset*dt,len(c['metadata']))[component]) for offset in (-2,-1,0,1,2)]
   jump=max(s['value'] for s in samples)-min(s['value'] for s in samples)
   assert jump>0,'Flagged boundary not reproduced by native routine'
   flagged.append(dict(curve=ci,component=component,quantization_units=error,time=t,registers=registers,references=refs,native_samples=samples,native_value_span=jump))
  
 rows.append(dict(name=name,clipdata_sha256=clip.sha,max_continuity_units=clip.layout['max_continuity_error_quantization_units'],flagged=flagged))
assert len(rows[1]['flagged'])==2
assert all(r['node']==344 for f in rows[1]['flagged'] for r in f['references'])
report=dict(exe_sha256=sha,model_sha256=rig.sha,clips=rows,scope='Original native scalar routine reproduces eye-control boundary steps in pinned PC idle02. Not proof of authored intent, rendered eyes, timing, full-animation parity or finger correction.')
out=ROOT/'ControllerState/pc-idle-discontinuity-audit.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
for r in rows:print(r['name'],r['max_continuity_units'],[(f['curve'],f['time'],f['native_value_span'],f['references']) for f in r['flagged']])
