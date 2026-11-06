"""Ahsoka body-animation trial with explicit bind-relative secondary-motion fixtures."""
import json,sys,base64,hashlib,numpy as np
from pathlib import Path
from princess_source_graph import Graph,Eval,P,get,walk
from bake_wiiu_clip import matrix
from wiiu_clip_sampler import WiiUClip
Q=P/'AhsokaTrial';a=Graph(Q/'ahsoka.tree.json');raw=json.loads((Q/'Assets/mesh.json').read_text());bindings=json.loads((Q/'bindings.json').read_text());bybone={b['bone']:b for b in bindings};inf={get(n,'Name'):n for n in walk(a.tree)if n['name']=='Influence'};R=np.diag([-1,1,1,1]);worlds={n:np.linalg.inv(np.array(get(inf[n],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T)for n in raw['bones']}
fallback={n:('Head'if n.startswith('hair')else'Hips')for n in raw['bones']if n.startswith(('hair','Cloth'))};assert len(fallback)==8;relative={n:np.linalg.inv(worlds[parent])@worlds[n]for n,parent in fallback.items()};clips=[];skipped=set()
for name in ['ahsoka_bm_idle_dynamic','ahsoka_bm_idle_saber_off','ahsoka_bm_idle_saber_on']:
 clip=WiiUClip(Q/'Assets'/f'{name}.oct.clipdata',Q/'ahsoka.tree.json');frames=clip.frames();samples=[]
 for index,frame in enumerate(frames):
  e=Eval(a,frame);poses={}
  for n in raw['bones']:
   if n not in fallback:poses[n]=matrix(e.run(bybone[n]['source_node']))
  for n,parent in fallback.items():poses[n]=poses[parent]@relative[n]
  out=[]
  for n in raw['bones']:
   m=poses[n];assert np.isfinite(m).all()and np.linalg.det(m[:3,:3])>1e-8,(name,n,frame['time']);out.append({'bone':n,'matrix':(R@m@R).flatten().tolist()})
  samples.append({'time':frame['time']-clip.lo,'transforms':out});skipped.update(r['source_node']for r in frame['ports'].values()if r['source_node']in a.producers)
  if index%60==0:print(name,index,'/',len(frames),flush=True)
 clips.append({'name':'WiiU_tcw_'+name,'duration':clip.hi-clip.lo,'samples':samples,'clipdata_sha256':clip.sha})
sha=hashlib.sha256((Q/'Assets/tcw_ahsoka.oct').read_bytes()).hexdigest();model={'source':'Actual Wii U tcw_ahsoka mesh/weights; plain materials in this trial.','vertices':raw['skinPositions'],'uv':raw['uv'],'bones':raw['bones'],'weights':[{'indices':i,'weights':w}for i,w in zip(raw['indices'],raw['weights'])],'bindposes':[(R@np.linalg.inv(worlds[n])@R).flatten().tolist()for n in raw['bones']],'parts':[{'triangles':t,'texture':None}for t in raw['triangles']]}
cache={'model_sha256':sha,'reference_rig_adapter':True,'reference_source_outputs':62,'source_skin_nodes':{n:bybone[n]['source_node']for n in raw['bones']if n not in fallback},'fallback_parents':fallback,'scope':'Ahsoka source body graph:62evaluated outputs,8explicit bind-relative secondary fixtures. No Elsa retargeting. Not full native/game parity.','fixture_assumptions':['Six hair outputs follow Head bind-relative;two cloth outputs follow Hips bind-relative. Four native dynamic chains NOT evaluated.','Direct source clips; actor-layer scheduling and additive context not reconstructed.','Plain materials; source texture application pending.'],'clips':clips}
(Q/'ahsoka-model.json').write_text(json.dumps(model,separators=(',',':')),encoding='utf-8');(Q/'ahsoka-animation.json').write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8');(Q/'bake-validation.json').write_text(json.dumps({'model_sha256':sha,'source_outputs':62,'fallback_outputs':8,'fallback_parents':fallback,'computed_clip_controls_not_overwritten':sorted(skipped),'clips':[{'name':c['name'],'samples':len(c['samples'])}for c in clips]},indent=2),encoding='utf-8');print('PASS',sha,flush=True)
