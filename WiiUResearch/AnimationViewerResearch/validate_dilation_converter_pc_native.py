"""Nonidentity forward Dilation converter tests against original PC instructions."""
from pathlib import Path
import sys,json,random
import numpy as np
P=Path(__file__).parent
sys.path.insert(0,str(P.parents[1]/'ElsaSceneResearch'))
from native_pc_dress_math import call
from native_pc_clip_math import rotation
from native_pc_lean_ik import sha

def matrix(v):
 x,y,z,w=v[:4]
 r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
 [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
 [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]).T
 m=np.eye(4);m[:3,:3]=r*v[7];m[:3,3]=v[4:7];return m

rng=random.Random(20261024);identity=[0,0,0,1,0,0,0,1];cases=[]
for i in range(48):
 def value():return rotation([rng.uniform(-2,2)for _ in range(3)])+[rng.uniform(-3,3)for _ in range(3)]+[rng.uniform(.3,2)]
 a,b=value(),value()
 if i==0:a=identity
 if i==1:b=identity
 out=call(0x4d7310,[a,b],'typed',8)
 error=float(np.max(abs(matrix(out)-matrix(b)@matrix(a))))
 wrong=float(np.max(abs(matrix(out)-matrix(a)@matrix(b))))
 assert error<2e-5,(i,error)
 cases.append({'input':a,'converter':b,'output':out,'converter_left_matrix_error':error,'wrong_order_error':wrong})
report={'scope':'Original PC forward typed routine; positive uniform scales, unit rotations and translations. Independent column-matrix comparison. Not Wii U machine-code execution.','pc_exe_sha256':sha,'pc_compute_address':'0x004d7310','wiiu_compute_address':'0x021d3eb0','wiiu_basis_convert_address':'0x021c9b68','wiiu_dilation_add_address':'0x0214b818','case_count':len(cases),'maximum_error':max(c['converter_left_matrix_error']for c in cases),'maximum_wrong_order_witness':max(c['wrong_order_error']for c in cases),'cases':cases}
(P/'dilation-converter-native-crosscheck.json').write_text(json.dumps(report,indent=2))
print('PASS',len(cases),'nonidentity/identity fixtures; max error',report['maximum_error'])
