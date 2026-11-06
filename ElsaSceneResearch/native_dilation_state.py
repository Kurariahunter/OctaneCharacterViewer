"""Retained native Dilation output; single unflagged contributor, no defaults/filter."""
import math,struct
from native_pc_blend_replay import blend,u,PROC

class DilationStates:
 def __init__(self):self.states={};self.evaluations=0
 def seed(self,key,values,bypass=False):
  if len(values)!=8 or not all(math.isfinite(v)for v in values):raise ValueError('Finite Dilation required')
  if abs(sum(v*v for v in values[:4])-1)>1e-4:raise ValueError('Unit quaternion required')
  self.states[key]=dict(values=list(values),bypass=bool(bypass))
 def update(self,key,target,factor):
  if key not in self.states:raise ValueError('Explicit outgoing Dilation seed required')
  if len(target)!=8 or not all(math.isfinite(v)for v in target)or not math.isfinite(factor)or not 0<=factor<=1:raise ValueError('Invalid Dilation target/factor')
  if abs(sum(v*v for v in target[:4])-1)>1e-4:raise ValueError('Unit target quaternion required')
  prior=self.states[key]
  value=blend([dict(values=list(target)+[0.]*8,priority=5.,flag=0,weight=None,factor2c=None,factor30=factor)],previous_dilation=prior['values'],bypass_fade=prior['bypass'])
  bypass=bool(struct.unpack('<I',u.mem_read(PROC+0x18,4))[0]&0x80000000)
  self.states[key]=dict(values=value,bypass=bypass);self.evaluations+=1
  return value
