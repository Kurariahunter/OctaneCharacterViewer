"""Wii U forward walk/run composition fixtures, source-declared tracks and native blend."""
import json,sys,struct,base64,hashlib,copy,numpy as np
from pathlib import Path
from bake_wiiu_clip import matrix
from wiiu_pc_graph_adapter import Adapter,P,refs,get,walk
from wiiu_clip_sampler import WiiUClip
from wiiu_dress_adapter import DressStates,SourceDressEval
from evaluate_pc_dress import DressEval
from pc_graph_controls import apply
from pc_finger_controls import prepare_fingers
from native_pc_clip_buffer_blend import apply_layer
from inspect_pc_run_lean import read_static
sys.path.insert(0,str(P.parent/'OCTParser'))
from read_binary_tup import parse

class ScaledEval(DressEval):
 def run(self,i):
  if i in(644,650)and i in self.overrides:
   if i not in self.cache:self.cache[i]=matrix(self.raw.run(i))
   return self.cache[i]
  return super().run(i)

def lean_tracks(a):
 f=P/'ClipExpansion/Locomotion/human_bm_runf_lean_add.oct';r=parse(f);raw=base64.b64decode(next(n['value']['base64']for n in r['nodes']if n['key']=='ClipDataBlock'));pool,start=struct.unpack_from('>II',raw,12);dst=bytearray(raw)
 for at in [0,4,12,16]:dst[at:at+4]=raw[at:at+4][::-1]
 for at in list(range(8,12,2))+list(range(start,pool,2)):dst[at:at+2]=raw[at:at+2][::-1]
 for at in range(pool,len(raw),4):dst[at:at+4]=raw[at:at+4][::-1]
 tracks=read_static(bytes(dst))['tracks'];link=next(n for n in walk(a.tree)if n['name']=='BaseDataNodeLinks');net=next(n for n in walk(a.tree)if n['name']=='SubNetwork')
 shorts=lambda v:struct.unpack('>'+str(len(base64.b64decode(v))//2)+'H',base64.b64decode(v))
 used=get(net,'ConnectionMapUsedDataNodes');lookup={port:used[slot]for slot,port in zip(shorts(get(link,'LocalUsedDataNodeIndices')),shorts(get(link,'LocalToPortIndices')))}
 for row in tracks:
  source=lookup[row['port']];row['source_node']=a.mapping[source];row['wiiu_source_node']=source
 return tracks

def bake(mode):
 a=Adapter();audit=a.audit();folder=P/'ClipExpansion/Locomotion';clip=WiiUClip(folder/f'grl_bm_{mode}f.oct.clipdata');upper=WiiUClip(folder/f'grl_bm_{mode}_upbody_add.oct.clipdata');base=WiiUClip(P/'ClipExpansion/Extracted/elsa_bm_idle_passive.oct.clipdata');lean=lean_tracks(a);weight=.5 if mode=='walk'else 1.
 # Validate the exact authored forward group before admitting this composition.
 sys.path.insert(0,str(P.parents[1]/'ElsaSceneResearch'));from pc_banm_declarations import parse as parse_banm,descendants
 ast=parse_banm((folder/'grl_bm_walkrun.banm').read_text(encoding='utf-8-sig'));group=next(n for n in descendants(ast)if n['field']=='GroupTrack'and n['label']==mode.title()+' Forward');tracks=[{v['field']:v.get('value')for v in n['children']}for n in descendants(group['children'])if n['field']=='ReferencedTrack']
 assert [Path(t['Filename']).name for t in tracks]==[f'grl_bm_{mode}f.oct',f'grl_bm_{mode}_upbody_add.oct','human_bm_runf_lean_add.oct'];assert tracks[2]['BlendMethod']==1 and tracks[2].get('Weight',1)==weight
 bindings=json.loads((P/'wiiu-skin-associations.json').read_text());states=DressStates(a);R=np.diag([-1,1,1,1]);samples=[];checks=[];cycles=4;duration=(clip.hi-clip.lo)*cycles;count=round(duration*60);dt=duration/count
 for tick in range(120+count+1):
  local=max(0,tick-120);phase=(local%(count//cycles))/(count//cycles);pc=ScaledEval()
  apply(pc,a.controls(base.sample(base.lo)));apply(pc,a.controls(clip.sample(clip.lo+phase*(clip.hi-clip.lo))),allow_transform_scale=True);apply(pc,a.controls(upper.sample(upper.lo+phase*(upper.hi-upper.lo))))
  for row in lean:
   node=row['source_node'];fields=pc.overrides.get(node)
   if fields is None:
    data=next((c for c in a.nodes[row['wiiu_source_node']]['children']if c['name']=='Data'),{'children':[]});fields={c['name']:copy.deepcopy(c['value'])for c in data['children']};pc.overrides[node]=fields
   delta={};mask=0
   for d in row['descriptors']:
    if d['opcode']==0:delta['Translation']=d['values'];mask|=7
    elif d['opcode']==4:delta['Orientation']=d['values'];mask|=0x100
    else:raise ValueError('Unsupported lean channel')
   value=apply_layer(fields,delta,mask,weight=weight,additive=True)
   if mask&7:fields['Translation']=value['Translation']
   if mask&0x100:fields['Orientation']=value['Orientation']
  prepare_fingers(pc);source=SourceDressEval(a,audit,pc,states,tick,1/60 if tick<120 else dt);out=[]
  for b in bindings:
   node=refs(a.producers[b['matrix_node']][0])['Input'];m=matrix(source.run(node));assert np.isfinite(m).all()and np.linalg.det(m[:3,:3])>1e-8;out.append({'bone':b['bone'],'matrix':(R@m@R).flatten().tolist()})
  assert len(source.chain_checks)==3 and all(c['native_last_frame']==tick for c in source.chain_checks);checks.extend(source.chain_checks)
  if tick>=120 and(local%2==0 or local==count):samples.append({'time':local*dt,'transforms':out})
  if tick%120==0:print(mode,tick,'/',120+count+1,flush=True)
 cache=json.loads((P/'wiiu-source-mesh-animation-full.json').read_text());cache['clips']=[{'name':f'WiiU_grl_{mode}_forward_composed','duration':duration,'samples':samples,'cycles':cycles}];cache['scope']='Source-declared Wii U locomotion tracks on Elsa mesh, unit assignments and passive initializer fixture, native lean blend, no runtime actor-layer parity.'
 report={'mode':mode,'tracks':tracks,'poses':len(samples),'cycles':cycles,'chain_checks':len(checks),'max_root_error':max(c['root_error']for c in checks),'max_length_error':max(c['segment_length_error']for c in checks),'fixtures':['Passive idle phase zero initialization','Unit lower/upper assignments, phase normalized per cycle','120tickwarmup,PCgravity,nocollision','Native lean additive mapping reused from PC research; Wii U live blend not captured']}
 target=P/'ClipExpansion'/f'wiiu-{mode}-forward.animation.json';target.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8');target.with_suffix('.validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS',mode,len(samples),flush=True)
if __name__=='__main__':
 for mode in sys.argv[1:]:bake(mode)
