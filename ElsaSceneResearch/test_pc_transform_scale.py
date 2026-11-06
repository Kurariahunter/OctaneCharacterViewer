from native_pc_transform_scale import *
import random
from evaluate_pc_arms import quat,rotor
if True:
 rng=random.Random(20261015);errors=[]
 for j in range(100):
  states=[]
  for k in range(2):
   q=np.array([rng.uniform(-1,1) for _ in range(4)]);q/=np.linalg.norm(q);t=[rng.uniform(-1,1) for _ in range(3)];s=[rng.uniform(.8,1.2) for _ in range(4)];us=[rng.uniform(.8,1.2) for _ in range(4)];raw=compose(q,t,s,us);expected=payload(q,t,s,us);err=max(abs(x-y) for x,y in zip(raw,expected));assert err<1e-6;states.append(raw)
   v=np.array([rng.uniform(-1,1) for _ in range(3)]);want=(np.array(t)+quat(q)@(v*np.array(s[:3])*s[3]))*np.array(us[:3]);err2=float(np.max(abs(point(raw,v)-want)));assert err2<2e-6,(j,k,err2,raw,v.tolist(),want.tolist(),point(raw,v).tolist());errors.append({'compose':err,'point':err2})
  c,p=states;out=concat(c,p);r=quat(p[:4])@quat(c[:4]);t=np.array(p[4:7])+quat(p[:4])@(np.array(c[4:7])*np.array(c[12:15])*c[15]*p[7]);expected=payload(rotor(r),t,c[8:12],[1]*4);expected[7]=c[7]*p[7];err=float(np.max(abs(np.r_[quat(out[:4]).flatten()-r.flatten(),np.array(out[4:])-np.array(expected[4:])])));assert err<3e-6;errors[-1]['concat']=err
 report={'exe_sha256':sha,'cases':{'component_compose':200,'point_transform':200,'concatenate':100},'max_error':max(max(v.values()) for v in errors),'scope':'Positive Scale/Unscale/uniform factors 0.8..1.2 with mixed-axis rotors. Original helpers executed. This does not establish which Unscale values a complete skin hierarchy assigns.','compose_execute':'0x5303e0','point_helper':'0x4c4350','concat_helper':'0x4c2d50','payload':'quaternion[4],translation[3],uniform,Scale[4],Unscale[4]; native compose copies Scale.w to uniform and forces Unscale.w=1','rows':errors}
 (ROOT/'pc-transform-scale-native-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='rows'})
