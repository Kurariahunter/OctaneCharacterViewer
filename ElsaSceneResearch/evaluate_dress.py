"""Bounded native aim/vector operations for Elsa dress kinematic proxies."""
import numpy as np
from evaluate_elsa_feet import FootEval
from evaluate_native_skin import NativeSkinEval
from evaluate_elsa_head import DN,PROD,get,quat,stored
from native_dress_math import aim,inverse_point,inverse_vector,difference
from native_transform_scale import point
class DressEval(FootEval):
 def __init__(self):super().__init__();self.native=NativeSkinEval(self)
 def run(self,i):
  if i in self.cache:return self.cache[i]
  prod=PROD.get(i)
  if not prod:return super().run(i)
  p,a=prod;typ=get(p,'Type');refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
  if typ=='Position3dDifferenceProcessor':value=np.array(difference(self.run(refs['To']),self.run(refs['From'])))
  elif typ=='AimConstraintProcessorNode':
   if set(refs)-{'AlignInput','AlignReference','UpInput','UpReference','Output'}:raise ValueError('untested optional aim inputs')
   q=aim(self.run(refs['AlignInput']),self.run(refs['AlignReference']),self.run(refs['UpInput']),self.run(refs['UpReference']));value=quat(q)
  elif typ in ('InverseTransformPositionWithTransform','InverseTransformVectorWithTransform'):
   fn=inverse_point if typ.startswith('InverseTransformPosition') else inverse_vector;value=np.array(fn(self.run(refs['Input']),self.native.run(refs['Converter'])))
  elif typ=='TransformComponentProcessorDecompose':
   raw=self.native.run(refs['Aggregate'])
   if a=='Orientation':value=quat(raw[:4])
   elif a=='Translation':value=np.array(raw[4:7])
   elif a=='Scale':value=np.array(raw[8:12])
   else:raise ValueError('untested component '+a)
  else:return super().run(i)
  if not np.isfinite(value).all():raise ValueError('nonfinite dress dependency '+str(i))
  self.cache[i]=value;return value
