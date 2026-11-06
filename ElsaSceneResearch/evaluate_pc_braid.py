"""Experimental source braid path. Native chain, source constraints and local Aim feedback."""
from evaluate_pc_feedback_dress import *
from native_pc_transform_scale import point
class BraidEval(FeedbackDressEval):
 def run(self,i):
  if i in self.cache:return self.cache[i]
  prod=PROD.get(i)
  if prod and get(prod[0],'Type')=='TransformPositionWithTransform':
   refs=dict(zip(get(prod[0],'DataNodeAttributes'),get(prod[0],'DataNodeRefs')))
   value=np.array(point(self.raw.run(refs['Converter']),self.run(refs['Input'])));self.cache[i]=value;return value
  if i==671:
   refs=dict(zip(get(prod[0],'DataNodeAttributes'),get(prod[0],'DataNodeRefs')))
   args=[self.run(refs[k])for k in ('AlignInput','AlignReference','UpInput','UpReference')]
   prior=self.states.states[548]['q'][:]
   q=aim(*args,initial=prior);self.cache[i]=quat(q);self.states.feedback(548,q);return self.cache[i]
  return super().run(i)
