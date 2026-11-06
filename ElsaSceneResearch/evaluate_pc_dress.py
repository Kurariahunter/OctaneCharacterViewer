"""PC source dress anchors with native reset-only lower chains, not cloth simulation."""
from evaluate_pc_legs import *
from native_pc_dress_math import aim,inverse_point,inverse_vector,difference

class DressEval(LegEval):
 def run(self,i):
  if i in self.cache:return self.cache[i]
  prod=PROD.get(i)
  if prod is None:return super().run(i)
  p,a=prod;typ=get(p,'Type');refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
  if typ=='DynamicChain':
   if int(p['value'])not in (550,551):raise ValueError('unsupported PC chain')
   from native_pc_chain_reset import make,invoke,positions,u
   import struct
   anchor=self.raw.run(refs['AnchorToWorld']);container=self.raw.run(refs['Container'])
   for value in [anchor,container]:
    if len(value)>8 and (max(abs(value[j]-1)for j in [8,9,10,12,13,14,15])>1e-5 or abs(value[11]-value[7])>1e-5):raise ValueError('nonuniform reset fixture')
   ins,outs=make(anchor[:8],container[:8],side='Left' if int(p['value'])==550 else 'Right')
   constraint=self.run(refs['ConstraintPoint[0]']);u.mem_write(ins[11]+0x34,struct.pack('<3f',*constraint));invoke(0x4acad0)
   for node,value in zip([refs['Position[0]'],refs['Position[1]']],positions(outs)):self.cache[node]=np.array(value)
   root_error=float(np.linalg.norm(self.cache[refs['Position[0]']]-constraint));length=float(np.linalg.norm(self.cache[refs['Position[1]']]-self.cache[refs['Position[0]']]));length_error=abs(length-get(DN[refs['Particle[1]']],'ConstraintLength')*anchor[7])
   if max(root_error,length_error)>1e-5:raise ValueError('chain reset root or length mismatch')
   if not hasattr(self,'dress_checks'):self.dress_checks=[]
   self.dress_checks.append({'processor':int(p['value']),'root_error':root_error,'segment_length_error':length_error})
   return self.cache[i]
  if typ=='Position3dDifferenceProcessor':value=np.array(difference(self.run(refs['To']),self.run(refs['From'])))
  elif typ=='AimConstraintProcessorNode':
   if set(refs)-{'AlignInput','AlignReference','UpInput','UpReference','Output'}:raise ValueError('unsupported aim inputs')
   value=quat(aim(*[self.run(refs[k])for k in ['AlignInput','AlignReference','UpInput','UpReference']]))
  elif typ in ('InverseTransformPositionWithTransform','InverseTransformVectorWithTransform'):
   fn=inverse_point if typ.startswith('InverseTransformPosition')else inverse_vector;value=np.array(fn(self.run(refs['Input']),self.raw.run(refs['Converter'])))
  else:return super().run(i)
  if not np.isfinite(value).all():raise ValueError('nonfinite dress graph')
  self.cache[i]=value;return value
