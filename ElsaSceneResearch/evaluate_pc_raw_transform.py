"""Native Transform payload propagation on explicit Elsa skin-output paths.
Dilation/control dependencies remain in the bounded FootEval; no loader claim.
"""
import json
import numpy as np
from pathlib import Path
from evaluate_pc_arms import DN,PROD,get,quat,stored,rotor

from native_pc_transform_scale import compose,point
from native_pc_dress_math import call
SPECS={'TransformDilationWithTransform':(0x4d78d0,'typed',8),'ConcatenateInverseTransformDilation':(0x4d1220,'array',16),'InvertConcatenateChainTransform':(0x4d2540,'array',16)}
def native(name,a,b=None):
 fn,layout,count=SPECS[name];return call(fn,[a] if b is None else [a,b],'typed' if layout=='typed' else 'array',count)
SPECS.update({'ConcatenateTransformDilation':(0x4d0c50,'array',16),'InvertTransform':(0x4d1a60,'unary',16),'ConcatenateChainTransform':(0x57e240,'array',16),'ConcatenateDilationTransform':(0x57cb30,'array',16)})

def dilation(m):
 scale=float(np.linalg.norm(m[:3,0]));r=m[:3,:3]/scale
 if max(abs(np.linalg.norm(m[:3,:3],axis=0)-scale))>1e-5 or np.max(abs(r.T@r-np.eye(3)))>1e-5:raise ValueError('nonuniform Dilation dependency')
 return rotor(r)+m[:3,3].tolist()+[scale]

def affine(raw):
 origin=point(raw,[0,0,0]);m=np.eye(4);m[:3,3]=origin
 for j in range(3):
  v=np.zeros(3);v[j]=1;m[:3,j]=point(raw,v)-origin
 return m

class NativeSkinEval:
 def __init__(self,e):self.e=e;self.cache={};self.visited=set()
 def rotation(self,i):
  prod=PROD.get(i)
  if prod:
   p,a=prod;typ=get(p,"Type");refs=dict(zip(get(p,"DataNodeAttributes"),get(p,"DataNodeRefs")))
   if typ=="UnitRotor3dConnection":return self.rotation(refs["Input"])
   if typ=="UnitRotor3dOffsetProcessor":return self.rotation(refs["Input"])@self.rotation(refs["Offset"])
   if typ in ("DilationComponentProcessorDecompose","TransformComponentProcessorDecompose") and a=="Orientation":return quat(self.run(refs["Aggregate"])[:4])
  return self.e.run(i)
 def run(self,i):
  if i in self.cache:return self.cache[i]
  if get(DN[i],'Type')!='Transform':
   prod=PROD.get(i)
   if prod:
    p,a=prod;typ=get(p,'Type');refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
    if typ=='TransformDilationWithTransform':return native(typ,self.run(refs['Input']),self.run(refs['Converter']))
    if typ=='DilationComponentProcessorCompose' and 'Orientation' in refs:
     m=stored(DN[i]);r=self.rotation(refs['Orientation']);scale=float(np.linalg.norm(m[:3,0]));t=self.e.run(refs['Translation']) if 'Translation' in refs else m[:3,3]
     return rotor(r)+list(t)+[scale]
   try:return dilation(self.e.run(i))
   except ValueError as ex:raise ValueError('Dilation node '+str(i)+' '+str(ex)) from ex
  self.visited.add(i);pout=PROD.get(i);data=next((c for c in DN[i]['children'] if c['name']=='Data'),None);f={c['name']:c['value'] for c in data['children']} if data else {}
  if not pout:
   f.update(self.e.overrides.get(i,{}));out=compose(f.get('Orientation',[0,0,0,1]),f.get('Translation',[0,0,0]),f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
  else:
   p,attr=pout;typ=get(p,'Type');pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
   if typ=='TransformComponentProcessorCompose':
    inputs={a:(self.rotation(v) if a=='Orientation' else self.e.run(v)) for a,v in pairs if a!='Aggregate'}
    out=compose(rotor(inputs['Orientation']) if 'Orientation' in inputs else f.get('Orientation',[0,0,0,1]),inputs.get('Translation',f.get('Translation',[0,0,0])),inputs.get('Scale',f.get('Scale',[1]*4)),inputs.get('Unscale',f.get('Unscale',[1]*4)))
   elif typ in ('TransformTransformWithDilation','TransformTransformWithTransform'):
    refs=dict(pairs);out=call(0x4d7e90 if typ.endswith('Dilation')else 0x4d82c0,[self.run(refs['Input']),self.run(refs['Converter'])],'typed',16)
   elif typ=='ConcatenateChainInverseTransform':
    values=[native('InvertTransform',self.run(v))if a.startswith('Invert')else self.run(v)for a,v in pairs if a!='Output']
    out=values[0]
    for value in values[1:]:out=native('ConcatenateChainTransform',out,value)
   elif typ=='ConcatenateInverseDilationTransform':
    refs=dict(pairs);right=native('InvertTransform',self.run(refs['Right']));out=native('ConcatenateDilationTransform',self.run(refs['Left']),right)
   elif typ=='TransformTranslationOrientationConnection':
    refs=dict(pairs);value=self.run(refs['Input'])
    out=compose(value[:4],value[4:7],f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
    if 'RotateOffset' in refs:
     from native_pc_head_connections import connect
     if 'TranslateOffset' in refs:raise ValueError('Unverified translation offset connection')
     out=connect(value,rotor(self.rotation(refs['RotateOffset'])),out,True,
       input_transform=get(DN[refs['Input']],'Type')=='Transform',output_transform=True)
   elif typ=='TransformTranslationOrientationScaleConnection':
    refs=dict(pairs)
    if set(refs)!={'Input','Output'}:raise ValueError('Scaled connection offsets are not validated')
    from native_pc_scaled_connection import connect
    initial=compose(f.get('Orientation',[0,0,0,1]),f.get('Translation',[0,0,0]),f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
    out=connect(self.run(refs['Input']),initial)
   elif typ in ('ConcatenateTransformDilation','InvertTransform','ConcatenateChainTransform','ConcatenateDilationTransform','ConcatenateInverseTransformDilation','InvertConcatenateChainTransform'):
    args=[self.run(v) for a,v in pairs if not a.startswith('Output')]
    if len(args)>2:raise ValueError('native fixture supports at most two inputs')
    out=native(typ,args[0],args[1] if len(args)==2 else None)
   else:raise ValueError('unsupported native skin Transform '+typ+' node '+str(i))
  self.cache[i]=out;return out

