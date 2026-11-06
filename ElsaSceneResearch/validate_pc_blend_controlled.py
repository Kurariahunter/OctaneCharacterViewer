"""Controlled native blend-order experiments; unit scale, equal priority, full replacement."""
import math,json
from pathlib import Path
from native_pc_blend_replay import blend,sha
from probe_pc_blend_order import qaxis,mul,err,contributor
R=Path(__file__).parent
bases=[mul(qaxis(0,37),qaxis(2,-21)),mul(qaxis(1,-54),qaxis(0,12)),mul(qaxis(2,62),qaxis(1,25))]
deltas=[mul(qaxis(1,43),qaxis(0,-17)),mul(qaxis(2,-33),qaxis(0,28)),mul(qaxis(0,51),qaxis(1,-29))]
rows=[];reverse=[];negative=[]
for bi,b in enumerate(bases):
 for di,d in enumerate(deltas):
  for w in [0.,.25,.5,1.]:
   cs=[contributor(b,0,t=[1.,2.,3.]),contributor(d,1,w,t=[.4,-.3,.2])];out=blend(cs)
   q=[v*w for v in d];q[3]+=1-w;n=math.sqrt(sum(v*v for v in q));q=[v/n for v in q]
   good=err(out[:4],mul(q,b));wrong=err(out[:4],mul(b,q));terr=max(abs(a-z)for a,z in zip(out[4:7],[1+.4*w,2-.3*w,3+.2*w]))
   assert good<2e-6 and terr<2e-6 and abs(out[7]-1)<2e-6
   rows.append(dict(base=bi,delta=di,weight=w,rotor_error=good,reversed_multiplication_error=wrong,translation_error=terr,observed=out))
   rev=blend(list(reversed(cs)));reverse.append(dict(base=bi,delta=di,weight=w,output_difference=err(rev[:4],out[:4]),translation_difference=max(abs(a-z)for a,z in zip(rev[4:7],out[4:7])),observed=rev,rotor_difference_from_base=err(rev[:4],b)))
   neg=blend([cs[0],contributor([-v for v in d],1,w,t=[.4,-.3,.2])]);negative.append(dict(base=bi,delta=di,weight=w,orientation_difference=err(neg[:4],out[:4])))
summary=dict(exe_sha256=sha,controlled_cases=len(rows),max_rotor_error=max(r['rotor_error']for r in rows),max_translation_error=max(r['translation_error']for r in rows),wrong_order_max_error=max(r['reversed_multiplication_error']for r in rows),reverse_table_order_max_error=max(r['output_difference']for r in reverse),negative_delta_quaternion_max_difference=max(r['orientation_difference']for r in negative),scope='One unflagged base + one flagged delta, same priority5, unit scale, weights0/.25/.5/1, factor2c=1 and factor30=1, no default-network pose or temporal fade. Delta w positive in primary formula checks. Quaternion product defined by explicit Hamilton xyzw math; source matrix convention differs from Unity. Extra diagnostics do not extend proof to multiple flagged layers or arbitrary priorities.')
(R/'pc-native-blend-controlled-validation.json').write_text(json.dumps(dict(summary=summary,rows=rows,reverse_table_order=reverse,negative_delta_quaternion=negative),indent=2));print('SUMMARY',json.dumps(summary,indent=2))

