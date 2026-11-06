"""Controlled full native blend tests for independent source/filter indices and coefficient products."""
import json,math
from pathlib import Path
from native_pc_blend_replay import blend,sha
from probe_pc_blend_order import contributor,qaxis,mul,err
base=mul(qaxis(0,37),qaxis(2,-21));deltas=[mul(qaxis(1,43),qaxis(0,-17)),mul(qaxis(2,-33),qaxis(0,28))];translations=[[.4,-.3,.2],[1.2,.7,-.4]]
filter_values=[0.,.25,1.];rows=[]
for source_index in [0,1]:
 for filter_index in [0,1,2]:
  for factor2c in [.25,.5,1.]:
   delta=contributor(deltas[source_index],1,1,t=translations[source_index]);delta.update(source_values=[contributor(q,1,t=t)['values']for q,t in zip(deltas,translations)],source_index=source_index,filter_values=filter_values,filter_index=filter_index,factor2c=factor2c)
   cs=[contributor(base,0,t=[1.,2.,3.]),delta];out=blend(cs);built=blend(cs,build_entries=True);reversed_built=blend(list(reversed(cs)),build_entries=True)
   if max(abs(a-b)for a,b in zip(out,built))>1e-7 or max(abs(a-b)for a,b in zip(out,reversed_built))>1e-7:raise ValueError('Native builder-to-consumer mismatch')
   weight=filter_values[filter_index]*factor2c
   q=[v*weight for v in deltas[source_index]];q[3]+=1-weight;length=math.sqrt(sum(v*v for v in q));q=[v/length for v in q]
   re=err(out[:4],mul(q,base));te=max(abs(v-(b+d*weight))for v,b,d in zip(out[4:7],[1.,2.,3.],translations[source_index]))
   if re>2e-6 or te>2e-6:raise ValueError(('Indexed filter mismatch',source_index,filter_index,factor2c,re,te))
   rows.append(dict(source_index=source_index,filter_index=filter_index,filter_value=filter_values[filter_index],factor2c=factor2c,effective_weight=weight,rotor_error=re,translation_error=te))
# A missing Filter pointer uses coefficient 1 even when the packed filter index is nonzero.
missing=contributor(deltas[0],1,None,t=translations[0]);missing['filter_index']=127
out=blend([contributor(base,0,t=[1.,2.,3.]),missing]);te=max(abs(v-(b+d))for v,b,d in zip(out[4:7],[1.,2.,3.],translations[0]));assert te<2e-6
report=dict(pass_=True,exe_sha256=sha,entry='0x4e35d0',packed_source_index_bits=[0,11],packed_filter_index_bits=[12,23],filter_pointer='contributor +0x28',filter_payload='Filter +0x10',coefficient_product='selected Filter float times optional scalar node at contributor +0x2c',cases=rows,null_filter_case=dict(packed_filter_index=127,coefficient=1,translation_error=te),max_rotor_error=max(r['rotor_error']for r in rows),max_translation_error=max(r['translation_error']for r in rows),scope='Full native Dilation blend on synthetic source arrays/Filter payloads. One equal-priority unflagged base + one flagged delta, unit scale, factor30=1, no actor/default-network temporal fade. This proves table index extraction and selected coefficients in this fixture, not final authored index mapping or general composition parity.')
report['native_builder_to_consumer']={'entry_builder':'0x5440c0','consumer':'0x4e35d0','cases':len(rows),'reversed_input_sorted_cases':len(rows),'max_allowed_difference':1e-7};report['pass']=report.pop('pass_');Path(__file__).with_name('pc-indexed-filter-blend-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='cases'},indent=2))
