import json,struct
from pathlib import Path
from native_pc_output_bridge import replay,GLOBALS
globals_={}
for i in range(0,len(GLOBALS),2):globals_[GLOBALS[i]]=0xffffffff;globals_[GLOBALS[i+1]]=99+i
globals_[0x213e48c]=1;globals_[0x213e6ec]=2;globals_[0x213e3cc]=3
def pack(v):return struct.pack('<'+'f'*len(v),*v)
row=[7,3,4,5,1.5,2,2.5,2,0,0,0,2]
rows=b''.join(struct.pack('<12fI',*row,m)for m in (1,0x18e,0x1fe))
initials=[[0],[0,0,0,1,0,0,0,1],[0,0,0,1,0,0,0,1,1,1,1,1,1,1,1,1]]
nodes=[dict(payload=pack(v),type_word=t,node_stamp=5,metadata_stamp=123)for v,t in zip(initials,(2,1,3))]
r=replay(rows,nodes,globals_)
actual=[list(struct.unpack('<'+'f'*(len(r[i]['payload'])//4),r[i]['payload']))for i in range(3)]
assert actual[0]==[7]
assert actual[1]==[0,0,0,2,3,4,5,2] # direct rotor copy
assert actual[2][:11]==[0,0,0,1,3,4,5,2,1.5,2,2.5] # normalized rotor branch
assert all(x['node_stamp']==123 for x in r.values())
# Mask-zero rows must preserve payloads; scalar stamp should stay untouched.
zero=b''.join(struct.pack('<12fI',*row,0)for _ in nodes);z=replay(zero,nodes,globals_)
assert all(z[i]['payload']==nodes[i]['payload']for i in range(3))and z[0]['node_stamp']==5
report=dict(pass_=True,typed_cases=3,mask_zero_cases=3,scope='Full native52B3C0 with synthetic typed descriptors/predicate globals. Verifies scalar, direct rotor and normalized rotor output branches plus mask preservation; no live bridge parity yet.')
(Path(__file__).parent/'ControllerState/output-bridge-native-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
