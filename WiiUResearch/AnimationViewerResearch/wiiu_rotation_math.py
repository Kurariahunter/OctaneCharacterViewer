"""Scalar formula reconstructed from Wii U Types::ReverseEulerZXY::AsRotor.
Not bit-exact PowerPC arithmetic; no coordinate-system conversion implied.
"""
import math,struct

def reverse_euler_zxy(angles):
 if len(angles)!=3 or not all(math.isfinite(x)for x in angles):raise ValueError('Three finite radians required')
 # Authored angles are float32; ordinary Python trig models, not emulates, libm/FMA.
 a=[struct.unpack('<f',struct.pack('<f',x))[0]for x in angles]
 sx,sy,sz=[math.sin(x*.5)for x in a];cx,cy,cz=[math.cos(x*.5)for x in a]
 return [-(sx*cy*cz+cx*sy*sz),-(cx*sy*cz-sx*cy*sz),-(cx*cy*sz-sx*sy*cz),cx*cy*cz+sx*sy*sz]
