"""Original PC packed affine conversion versus native point transforms."""
from pathlib import Path
import sys,json,struct,random
import numpy as np
P=Path(__file__).parent;sys.path.insert(0,str(P.parents[1]/'ElsaSceneResearch'))
from native_pc_transform_scale import execute,u,compose,point
from native_pc_clip_math import rotation
from native_pc_lean_ik import sha
import exe_reader

def convert(v):
 source=0x10008200;output=0x10008000
 u.mem_write(source,struct.pack('<8f',*v));u.mem_write(output,b'\0'*64)
 execute(0x48d9e0,[source],this=output)
 packed=list(struct.unpack('<12f',u.mem_read(output,48)))
 m=np.eye(4);m[:3,:]=np.array(packed).reshape(4,3).T
 return packed,m

def point_matrix(v):
 tr=compose(v[:4],v[4:7],[v[7]]*3+[1],[1]*4)
 origin=point(tr,[0,0,0]);m=np.eye(4);m[:3,3]=origin
 for col in range(3):
  axis=[0,0,0];axis[col]=1;m[:3,col]=point(tr,axis)-origin
 return m

if __name__=='__main__':
 rng=random.Random(20261024);cases=[]
 for i in range(48):
  v=rotation([rng.uniform(-2,2)for _ in range(3)])+[rng.uniform(-3,3)for _ in range(3)]+[rng.uniform(.3,2)]
  packed,m=convert(v);expected=point_matrix(v);error=float(np.max(abs(m-expected)))
  assert error<2e-6
  cases.append({'kind':'generated','input':v,'packed_affine':packed,'maximum_error':error})
 fixture=json.loads((P/'wiiu-head-eyelid-world-fixture.json').read_text())
 for frame in fixture['samples']:
  for eye in frame['eyelids']:
   packed,m=convert(eye['world_dilation']);error=float(np.max(abs(m-np.array(eye['world_matrix_column_convention']))))
   assert error<2e-6
   cases.append({'kind':'eyelid','time':frame['time'],'bone':eye['bone'],'packed_affine':packed,'column_matrix':m.tolist(),'maximum_error':error})
 report={'scope':'Original PC Dilation conversion, traced from registry factory to constructor vtable Compute. Compared with original PC Transform compose/point helpers. Wii U numerical execution and rendered parity remain unverified.','pc_exe_sha256':sha,'factory':'0x004f7da0','constructor':'0x004dedb0','vtable':'0x01b2f544','compute':'0x004dee10','conversion':'0x0048d9e0','layout':'12 floats: three 3-component basis vectors, then translation; column matrix = reshape(4,3).T plus homogeneous row','case_count':len(cases),'maximum_error':max(c['maximum_error']for c in cases),'cases':cases}
 (P/'dilation-matrix-native-crosscheck.json').write_text(json.dumps(report,indent=2))
 for address,size in [(0x4f7da0,0x1f0),(0x4dedb0,0x2c),(0x4dee10,0xb3),(0x48d9e0,0x300)]:
  (P/f'pc-{address:08x}.txt').write_text(exe_reader.disasm(address,size))
 print('PASS',len(cases),'native conversion comparisons; max error',report['maximum_error'])
