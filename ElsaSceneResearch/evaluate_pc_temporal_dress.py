"""PC dress graph with persistent native chain state supplied by the caller."""
from evaluate_pc_dress import *

class TemporalDressEval(DressEval):
 def __init__(self,states,frame,dt):
  super().__init__();self.states=states;self.frame=frame;self.dt=dt;self.dress_checks=[]
 def run(self,i):
  if i in self.cache:return self.cache[i]
  prod=PROD.get(i)
  if prod and get(prod[0],'Type')=='DynamicChain':
   p,a=prod;pid=int(p['value']);refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
   values,check=self.states.step(pid,self.frame,self.dt,self.raw.run(refs['AnchorToWorld']),self.raw.run(refs['Container']),self.run(refs['ConstraintPoint[0]']))
   for node,value in zip([refs['Position[0]'],refs['Position[1]']],values):self.cache[node]=value
   self.dress_checks.append(check);return self.cache[i]
  value=super().run(i)
  if i in (689,705):self.states.feedback(550 if i==689 else 551,rotor(value))
  return value
