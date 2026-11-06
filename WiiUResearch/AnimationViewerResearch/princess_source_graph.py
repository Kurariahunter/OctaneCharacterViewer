"""Explicit source graph trial; no Elsa node mappings or guessed bone parents."""
import json,copy,base64,numpy as np
from pathlib import Path
from wiiu_pc_graph_adapter import P,get,refs,walk,producer_map,relationship_little
from wiiu_leg_adapter import SourceLegEval
from native_pc_transform_scale import compose
from native_pc_dress_math import call,aim,inverse_vector
from native_pc_relationship import run as relationship
from native_pc_clip_math import rotation
from native_pc_scaled_connection import connect as scaled_connect

class Graph:
 def __init__(self,path):
  self.tree=json.loads(Path(path).read_text());self.byte_order=self.tree.get('byte_order','>');self.net=next(n for n in walk(self.tree)if n['name']=='SubNetwork');self.nodes={int(n['value']):n for n in walk(self.net)if n['name']=='DataNode'};self.producers=producer_map(self.net)
  layout=get(self.net,'HeaderLayout');indices=get(self.net,'HeaderStringIndices');strings=get(self.net,'HeaderStrings');parents={};cursor=1
  for parent,count in zip(layout[::2],layout[1::2]):
   for i in range(cursor,cursor+count):parents[i]=parent
   cursor+=count
  self.paths={}
  for i,n in self.nodes.items():
   h=get(n,'Header');parts=[]
   while h:parts.append(strings[indices[h-1]]);h=parents[h]
   self.paths[i]='|'.join(reversed(parts))
class Eval(SourceLegEval):
 def __init__(self,a,frame):
  super().__init__(a,{'rows':[]},None);self.overrides={}
  for r in frame['ports'].values():
   i=r['source_node']
   if i is None or i in a.producers:continue
   f=self.fields(i)
   for key,ch in r['channels'].items():
    op=int(key);v=ch.get('derived_quaternion_xyzw',ch['values'])
    if op==0:f['Translation']=v
    elif op in(1,2,3):f.setdefault('Translation',[0,0,0])[op-1]=v[0]
    elif op==4:f['Orientation']=v
    elif op==5:
     if get(a.nodes[i],'Type')=='Dilation':
      if max(v)-min(v)>1e-6:raise ValueError('Nonuniform scale on Dilation '+str(i))
      f['Scale']=float(v[0])
     else:f['Scale']=v+[f.get('Scale',[1]*4)[3]]
    elif op in(6,7,8):
     if get(a.nodes[i],'Type')=='Dilation':raise ValueError('Component scale on Dilation '+str(i))
     f.setdefault('Scale',[1]*4)[op-6]=v[0]
    elif op==10:f['Value']=v[0]
    else:raise ValueError('Unhandled source control channel '+str(op))
   self.overrides[i]=f
 def compatible(self,i,seen=None):return False
 def fields(self,i):return copy.deepcopy(self.overrides[i])if hasattr(self,'overrides')and i in self.overrides else super().fields(i)
 def stored(self,i):
  typ=get(self.a.nodes[i],'Type');f=self.fields(i)
  if typ=='Dilation':return f.get('Orientation',[0,0,0,1])+f.get('Translation',[0,0,0])+[f.get('Scale',1)]
  if typ=='Transform':return compose(f.get('Orientation',[0,0,0,1]),f.get('Translation',[0,0,0]),f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
  if typ=='EulerZXY':return get(self.a.nodes[i],'Data')or[0,0,0]
  if typ=='Float':return f.get('Value',get(self.a.nodes[i],'Data',0.))
  return get(self.a.nodes[i],'Data',{'Rotor':[0,0,0,1],'Vector':[0,0,0],'Position':[0,0,0],'EulerZXY':[0,0,0],'Scale':[1]*4}.get(typ))
 def run(self,i):
  if i in self.cache:return self.cache[i]
  p=self.a.producers.get(i)
  if not p:
   v=self.stored(i)
   if v is None:raise ValueError('Unresolved source leaf '+str(i))
   self.cache[i]=v;return v
  proc,output=p;typ=get(proc,'Type');rr=refs(proc)
  supported={'UnitRotor3dNormalizedWeightedAverageProcessor','UnitRotor3dWeightedAverageProcessor','UnitRotor3dOffsetProcessor','TransformVectorWithDilation','RotorToEulerZXYVariantProcessor','EulerZXYComponentProcessorDecompose','RelationshipProcessor','DilationComponentProcessorDecompose','TransformComponentProcessorDecompose','FloatMultiply','Position3dConnection','FloatConnection','EulerZXYToRotorVariantProcessor','EulerZXYComponentProcessorCompose','DilationComponentProcessorCompose','TransformDilationWithDilation','ConcatenateChainInverseTransform','ConcatenateInverseDilationTransform','AimConstraintProcessorNode','InverseTransformVectorWithTransform','TransformTranslationOrientationScaleConnection'}
  if typ not in supported:return super().run(i)
  if i in self.active:raise ValueError('Source cycle '+str(i))
  self.active.add(i)
  if typ=='RelationshipProcessor':
   raw_blob=base64.b64decode(get(self.a.nodes[rr['RelationshipData']],'RelationshipDataBlock'));blob=relationship_little(raw_blob)if self.a.byte_order=='>'else raw_blob;inputs=[self.run(v)for k,v in rr.items()if k.startswith('Input[')];outputs=[v for k,v in rr.items()if k.startswith('Output[')]
   initial=[]
   for n in outputs:
    value=self.stored(n);initial.append(value if get(self.a.nodes[n],'Type')in('Transform','Dilation')else([float(value)]+[0]*7 if np.ndim(value)==0 else list(value)+[0]*(8-len(value))))
   for n,v in zip(outputs,relationship(blob,inputs,len(outputs),initial_outputs=initial,output_types=[get(self.a.nodes[n],'Type')for n in outputs])):
    typout=get(self.a.nodes[n],'Type');self.cache[n]=v[0]if typout=='Float'else v[:3]if typout in('Position','Vector','EulerZXY')else v[:4]if typout in('Rotor','Scale')else v
   value=self.cache[i]
  elif typ in('DilationComponentProcessorDecompose','TransformComponentProcessorDecompose'):
   raw=self.run(rr['Aggregate']);slices={'Orientation':raw[:4],'Translation':raw[4:7],'Scale':raw[7]if len(raw)==8 else raw[8:12],'Unscale':raw[12:16]};value=slices[output]
  elif typ=='DilationComponentProcessorCompose':
   value=self.stored(i)
   for k,n in rr.items():
    if k=='Orientation':value[:4]=self.run(n)
    elif k=='Translation':value[4:7]=self.run(n)
    elif k=='Scale':value[7]=self.run(n)
    elif k!='Aggregate':raise ValueError('Unknown Dilation field '+k)
  elif typ=='FloatMultiply':value=call(0x52d540,[[self.run(n)]for k,n in rr.items()if k.startswith('Input[')],'array',1)[0]
  elif typ=='RotorToEulerZXYVariantProcessor':
   from native_pc_forearm_twist import euler
   value=euler(self.run(rr['Input']))
  elif typ=='EulerZXYComponentProcessorDecompose':value=self.run(rr['Aggregate'])['XYZ'.index(output)]
  elif typ in('Position3dConnection','FloatConnection'):value=self.run(rr['Input'])
  elif typ=='EulerZXYToRotorVariantProcessor':value=rotation(self.run(rr['Input']))
  elif typ=='EulerZXYComponentProcessorCompose':
   value=list(self.stored(i));idx={'X':0,'Y':1,'Z':2}
   for k,n in rr.items():
    if k!='Aggregate':value[idx[k]]=self.run(n)
  elif typ=='TransformDilationWithDilation':value=call(0x4d1cb0,[self.run(rr['Input']),self.run(rr['Converter'])],'array',8)
  elif typ=='ConcatenateChainInverseTransform':
   args=[call(0x4d1a60,[self.run(n)],'array',16)if k.startswith('Invert')else self.run(n)for k,n in rr.items()if k!='Output'];value=args[0]
   for v in args[1:]:value=call(0x57e240,[value,v],'array',16)
  elif typ=='ConcatenateInverseDilationTransform':value=call(0x57cb30,[self.run(rr['Left']),call(0x4d1a60,[self.run(rr['Right'])],'array',16)],'array',16)
  elif typ=='AimConstraintProcessorNode':value=aim(*[self.run(rr[k])for k in('AlignInput','AlignReference','UpInput','UpReference')])
  elif typ=='InverseTransformVectorWithTransform':value=inverse_vector(self.run(rr['Input']),self.run(rr['Converter']))
  elif typ=='UnitRotor3dNormalizedWeightedAverageProcessor':
   inputs=[self.run(n)for k,n in rr.items()if k.startswith('TargetInput[')];weights=[[self.run(n)]for k,n in rr.items()if k.startswith('TargetWeight[')];assert len(inputs)==2 and len(weights)==1;value=call(0x4d9ee0,inputs+weights,'array',4)
  elif typ=='UnitRotor3dWeightedAverageProcessor':
   inputs=[self.run(n)for k,n in rr.items()if k.startswith('TargetInput[')];weights=[[self.run(n)]for k,n in rr.items()if k.startswith('TargetWeight[')];assert len(inputs)==len(weights)==2 and all(abs(w[0]-1)<1e-6 for w in weights);value=call(0x4d9ed0,inputs+weights,'array',4)
  elif typ=='UnitRotor3dOffsetProcessor':value=call(0x4d1cb0,[self.run(rr['Offset'])+[0,0,0,1],self.run(rr['Input'])+[0,0,0,1]],'array',8)[:4]
  elif typ=='TransformVectorWithDilation':
   from native_pc_eye_vector import transform
   value=transform(self.run(rr['Input']),self.run(rr['Converter']))
  elif typ=='TransformTranslationOrientationScaleConnection':
   assert set(rr)<=set(('Input','Output','TranslateOffset','RotateOffset'));value=scaled_connect(self.run(rr['Input']),self.stored(i),self.run(rr['TranslateOffset'])if 'TranslateOffset'in rr else None,self.run(rr['RotateOffset'])if 'RotateOffset'in rr else None)
  assert np.isfinite(value).all();self.cache[i]=value;self.active.remove(i);return value
