from pathlib import Path
import sys,json,math,random
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from native_pc_clip_math import rotation,sha
from wiiu_rotation_math import reverse_euler_zxy
P=Path(__file__).parent;rng=random.Random(20261024)
cases=[[0,0,0],[.3,-.7,1.1],[-1.2,.6,2.4],[math.pi/2,math.pi/3,-math.pi/4]]
for axis in range(3):
 for angle in [-math.pi,-.5,.5,math.pi]:
  a=[0,0,0];a[axis]=angle;cases.append(a)
cases +=[[rng.uniform(-math.pi,math.pi)for _ in range(3)]for _ in range(128)]
rows=[]
for angles in cases:
 q=reverse_euler_zxy(angles);native=rotation(angles);err=max(abs(x-y)for x,y in zip(q,native));norm=abs(sum(x*x for x in q)-1)
 assert err<5e-7,(angles,err);assert norm<1e-12
 rows.append({'angles_radians':angles,'reconstructed_wiiu_formula_xyzw':q,'native_pc_xyzw':native,'max_component_error':err})
# Negative witness: ordinary positive XYZ-order composition cannot pass a noncommuting case.
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b;return[w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
a=[.3,-.7,1.1];qx=[math.sin(a[0]/2),0,0,math.cos(a[0]/2)];qy=[0,math.sin(a[1]/2),0,math.cos(a[1]/2)];qz=[0,0,math.sin(a[2]/2),math.cos(a[2]/2)];wrong=mul(mul(qx,qy),qz);correct=rotation(a);wrong_error=min(max(abs(x-y)for x,y in zip(wrong,correct)),max(abs(x+y)for x,y in zip(wrong,correct)));assert wrong_error>.1
report={'scope':'Reconstructed Wii U scalar formula versus original PC native order2 routine; no execution of Wii U machine code or bit-exact libm claim. Input radians, output xyzw.','pc_exe_sha256':sha,'tests':len(rows),'pass':True,'max_component_error':max(r['max_component_error']for r in rows),'wrong_order_sign_witness_error':wrong_error,'cases':rows}
(P/'rotation-native-crosscheck.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='cases'},indent=2))
# Add derived quaternion interpretation beside the raw Euler control samples.
data=json.loads((P/'elsa-raw-control-samples.json').read_text());count=0
for sample in data['samples']:
 for port in sample['ports'].values():
  for channel in port['channels'].values():
   if 'order_code'in channel:
    assert channel['order_code']==2;channel['derived_quaternion_xyzw']=reverse_euler_zxy(channel['values']);channel['kind']='source Euler operands with reconstructed ReverseEulerZXY quaternion';count+=1

data['scope']='Three source-control samples; static constants, sampled scalar controls and reconstructed ReverseEulerZXY quaternions. Python interior cubic timing is not native-quantized. No downstream graph, IK, world transforms or final skin palette evaluated.'
(P/'elsa-control-quaternions.json').write_text(json.dumps(data,indent=2));print('Derived',count,'typed control quaternions')
