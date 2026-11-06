"""Bounded installed-PC hips/leg graph. Experimental; rejects unknown paths."""
import hashlib
from evaluate_pc_arms import *
from native_pc_dress_math import call
from native_pc_relationship import run as relationship
from native_pc_lean_ik import solve

for p in allnodes(N,'ProcessorNode'):
 if get(p,'Type')=='IkLean2LinkProcessor':
  for a,v in zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')):
   if a in ('StartOrientation','MidOrientation','Scale'):PROD[v]=(p,a)

def dilation(m):
 scales=np.linalg.norm(m[:3,:3],axis=0)
 if min(scales)<1e-8 or max(abs(scales-scales[0]))>1e-5:raise ValueError('nonuniform dilation')
 return rotor(m[:3,:3]/scales[0])+m[:3,3].tolist()+[float(scales[0])]

class LegEval(Eval):
 def __init__(self):
  super().__init__();self.extra_busy=set();self.solvers={}
  from evaluate_pc_raw_transform import NativeSkinEval
  self.raw=NativeSkinEval(self)
 def run(self,i):
  if i in self.cache:return self.cache[i]
  if get(DN[i],'Type')=='Transform':
   from evaluate_pc_raw_transform import affine
   self.visited.add(i);self.cache[i]=affine(self.raw.run(i));return self.cache[i]
  prod=PROD.get(i)
  if prod is None:return super().run(i)
  p,output=prod;typ=get(p,'Type');pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
  if typ=='RotorToEulerZXYVariantProcessor':
   from native_pc_forearm_twist import euler
   m=np.array(euler(rotor(self.run(dict(pairs)['Input']))));self.cache[i]=m;return m
  if typ=='EulerZXYComponentProcessorDecompose':
   m=np.array(self.run(dict(pairs)['Aggregate'])['XYZ'.index(output)]);self.cache[i]=m;return m
  if typ=='FloatMultiply':
   values=[[float(self.run(v))] for a,v in pairs if a.startswith('Input[')]
   if len(values)!=2:raise ValueError('unverified FloatMultiply arity')
   m=np.array(call(0x52d540,values,'array',1)[0]);self.cache[i]=m;return m
  if typ=='TransformComponentProcessorDecompose':
   raw=self.raw.run(dict(pairs)['Aggregate']);m=quat(raw[:4]) if output=='Orientation' else np.array(raw[4:7] if output=='Translation' else raw[8:12]);self.cache[i]=m;return m
  supported={'RelationshipProcessor','IkLean2LinkProcessor','ShrinkingVolumeScaleZ','ScaleConnection','FloatNegate','TransformComponentProcessorCompose','TransformDilationWithTransform','TransformPositionWithDilation','InvertConcatenateChainTransform','InvertConcatenateChainDilation','Position3dOffsetProcessor','ConcatenateInverseTransformDilation','DilationTranslationOrientationConnection','DilationOrientationConnection'}
  supported.add('TransformVectorWithDilation')
  if typ not in supported:return super().run(i)
  if i in self.extra_busy:raise ValueError('PC leg graph cycle '+str(i))
  self.extra_busy.add(i);self.visited.add(i)
  try:
   refs=dict(pairs)
   if typ=='RelationshipProcessor':
    known={16:'8093efdf1d301e42983bd039ff3ec265f5a5ca975db9f6f38894833c0ce5f4b5',19:'7018f68db2c0966e922208c29f7764bbf8f4b7700fcf7a1370dbd041bb36033b',28:'d3b281b38bf0e06231ee69d032814b3b3887b39bd76d39e9c99ce3f2015e7f6b'}
    blob=bytes.fromhex(get(DN[refs['RelationshipData']],'RelationshipDataBlock')['hex'])
    known[177]='7ad4d7ac5ad56a235376973be6fd8849ac5e68d27d1ece72d96d04a1f25216b3'
    if hashlib.sha256(blob).hexdigest()!=known.get(int(p['value'])):raise ValueError('unvalidated PC relationship')
    values=[float(self.run(v))for a,v in pairs if a.startswith('Input[')]
    if any(abs(v)>100 for v in values):raise ValueError('relationship input bounds')
    outs=[v for a,v in pairs if a.startswith('Output[')]
    for node,raw in zip(outs,relationship(blob,values,len(outs))):
     m=np.eye(4);m[:3,:3]=quat(raw[:4])*raw[7];m[:3,3]=raw[4:7];self.cache[node]=m
   elif typ=='IkLean2LinkProcessor':
    if int(p['value'])not in (405,411):raise ValueError('unvalidated PC IK')
    # PC factory leaves its optional rotor slot null for this Vector-typed Axis.
    if get(DN[refs['Axis']],'Type')!='Vector' or max(abs(self.run(refs['Axis'])-np.array([1,0,0])))>1e-6:raise ValueError('different PC axis configuration')
    vals=[self.run(refs[a]).tolist() for a in ['StartPosition','MidPosition','EndPosition','Target','PoleVector']]+[None,[float(self.run(refs['Twist']))],[1.]]
    raw=solve(vals);self.solvers[int(p['value'])]={'inputs':vals,'outputs':[list(v)for v in raw]}
    for a,value in zip(['StartOrientation','MidOrientation','Scale'],raw):self.cache[refs[a]]=quat(value)if a!='Scale'else np.array(value[0])
   else:
    args={a:self.run(v)for a,v in pairs if a not in ('Output','Aggregate')}
    if typ=='TransformComponentProcessorCompose':
     m=stored(DN[i]).copy()
     if 'Orientation'in args:m[:3,:3]=args['Orientation']
     if 'Translation'in args:m[:3,3]=args['Translation']
     if 'Scale'in args:m[:3,:3]*=np.array(args['Scale'])[:3]
    elif typ=='ShrinkingVolumeScaleZ':m=np.array(call(0x4c8b40,[[float(args['Input'])]],'typed',4))
    elif typ=='ScaleConnection':m=args['Input'].copy()
    elif typ=='FloatNegate':m=-args['Input']
    elif typ=='Position3dOffsetProcessor':m=args['Input']+args['Offset']
    elif typ=='TransformPositionWithDilation':m=(args['Converter']@np.r_[args['Input'],1])[:3]
    elif typ=='TransformVectorWithDilation':
     from native_pc_eye_vector import transform
     if get(DN[refs['Input']],'Type')!='Vector' or get(DN[refs['Converter']],'Type')!='Dilation':raise ValueError('unverified eye vector input types')
     m=np.array(transform(args['Input'],dilation(args['Converter'])))
    elif typ=='TransformDilationWithTransform':
     from native_pc_skin_matrix import dilation_matrix as packed_dilation
     raw=self.raw.run(i);packed=packed_dilation(raw);m=np.eye(4)
     m[:3,:3]=np.array(packed[:9]).reshape(3,3).T;m[:3,3]=packed[9:]
    elif typ=='ConcatenateInverseTransformDilation':m=np.linalg.inv(args['Right'])@args['Left']
    elif typ in ('DilationTranslationOrientationConnection','DilationOrientationConnection'):
     from native_pc_head_connections import connect
     transform=get(DN[refs['Input']],'Type')=='Transform'
     if transform:
      input_raw=self.raw.run(refs['Input'])
     else:input_raw=dilation(args['Input'])
     raw=connect(input_raw,rotor(args.get('RotateOffset',np.eye(3))),dilation(stored(DN[i])),typ=='DilationTranslationOrientationConnection',input_transform=transform)
     m=np.eye(4);m[:3,:3]=quat(raw[:4])*raw[7];m[:3,3]=raw[4:7]
    else:
     m=np.eye(4)
     for a,v in pairs:
      if a!='Output':m=m@np.linalg.inv(args[a])
    if not np.all(np.isfinite(m)):raise ValueError('nonfinite PC leg graph')
    self.cache[i]=m
   return self.cache[i]
  finally:self.extra_busy.remove(i)

if __name__=='__main__':
 for i in [384,402,407,416,425,631,430,435,444,453,628]:
  e=LegEval()
  try:print(i,e.run(i).tolist(),e.solvers)
  except Exception as ex:print('FAIL',i,str(ex))
