"""Per-processor Float state for the verified single unflagged source case.

The caller owns activation/clock/factor production. No automatic game scheduler
or empirical pose correction is supplied here.
"""
import math,struct
from native_pc_blend_replay import blend,u,PROC

class ScalarStates:
 def __init__(self):self.states={};self.evaluations=0
 def seed(self,key,output=0.,factor=0.,bypass=False):
  # Constructor533747 clears bypass/fade. Output0 is an explicit fixture;
  # this is not a policy to reset existing states on clip changes.
  if not all(math.isfinite(v)for v in (output,factor))or not 0<=factor<=1:raise ValueError('Invalid prior scalar state')
  self.states[key]=dict(output=output,factor=factor,bypass=bypass)
 def update(self,key,target,factor=1.):
  if not math.isfinite(target)or not math.isfinite(factor)or not 0<=factor<=1:raise ValueError('Invalid scalar input/fade')
  if key not in self.states:self.seed(key)
  prior=dict(self.states[key])
  value=blend([dict(values=[target]+[0.]*15,priority=5.,flag=0,weight=None,factor2c=None,factor30=factor)],scalar=True,previous_output=prior['output'],previous_factor=prior['factor'],bypass_fade=prior['bypass'])[0]
  stored=struct.unpack('<f',u.mem_read(PROC+0x34,4))[0]
  bypass=bool(struct.unpack('<I',u.mem_read(PROC+0x18,4))[0]&0x80000000)
  self.states[key]=dict(output=value,factor=stored,bypass=bypass);self.evaluations+=1
  return value
