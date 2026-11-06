"""Native PC rotor-to-Euler variant used by the forearm overlay path."""
import math
from native_pc_dress_math import call
def euler(q):
 if len(q)!=4 or not all(math.isfinite(v) for v in q) or abs(sum(v*v for v in q)-1)>1e-4:raise ValueError('unit rotor required')
 return call(0x4df750,[list(q)],'typed',3)
