"""Bake one explicitly supplied compatible Elsa clip on the source64-bone graph."""
import json,sys,numpy as np
from pathlib import Path
from wiiu_pc_graph_adapter import Adapter,P,refs
from wiiu_clip_sampler import WiiUClip
from wiiu_dress_adapter import DressStates,SourceDressEval
from evaluate_pc_dress import DressEval
from pc_graph_controls import apply
from pc_finger_controls import prepare_fingers
from native_pc_transform_scale import point
from validate_dilation_matrix_pc_native import convert

def matrix(raw):
 if len(raw)==8:return convert(raw)[1]
 assert len(raw)==16
 origin=point(raw,[0,0,0]);m=np.eye(4);m[:3,3]=origin
 for col in range(3):
  axis=[0,0,0];axis[col]=1;m[:3,col]=point(raw,axis)-origin
 return m

def bake(path):
 a=Adapter();audit=a.audit();clip=WiiUClip(path);frames=clip.frames(60);bindings=json.loads((P/'wiiu-skin-associations.json').read_text());states=DressStates(a);samples=[];checks=[];R=np.diag([-1,1,1,1]);dt=(clip.hi-clip.lo)/(len(frames)-1)
 for tick in range(120+len(frames)):
  local=tick-120;frame=frames[0]if local<0 else frames[local];pc=DressEval();apply(pc,a.controls(frame));prepare_fingers(pc);source=SourceDressEval(a,audit,pc,states,tick,1/60 if local<0 else dt);out=[]
  for binding in bindings:
   node=refs(a.producers[binding['matrix_node']][0])['Input'];m=matrix(source.run(node));assert np.isfinite(m).all()and np.linalg.det(m[:3,:3])>1e-8
   out.append({'bone':binding['bone'],'matrix':(R@m@R).flatten().tolist()})
  assert len(source.chain_checks)==3
  assert all(c["native_last_frame"]==tick for c in source.chain_checks)
  checks.extend(source.chain_checks)
  if local>=0 and(local%2==0 or local==len(frames)-1):samples.append({'time':frame['time']-clip.lo,'transforms':out})
  if tick%120==0:print(Path(path).name,tick,'/',120+len(frames),flush=True)
 base=json.loads((P/'wiiu-source-mesh-animation-full.json').read_text());name=Path(path).name.replace('.oct.clipdata','');base['clips']=[{'name':'WiiU_'+name,'duration':clip.hi-clip.lo,'samples':samples}];base['clipdata_sha256']=clip.sha
 target=P/'ClipExpansion'/(name+'.animation.json');target.write_text(json.dumps(base,separators=(',',':')),encoding='utf-8')
 report={'clip':name,'sha256':clip.sha,'source_outputs':64,'samples':len(samples),'chain_checks':len(checks),'parameter_checks':states.evidence,'maximum_root_error':max(c['root_error']for c in checks),'maximum_segment_length_error':max(c['segment_length_error']for c in checks),'warmup_ticks':120,'collision':False}
 target.with_suffix('.validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('PASS',target,len(samples),'poses',len(checks),'chain checks',flush=True)
 return target
if __name__=='__main__':
 for path in sys.argv[1:]:bake(path)
