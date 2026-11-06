"""Original PC TransformVectorWithDilation, explicit Vector/Dilation fixture."""
import math,struct
from native_pc_dress_math import call,u
def transform(vector,converter):
 if len(vector)!=3 or len(converter)!=8 or not all(math.isfinite(v) for v in list(vector)+list(converter)):raise ValueError('finite Vector and Dilation required')
 if abs(sum(v*v for v in converter[:4])-1)>1e-4:raise ValueError('unit Dilation rotor required')
 # Vector RTTI predicates; call() also selects the explicit Dilation fixture.
 for address in (0x21aedd0,0x21aedd4):u.mem_write(address,struct.pack('<I',0))
 return call(0x4d3a50,[list(vector),list(converter)],'typed',3)
