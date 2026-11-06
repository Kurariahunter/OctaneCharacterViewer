"""Bake native two-particle lower dress from bounded source idle anchors.
Explicit zero external force and previous-frame local aim feedback; not full loader.
"""
import json,struct,numpy as np
from pathlib import Path
from evaluate_native_skin import NativeSkinEval,affine
from evaluate_dress import DressEval
from evaluate_elsa_head import DN,get,quat
from native_transform_scale import point
from validate_foot_basis_native import native
from native_dress_math import aim,inverse_point,inverse_vector,difference
from native_dynamic_chain_fixture import make,invoke,positions,u,BASE,PROC,sha
R=Path(__file__).parent;reflect=np.diag([-1,1,1,1]);source=json.loads((R/'elsa-dress-control-samples.json').read_text());clips=[]
for clip in source['clips']:
 states={};rows=[];worstroot=0;worstlength=0;worstorigin=0;worstaxis=0
 for frame,s in enumerate(clip['samples']):
  e=DressEval();e.overrides={int(k):v for k,v in s['controls'].items()};n=e.native;worlds={};chainrows=[]
  for side,anchorid,containerid,rootid,axisid,upinid,uprefid,bone in [('Left',660,738,968,727,726,725,'dressLeftStart'),('Right',668,753,977,742,741,740,'dressRightStart')]:
   anchor=n.run(anchorid);container=n.run(containerid);constraint=point(anchor,get(DN[rootid],'Data'))
   if side not in states:
    ins,outs=make(anchor[:8],container[:8],orientation=[0,0,0,1],side=side);u.mem_write(ins[2]+0x34,struct.pack('<I',0xfffffffe));states[side]={'memory':bytes(u.mem_read(BASE,0x20000)),'inputs':ins,'outputs':outs,'q':[0,0,0,1]}
   state=states[side];u.mem_write(BASE,state['memory']);ins=state['inputs'];outs=state['outputs'];u.mem_write(ins[0]+0x34,struct.pack('<I',frame));dt=1/30 if frame==0 else s['time']-clip['samples'][frame-1]['time'];u.mem_write(ins[1]+0x34,struct.pack('<f',dt));u.mem_write(ins[5]+0x34,struct.pack('<8f',*anchor[:8]));u.mem_write(ins[6]+0x34,struct.pack('<8f',*container[:8]));u.mem_write(ins[11]+0x34,struct.pack('<3f',*constraint));u.mem_write(BASE+0x4000+21*256+0x34,struct.pack('<4f',*state['q']));invoke(0x4acad0);pos=np.array(positions(outs));state['memory']=bytes(u.mem_read(BASE,0x20000))
   delta=difference(pos[1],pos[0]);localaxis=inverse_vector(delta,anchor);q=aim(localaxis,get(DN[axisid],'Data'),get(DN[upinid],'Data'),get(DN[uprefid],'Data'),initial=state['q']);state['q']=q;assert abs(sum(x*x for x in q)-1)<1e-5
   localpos=inverse_point(pos[0],anchor);raw=native('ConcatenateDilationTransform',q+localpos+[1],anchor);m=affine(raw);worlds[bone]=(reflect@m@reflect).flatten().tolist()
   rooterr=float(np.linalg.norm(pos[0]-constraint));lengtherr=abs(float(np.linalg.norm(pos[1]-pos[0]))-.37*anchor[7]);originerr=float(np.linalg.norm(m[:3,3]-pos[0]));want=delta/np.linalg.norm(delta);actual=m[:3,:3]@np.array(get(DN[axisid],'Data'));actual/=np.linalg.norm(actual);axiserr=float(np.linalg.norm(actual-want));worstroot=max(worstroot,rooterr);worstlength=max(worstlength,lengtherr);worstorigin=max(worstorigin,originerr);worstaxis=max(worstaxis,axiserr)
   if max(rooterr,lengtherr,originerr)>2e-5 or axiserr>5e-3:raise ValueError((side,frame,rooterr,lengtherr,originerr,axiserr))
   chainrows.append({'side':side,'positions':pos.tolist(),'local_aim_quaternion':q,'root_error':rooterr,'length_error':lengtherr,'skin_origin_error':originerr,'skin_axis_error':axiserr})
  rows.append({'time':s['time'],'worlds':worlds,'chains':chainrows})
 clips.append({'name':clip['name'],'duration':clip['duration'],'samples':rows,'max_root_error':worstroot,'max_length_error':worstlength,'max_skin_origin_error':worstorigin,'max_skin_axis_error':worstaxis});print(clip['name'],len(rows),worstroot,worstlength,worstorigin,worstaxis)
report={'exe_sha256':sha,'scope':'Original native DynamicChain dispatch and native aim/inverse transforms on source idle anchors, positive uniform anchor scales. Two-particle state persists between frames; explicit zero external force and previous-frame local-aim feedback. Scene loader/name resolver and complete engine update order not executed. Start resets chain; not guaranteed seamless loop. Particle scalar slot98 kept at original constructor default1.','clips':clips}
(R/'native-dress-reset-only-samples.json').write_text(json.dumps(report,separators=(',',':')))
