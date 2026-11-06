"""Native Transform payload propagation on explicit Elsa skin-output paths.
Dilation/control dependencies remain in the bounded FootEval; no loader claim.
"""
import json
import numpy as np
from pathlib import Path
from evaluate_elsa_head import DN,PROD,get,quat,stored
from evaluate_elsa_feet import FootEval,rotor
from native_transform_scale import compose,point
from validate_foot_basis_native import native,SPECS
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
 def __init__(self,e=None):self.e=e or FootEval();self.cache={};self.visited=set()
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
   out=compose(f.get('Orientation',[0,0,0,1]),f.get('Translation',[0,0,0]),f.get('Scale',[1]*4),f.get('Unscale',[1]*4))
  else:
   p,attr=pout;typ=get(p,'Type');pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
   if typ=='TransformComponentProcessorCompose':
    inputs={a:(self.rotation(v) if a=='Orientation' else self.e.run(v)) for a,v in pairs if a!='Aggregate'}
    out=compose(rotor(inputs['Orientation']) if 'Orientation' in inputs else f.get('Orientation',[0,0,0,1]),inputs.get('Translation',f.get('Translation',[0,0,0])),inputs.get('Scale',f.get('Scale',[1]*4)),inputs.get('Unscale',f.get('Unscale',[1]*4)))
   elif typ in ('ConcatenateTransformDilation','InvertTransform','ConcatenateChainTransform','ConcatenateDilationTransform','ConcatenateInverseTransformDilation','InvertConcatenateChainTransform'):
    args=[self.run(v) for a,v in pairs if not a.startswith('Output')]
    if len(args)>2:raise ValueError('native fixture supports at most two inputs')
    out=native(typ,args[0],args[1] if len(args)==2 else None)
   else:raise ValueError('unsupported native skin Transform '+typ+' node '+str(i))
  self.cache[i]=out;return out

if __name__=='__main__':
 rows=[]
 for i in [424,430,426,433,19,432,441,453,459,461,470,419]:
  n=NativeSkinEval();raw=n.run(i);m=affine(raw);old=n.e.run(i)
  rows.append({'node':i,'raw':raw,'native_affine':m.tolist(),'flattened_difference':float(np.max(abs(m-old))),'visited':sorted(n.visited)})
 Path('native-skin-default-validation.json').write_text(json.dumps(rows,indent=2));print([(r['node'],r['flattened_difference']) for r in rows])
