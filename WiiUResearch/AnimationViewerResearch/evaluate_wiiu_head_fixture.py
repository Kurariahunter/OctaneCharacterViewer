"""Bounded Wii U source head graph using original-PC numerical operators.
Explicit source-default fixture, three clip-control snapshots. No Wii U code execution.
"""
from pathlib import Path
import json,sys,math
P=Path(__file__).parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from native_pc_dress_math import call
from native_pc_relationship import run as relationship
from native_pc_head_connections import connect
from native_pc_clip_math import rotation
from native_pc_transform_scale import compose,point
from native_pc_lean_ik import sha
from validate_dilation_matrix_pc_native import convert as native_matrix
from native_pc_scaled_connection import connect as scaled_connect

def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
def get(n,k,default=None):return next((c['value']for c in n['children']if c['name']==k),default)
def refs(n):return dict(zip(get(n,'DataNodeAttributes',[]),get(n,'DataNodeRefs',[])))
r=json.loads((P/'WiiUClips/fro_elsa.tree.json').read_text());net=next(n for n in walk(r)if n['name']=='SubNetwork');nodes={int(n['value']):n for n in walk(net)if n['name']=='DataNode'};producers={}
for proc in walk(net):
 if proc['name']!='ProcessorNode':continue
 typ=get(proc,'Type');rr=refs(proc)
 for k,i in rr.items():
  if k.startswith('Output')or(typ.endswith('ComponentProcessorCompose')and k=='Aggregate'):
   assert i not in producers;producers[i]=(proc,k)

def fields(i):
 data=next((c for c in nodes[i]['children']if c['name']=='Data'),None);return {c['name']:c['value']for c in data['children']}if data else {}
def stored(i):
 typ=get(nodes[i],'Type');f=fields(i)
 if typ in ('Float','Rotor','EulerZXY'):
  value=get(nodes[i],'Data')
  if typ=='EulerZXY'and value==[]:value=[0,0,0]
  return value
 if typ=='Dilation':return f.get('Orientation',[0,0,0,1])+f.get('Translation',[0,0,0])+[f.get('Scale',1)]
 if typ=='Transform':return compose(f.get('Orientation',[0,0,0,1]),f.get('Translation',[0,0,0]),f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
 raise ValueError('Unsupported stored type '+typ)
class Eval:
 def __init__(self,frame):self.cache={};self.active=set();self.defaults={};self.operations={};self.overrides={v['source_node']:v['channels']for v in frame['ports'].values()}
 def leaf(self,i):
  v=stored(i);typ=get(nodes[i],'Type');channels=self.overrides.get(i,{})
  if typ=='Float':
   if '10'in channels:v=channels['10']['values'][0]
  elif typ=='Dilation':
   if '0'in channels:v[4:7]=channels['0']['values']
   if '4'in channels:v[:4]=channels['4'].get('derived_quaternion_xyzw',channels['4']['values'])
   for op,index in [(1,4),(2,5),(3,6)]:
    if str(op)in channels:v[index]=channels[str(op)]['values'][0]
   if '5'in channels:
    s=channels['5']['values'];assert max(s)-min(s)<1e-6;v[7]=s[0]
  elif typ=='Transform'and channels:
   assert set(channels)<=set('012345'),'Unsupported Transform clip channel'
   f=fields(i);t=list(f.get('Translation',[0,0,0]));q=f.get('Orientation',[0,0,0,1]);s=list(f.get('Scale',[1]*4))
   if '0'in channels:t=list(channels['0']['values'])
   for op,index in [(1,0),(2,1),(3,2)]:
    if str(op)in channels:t[index]=channels[str(op)]['values'][0]
   if '4'in channels:
    c=channels['4'];q=c.get('derived_quaternion_xyzw',c['values']);assert len(q)==4,'Unresolved Transform Euler input'
   if '5'in channels:
    scale=channels['5']['values'];assert len(scale)==3;s[:3]=scale
   v=compose(q,t,s,f.get('Unscale',[1]*4))
  elif channels:raise ValueError('Unsupported override '+str(i))
  if not channels:self.defaults[i]={'type':typ,'value':v}
  return v
 def run(self,i):
  if i in self.cache:return self.cache[i]
  if i in self.active:raise ValueError('Cycle')
  self.active.add(i);pout=producers.get(i)
  if not pout:v=self.leaf(i)
  else:
   p,output=pout;typ=get(p,'Type');rr=refs(p);self.operations[int(p['value'])]=typ
   if i in self.overrides:raise ValueError('Clip override of produced node '+str(i))
   if typ=='RelationshipProcessor':
    blobnode=rr['RelationshipData'];assert blobnode in(34,41)
    filename='elsa-eyelids.pc-endian.bin'if blobnode==34 else 'relationship-41.pc-endian.bin';values=[self.run(v)for k,v in rr.items()if k.startswith('Input[')];outs=[v for k,v in rr.items()if k.startswith('Output[')]
    result=relationship((P/'WiiUClips'/filename).read_bytes(),values,len(outs))
    for node,value in zip(outs,result):self.cache[node]=value
    v=self.cache[i]
   elif typ in ('ConcatenateChainDilation','ConcatenateChainInverseDilation'):
    args=[self.run(v)for k,v in rr.items()if k!='Output'];normal=sum(k.startswith('Input[')for k in rr);v=call(0x4d1cb0 if typ=='ConcatenateChainDilation'else 0x4d2b00,args,'array',8,normal_input_count=normal if typ.endswith('InverseDilation')else None)
   elif typ=='InvertDilation':v=call(0x4d19c0,[self.run(rr['Input'])],'array',8)
   elif typ in ('DilationOrientationConnection','DilationTranslationOrientationConnection'):
    assert 'TranslateOffset'not in rr;v=connect(self.run(rr['Input']),self.run(rr['RotateOffset'])if 'RotateOffset'in rr else[0,0,0,1],stored(i),typ=='DilationTranslationOrientationConnection')
   elif typ in ('ConcatenateDilationTransform','ConcatenateTransformDilation'):
    v=call(0x57cb30 if typ=='ConcatenateDilationTransform'else 0x4d0c50,[self.run(rr['Left']),self.run(rr['Right'])],'array',16)
   elif typ=='TransformDilationWithDilation':
    v=call(0x4d7310,[self.run(rr['Input']),self.run(rr['Converter'])],'typed',8)
   elif typ=='TransformDilationWithTransform':
    v=call(0x4d78d0,[self.run(rr['Input']),self.run(rr['Converter'])],'typed',8)
   elif typ in ('TransformTransformWithDilation','TransformTransformWithTransform'):
    v=call(0x4d7e90 if typ.endswith('Dilation')else 0x4d82c0,[self.run(rr['Input']),self.run(rr['Converter'])],'typed',16)
   elif typ=='ConcatenateChainTransform':
    args=[self.run(node)for key,node in rr.items()if key.startswith('Input[')]
    assert len(args)==2;v=call(0x57e240,args,'array',16)
   elif typ=='TransformTranslationOrientationScaleConnection':
    assert set(rr)=={'Input','Output'};v=scaled_connect(self.run(rr['Input']),stored(i))
   elif typ=='FloatConnection':v=self.run(rr['Input'])
   elif typ=='EulerZXYComponentProcessorCompose':
    v=stored(i)
    for k,node in rr.items():
     if k!='Aggregate':v['XYZ'.index(k)]=self.run(node)
   elif typ=='EulerZXYToRotorVariantProcessor':
    angles=self.run(rr['Input']);assert max(abs(x)for x in angles)<1e-10,'Nonzero native EulerZXY variant not yet validated';v=rotation(angles)
   elif typ=='DilationComponentProcessorCompose':
    assert set(rr)=={'Orientation','Aggregate'};v=stored(i);v[:4]=self.run(rr['Orientation'])
   else:raise ValueError('Unsupported '+typ+' node '+str(i))
  if isinstance(v,list):assert all(math.isfinite(x)for x in v)
  else:assert math.isfinite(v)
  self.active.remove(i);self.cache[i]=v;return v

def matrix_from_transform(raw):
 origin=point(raw,[0,0,0]);m=[[0.]*4 for _ in range(4)];m[3][3]=1
 for a in range(3):m[a][3]=origin[a]
 for col in range(3):
  v=[0,0,0];v[col]=1;q=point(raw,v)
  for row in range(3):m[row][col]=q[row]-origin[row]
 return m
frames=json.loads((P/'elsa-control-quaternions.json').read_text())['samples'];results=[]
for frame in frames:
 e=Eval(frame);head=e.run(388);headmatrix=matrix_from_transform(head);eyes=[]
 bindings=json.loads((P/'wiiu-skin-associations.json').read_text())
 for binding in [b for b in bindings if b['bone']in ('LowerLidLeft','LowerLidRight','UpperLidLeft','UpperLidRight')]:
  bone=binding['bone'];matrix_id=binding['matrix_node'];influence=binding['influence']
  matrix_proc,_=producers[matrix_id];assert get(matrix_proc,'Type')=='DilationToMatrix4x4VariantProcessor'
  world_id=refs(matrix_proc)['Input'];world_proc,_=producers[world_id];assert get(world_proc,'Type')=='TransformDilationWithTransform'and refs(world_proc)['Converter']==388
  local_id=refs(world_proc)['Input'];local_proc,_=producers[local_id];assert get(local_proc,'Type')=='DilationOrientationConnection'
  converted=refs(local_proc)['Input'];converter_proc,_=producers[converted];assert get(converter_proc,'Type')=='TransformDilationWithDilation'
  converter=refs(converter_proc)['Converter']
  local=e.run(local_id);world=call(0x4d78d0,[local,head],'typed',8)
  packed,m=native_matrix(world);matrix=m.tolist()
  assert all(math.isfinite(v)for row in matrix for v in row)
  eyes.append({'bone':bone,'head_local_source_node':local_id,'world_source_node':world_id,'associated_matrix_node':matrix_id,'skin_influence':influence,'converter_source_node':converter,'evaluated_converter':e.run(converter),'head_local_dilation':local,'world_dilation':world,'native_pc_packed_affine':packed,'world_matrix_column_convention':matrix})
 results.append({'time':frame['time'],'head_source_node':388,'head_transform_payload':head,'head_world_matrix_column_convention':headmatrix,'eyelids':eyes,'stored_default_leaves':e.defaults,'evaluated_processors':e.operations})
report={'scope':'Bounded Wii U source graph replay using original-PC math and byte-equivalent relationship data, explicit source-default leaves and three approximate source-control snapshots. Matrix columns recovered by original-PC point transforms. Not native Wii U execution, full actor state, full palette or live-game parity.','pc_exe_sha256':sha,'samples':results}
(P/'wiiu-head-eyelid-world-fixture.json').write_text(json.dumps(report,indent=2));print('PASS 3 head-world snapshots and 12 eyelid-world outputs with evaluated converters; defaults and processors recorded')



