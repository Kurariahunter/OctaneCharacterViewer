import struct
from evaluate_elsa_head import N,DN,get
idx=get(N,'DefaultDataIndices');data=bytes(get(N,'DefaultData'));used=get(N,'ConnectionMapUsedDataNodes');print(len(idx),len(data),len(used));words=struct.unpack('<'+'H'*(len(idx)//2),bytes(idx))
for slot,w in enumerate(words):
 print(slot,used[slot] if slot<len(used) else None,hex(w),w&4095,(w&4095)*4)
print('FLOATS',struct.unpack('<'+'f'*(len(data)//4),data)[:55])
