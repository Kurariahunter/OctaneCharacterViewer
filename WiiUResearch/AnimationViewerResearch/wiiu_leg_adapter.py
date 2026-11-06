"""Wii U leg routing over shared PC evaluator and original numerical helpers.
Only differing source dependencies are dispatched here; no PC graph mutation.
"""
import base64,numpy as np
from wiiu_pc_graph_adapter import get,refs,relationship_little
from native_pc_dress_math import call,inverse_point,difference
from native_pc_transform_scale import compose,point
from native_pc_relationship import run as relationship
from native_pc_lean_ik import solve
from native_pc_head_connections import connect
from evaluate_pc_arms import rotor
from evaluate_pc_raw_transform import dilation

class SourceLegEval:
 def __init__(self,adapter,audit,pc):
  self.a=adapter;self.pc=pc;self.rows={r['source_node']:r for r in audit['rows']};self.cache={};self.active=set();self.compat_cache={};self.operations={};self.solvers={};self.blobs={}
 def compatible(self,i,seen=None):
  if i in self.compat_cache:return self.compat_cache[i]
  seen=set()if seen is None else seen
  if i in seen:return False
  seen=set(seen);seen.add(i);r=self.rows.get(i)
  if not r or not all(r[k]for k in ('same_type','processor_equivalent','stored_data_equivalent')):return False
  if r['relationship_equivalence']and not r['relationship_equivalence']['byte_equal']:return False
  p=self.a.producers.get(i)
  if p:
   if get(p[0],'Type')=='DynamicChain':return False
   for k,v in refs(p[0]).items():
    if not k.startswith('Output')and k!='Aggregate'and v!=i and not self.compatible(v,seen):return False
  self.compat_cache[i]=True;return True
 def fields(self,i):
  data=next((c for c in self.a.nodes[i]['children']if c['name']=='Data'),None)
  return {c['name']:c.get('value')for c in data['children']}if data else {}
 def stored(self,i):
  typ=get(self.a.nodes[i],'Type');f=self.fields(i)
  if typ=='Dilation':return f.get('Orientation',[0,0,0,1])+f.get('Translation',[0,0,0])+[f.get('Scale',1)]
  if typ=='Transform':return compose(f.get('Orientation',[0,0,0,1]),f.get('Translation',[0,0,0]),f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
  return get(self.a.nodes[i],'Data')
 def run(self,i):
  if i in self.cache:return self.cache[i]
  if i in self.active:raise ValueError('Wii U leg cycle '+str(i))
  typ=get(self.a.nodes[i],'Type')
  if self.compatible(i):
   target=self.a.mapping[i]
   if typ=='Transform':value=self.pc.raw.run(target)
   else:
    m=self.pc.run(target)
    if typ=='Dilation':value=dilation(m)
    elif typ=='Rotor':value=rotor(m)
    elif np.ndim(m)==0:value=float(m)
    else:value=np.asarray(m).tolist()
   self.cache[i]=value;return value
  self.active.add(i);producer=self.a.producers.get(i)
  if not producer:raise ValueError('Unmapped leg leaf '+str(i))
  p,output=producer;pt=get(p,'Type');rr=refs(p);self.operations[int(p['value'])]=pt
  if pt=='RelationshipProcessor':
   node=rr['RelationshipData'];assert node in (39,40)
   blob=relationship_little(base64.b64decode(get(self.a.nodes[node],'RelationshipDataBlock')));self.blobs[node]=blob
   values=[self.run(v)for k,v in rr.items()if k.startswith('Input[')];outs=[v for k,v in rr.items()if k.startswith('Output[')]
   assert len(values)==len(outs)==4 and all(abs(v)<=100 for v in values)
   for n,v in zip(outs,relationship(blob,values,len(outs))):self.cache[n]=v
   value=self.cache[i]
  elif pt in ('ConcatenateChainDilation','InvertConcatenateChainDilation','ConcatenateChainInverseDilation'):
   args=[self.run(v)for k,v in rr.items()if k!='Output'];fn={'ConcatenateChainDilation':0x4d1cb0,'InvertConcatenateChainDilation':0x4d2370,'ConcatenateChainInverseDilation':0x4d2b00}[pt]
   value=call(fn,args,'array',8,normal_input_count=sum(k.startswith('Input[')for k in rr)if pt=='ConcatenateChainInverseDilation'else None)
  elif pt in ('InvertTransform','InvertDilation'):
   value=call(0x4d1a60 if pt=='InvertTransform'else 0x4d19c0,[self.run(rr['Input'])],'array',16 if pt=='InvertTransform'else 8)
  elif pt in ('ConcatenateDilationTransform','ConcatenateTransformDilation','ConcatenateInverseTransformDilation','ConcatenateChainTransform','InvertConcatenateChainTransform'):
   fn={'ConcatenateDilationTransform':0x57cb30,'ConcatenateTransformDilation':0x4d0c50,'ConcatenateInverseTransformDilation':0x4d1220,'ConcatenateChainTransform':0x57e240,'InvertConcatenateChainTransform':0x4d2540}[pt]
   value=call(fn,[self.run(v)for k,v in rr.items()if k!='Output'],'array',16)
  elif pt=='TransformDilationWithTransform':value=call(0x4d78d0,[self.run(rr['Input']),self.run(rr['Converter'])],'typed',8)
  elif pt in ('TransformTransformWithDilation','TransformTransformWithTransform'):
   value=call(0x4d7e90 if pt.endswith('Dilation')else 0x4d82c0,[self.run(rr['Input']),self.run(rr['Converter'])],'typed',16)
  elif pt in ('DilationOrientationConnection','DilationTranslationOrientationConnection','TransformTranslationOrientationConnection'):
   inp=self.run(rr['Input']);value=connect(inp,self.run(rr['RotateOffset'])if 'RotateOffset'in rr else[0,0,0,1],self.stored(i),pt!='DilationOrientationConnection',input_transform=get(self.a.nodes[rr['Input']],'Type')=='Transform',output_transform=typ=='Transform',translate_offset=self.run(rr['TranslateOffset'])if 'TranslateOffset'in rr else None)
  elif pt=='IkLean2LinkProcessor':
   assert self.run(rr['Axis'])==[1,0,0]
   values=[self.run(rr[k])for k in ('StartPosition','MidPosition','EndPosition','Target','PoleVector')]+[None,[self.run(rr['Twist'])],[1.]]
   outputs=solve(values);self.solvers[int(p['value'])]={'inputs':values,'outputs':[list(v)for v in outputs]}
   for key,v in zip(('StartOrientation','MidOrientation','Scale'),outputs):
    if key in rr:self.cache[rr[key]]=list(v)if key!='Scale'else float(v[0])
   value=self.cache[i]
  elif pt=='ShrinkingVolumeScaleZ':value=call(0x4c8b40,[[self.run(rr['Input'])]],'typed',4)
  elif pt=='ScaleConnection':value=self.run(rr['Input'])
  elif pt=='UnitRotor3dConnection':value=self.run(rr['Input'])
  elif pt=='DilationComponentProcessorCompose':
   value=self.stored(i);args={k:self.run(v)for k,v in rr.items()if k!='Aggregate'}
   assert set(args)<=set(('Orientation','Translation'))
   if 'Orientation'in args:value[:4]=args['Orientation']
   if 'Translation'in args:value[4:7]=args['Translation']
  elif pt=='FloatNegate':value=-self.run(rr['Input'])
  elif pt=='Position3dOffsetProcessor':value=(np.array(self.run(rr['Input']))+self.run(rr['Offset'])).tolist()
  elif pt=='Position3dDifferenceProcessor':value=difference(self.run(rr['To']),self.run(rr['From']))
  elif pt=='TransformPositionWithDilation':value=call(0x4d4b40,[self.run(rr['Input']),self.run(rr['Converter'])],'typed',3)
  elif pt=='InverseTransformPositionWithTransform':value=inverse_point(self.run(rr['Input']),self.run(rr['Converter']))
  elif pt=='TransformComponentProcessorCompose':
   f=self.fields(i);args={k:self.run(v)for k,v in rr.items()if k!='Aggregate'}
   assert set(args)<=set(('Translation','Orientation','Scale','Unscale'))
   value=compose(args.get('Orientation',f.get('Orientation',[0,0,0,1])),args.get('Translation',f.get('Translation',[0,0,0])),args.get('Scale',f.get('Scale',[1]*4)),args.get('Unscale',f.get('Unscale',[1]*4)))
  else:raise ValueError('Unsupported Wii U leg processor '+pt+' node '+str(i))
  assert np.isfinite(value).all(),(i,pt,value);self.cache[i]=value;self.active.remove(i);return value
