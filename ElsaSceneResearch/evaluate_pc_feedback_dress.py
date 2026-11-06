"""Use prior computed local Aim output, matching the captured closed-loop test."""
from evaluate_pc_temporal_dress import *


class FeedbackDressEval(TemporalDressEval):
 def run(self,i):
  if i in self.cache:return self.cache[i]
  if i not in (689,705):return super().run(i)
  p,attr=PROD[i]
  if get(p,'Type')!='AimConstraintProcessorNode':raise ValueError('unexpected dress Aim producer')
  refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
  if set(refs)!={'AlignInput','AlignReference','UpInput','UpReference','Output'}:raise ValueError('unexpected Aim inputs')
  args=[self.run(refs[k])for k in ('AlignInput','AlignReference','UpInput','UpReference')]
  pid=550 if i==689 else 551
  # Resolving AlignInput advances this chain before accessing its prior output.
  prior=self.states.states[pid]['q'][:]
  q=aim(*args,initial=prior)
  value=quat(q);self.cache[i]=value;self.states.feedback(pid,q)
  return value
