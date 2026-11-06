"""Explicit state transition using file EaseDuration and original native math.

No branch/event scheduler, actor selection or automatic scalar binding.
"""
import math,struct
from native_node_duration import select
from native_transition_processor import activate,resolve_duration,step

def f(value):return struct.unpack('<f',struct.pack('<f',value))[0]

class ExplicitStateTransition:
 def __init__(self,units,clock=0.,*,header=None,configuration_units=-1,curve_parameter=1.,clock_offset=0.,override=None,flags=0):
  self.duration=select(float(units),override,flags)
  if header is None:
   h=bytearray(96);struct.pack_into('<HBB',h,0x18,0x58,1,1);struct.pack_into('<f',h,0x50,1.);header=bytes(h)
  self.clock=f(clock);self.output=0.
  configured=f(f(configuration_units)*f(1/30))
  self.header=activate(header,self.clock,duration=configured,curve_parameter=curve_parameter,clock_offset=clock_offset)
  self.header=resolve_duration(self.header,self.duration)
  self.stored_duration=struct.unpack_from('<f',self.header,0x24)[0]
 def update(self,clock):
  clock=f(clock)
  if not math.isfinite(clock)or clock<self.clock:raise ValueError('Finite nondecreasing explicit clock required')
  self.output,self.header=step(self.header,clock,self.output);self.clock=clock
  return self.output
