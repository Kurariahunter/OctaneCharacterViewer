"""Explicit retained Transform3d output and fade; no default network or scheduler."""
import math,struct
from native_pc_blend_replay import blend,u,PROC

class TransformStates:
 def __init__(self):self.states={};self.evaluations=0
 @staticmethod
 def validate(values):
  if len(values)!=16 or not all(math.isfinite(v)for v in values):raise ValueError('Finite sixteen-float Transform required')
  if abs(sum(v*v for v in values[:4])-1)>1e-4:raise ValueError('Unit Transform quaternion required')
 def seed(self,key,values,factor=0.,bypass=False):
  self.validate(values)
  if not math.isfinite(factor)or not 0<=factor<=1:raise ValueError('Invalid prior fade')
  self.states[key]=dict(values=list(values),factor=factor,bypass=bool(bypass))
 def update(self,key,target,factor):
  if key not in self.states:raise ValueError('Explicit outgoing Transform seed required')
  self.validate(target)
  if not math.isfinite(factor)or not 0<=factor<=1:raise ValueError('Invalid Transform fade')
  prior=self.states[key]
  value=blend([dict(values=list(target),priority=5.,flag=0,weight=None,factor2c=None,factor30=factor)],transform=True,previous_transform=prior['values'],previous_factor=prior['factor'],bypass_fade=prior['bypass'])
  stored=struct.unpack('<f',u.mem_read(PROC+0x34,4))[0];bypass=bool(struct.unpack('<I',u.mem_read(PROC+0x18,4))[0]&0x80000000)
  self.states[key]=dict(values=value,factor=stored,bypass=bypass);self.evaluations+=1
  return value
