"""Bake Princess trial using her own source graph and townsperson clip controls."""
import sys,json,base64,hashlib,numpy as np
from pathlib import Path
from princess_source_graph import Graph,Eval,P,walk,get
from bake_wiiu_clip import matrix
from wiiu_clip_sampler import WiiUClip
sys.path.insert(0,str(P.parent/'OCTParser'));from read_binary_tup import parse
Q=P/'PrincessTrial';a=Graph(Q/'princess.tree.json');mesh=json.loads((Q/'Assets/mesh.json').read_text());bindings=json.loads((Q/'bindings.json').read_text());bybone={b['bone']:b for b in bindings};inf={get(n,'Name'):n for n in walk(a.tree)if n['name']=='Influence'};R=np.diag([-1,1,1,1]);sha=hashlib.sha256((Q/'Assets/psx_princess.oct').read_bytes()).hexdigest();clips=[]
for name in ['twnla_bm_idle_active','twnla_bm_idle_passive']:
 path=Q/'Assets'/f'{name}.oct';parsed=parse(path);raw=base64.b64decode(next(n['value']['base64']for n in parsed['nodes']if n['key']=='ClipDataBlock'));cp=path.with_suffix('.oct.clipdata');cp.write_bytes(raw);clip=WiiUClip(cp,Q/'princess.tree.json');samples=[]
 for index,frame in enumerate(clip.frames()):
  e=Eval(a,frame);out=[]
  for bone in mesh['bones']:
   m=matrix(e.run(bybone[bone]['source_node']));assert np.isfinite(m).all()and np.linalg.det(m[:3,:3])>1e-8,(bone,frame['time'],m.tolist());out.append({'bone':bone,'matrix':(R@m@R).flatten().tolist()})
  samples.append({'time':frame['time']-clip.lo,'transforms':out})
  if index%60==0:print(name,index,flush=True)
 clips.append({'name':'WiiU_psx_princess_'+name,'duration':clip.hi-clip.lo,'samples':samples,'clipdata_sha256':clip.sha})
model={'source':'Actual Wii U psx_princess mesh,source54influences,sourceweights; plain materials pending texture decoding.','vertices':mesh['positions'],'uv':mesh['uv'],'bones':mesh['bones'],'weights':[{'indices':i,'weights':w}for i,w in zip(mesh['indices'],mesh['weights'])],'bindposes':[(R@np.array(get(inf[bone],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T@R).flatten().tolist()for bone in mesh['bones']],'parts':[{'triangles':t,'texture':None}for t in mesh['triangles']]}
cache={'model_sha256':sha,'reference_rig_adapter':True,'reference_source_outputs':54,'source_skin_nodes':{bone:bybone[bone]['source_node']for bone in mesh['bones']},'fallback_parents':{},'scope':'Princess own54-bone source graph and townsperson controls; shared original PC numeric routines; no Elsa mapping,retargeting or live Wii U parity.','fixture_assumptions':['Direct source clip on source graph without actor layer scheduling.','Plain materials; no texture substitution.'],'clips':clips}
(Q/'princess-model.json').write_text(json.dumps(model,separators=(',',':')),encoding='utf-8');(Q/'princess-animation.json').write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8');(Q/'bake-validation.json').write_text(json.dumps({'model_sha256':sha,'bones':54,'vertices':len(mesh['positions']),'clips':[{'name':c['name'],'samples':len(c['samples'])}for c in clips],'fallbacks':0,'finite_positive_palettes':True},indent=2),encoding='utf-8');print('PASS',sha,flush=True)
