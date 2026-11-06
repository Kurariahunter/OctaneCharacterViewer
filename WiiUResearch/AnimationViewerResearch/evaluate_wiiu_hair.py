"""Three source hair outputs using source routing and retained native braid state."""
import json,numpy as np
from wiiu_pc_graph_adapter import Adapter,P,refs
from wiiu_clip_sampler import WiiUClip
from wiiu_dress_adapter import DressStates,SourceDressEval
from evaluate_pc_dress import DressEval
from pc_graph_controls import apply
from native_pc_transform_scale import point
from validate_dilation_matrix_pc_native import convert

def matrix(raw):
 if len(raw)==8:return convert(raw)[1]
 assert len(raw)==16;origin=point(raw,[0,0,0]);m=np.eye(4);m[:3,3]=origin
 for col in range(3):
  axis=[0,0,0];axis[col]=1;m[:3,col]=point(raw,axis)-origin
 return m

a=Adapter();audit=a.audit();clip=WiiUClip();frames=clip.frames(60);bindings=json.loads((P/'wiiu-skin-associations.json').read_text());names={'hairStart','hair01','hair02'};selected=[b for b in bindings if b['bone']in names];assert len(selected)==3
states=DressStates(a);checks=[];samples=[];warmup=120;dt=(clip.hi-clip.lo)/(len(frames)-1);zero=clip.sample(clip.lo)
for tick in range(warmup+len(frames)):
 local=tick-warmup;frame=zero if local<0 else frames[local];pc=DressEval();apply(pc,a.controls(frame));source=SourceDressEval(a,audit,pc,states,tick,1/60 if local<0 else dt);outputs=[]
 for binding in selected:
  node=refs(a.producers[binding['matrix_node']][0])['Input'];m=matrix(source.run(node));assert np.isfinite(m).all()and abs(np.linalg.det(m))>1e-8
  outputs.append({**binding,'source_node':node,'matrix':m.tolist()})
 assert len(source.chain_checks)==1
 for check in source.chain_checks:
  assert check['native_last_frame']==tick;checks.append({'tick':tick,'time':frame['time'],'warmup':local<0,**check})
 if local>=0 and local%2==0:samples.append({'time':frame['time'],'outputs':outputs})
 if tick%60==0:print('HAIR',tick+1,'/',warmup+len(frames),flush=True)
assert len(samples)==153
report={'scope':'Three Wii U source hair outputs, existing native PC braid solver on source-matched parameters and source routing. Explicit120tick warmup/60Hzgravity fixture, no scene collision or full game parity.','warmup_ticks':warmup,'simulation_ticks':len(frames),'parameter_checks':[r for r in states.evidence if r['processor']==550],'samples':samples,'chain_checks':checks,'max_root_error':max(c['root_error']for c in checks),'max_length_error':max(c['segment_length_error']for c in checks)}
(P/'wiiu-source-hair-animation.json').write_text(json.dumps(report,separators=(',',':')),encoding='utf-8');print('PASS',len(samples)*3,'hair matrices;',len(checks),'chronological chain checks; max root/length',report['max_root_error'],report['max_length_error'])
