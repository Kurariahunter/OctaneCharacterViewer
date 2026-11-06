from pathlib import Path
import json
from native_pc_clip_buffer_blend import apply_layer
from validate_pc_source_mode_dispatch import native_case
from probe_pc_blend_order import qaxis,mul
b=mul(qaxis(0,37),qaxis(2,-21));d=mul(qaxis(1,43),qaxis(0,-17));rows=[]
for mode in (0,1):
 for w in (0.,.25,.5,1.):
  want=native_case(mode,w,b,d);got=apply_layer(dict(Translation=[1,2,3],Scale=[2,3,4,1],Orientation=b),dict(Translation=[.4,-.3,.2],Scale=[1.2,.8,1.5,1],Orientation=d),0x177,w,bool(mode))
  error=max(abs(x-y)for k,z in [('Translation','translation'),('Orientation','rotor')]for x,y in zip(got[k],want[z]));error=max(error,max(abs(x-y)for x,y in zip(got['Scale'][:3],want['scale'])));assert error==0;rows.append(dict(mode=mode,weight=w,error=error))
# A rotation-only layer must leave translation and nonuniform scale untouched.
base=dict(Translation=[1,2,3],Scale=[2,3,4,1],Orientation=b);out=apply_layer(base,dict(Orientation=d),0x100)
assert out['Translation']==base['Translation']and out['Scale']==base['Scale']
report=dict(cases=len(rows),max_error=max(x['error']for x in rows),rotation_only_preserves_translation_scale=True,rows=rows)
Path(__file__).with_name('pc-clip-buffer-adapter-validation.json').write_text(json.dumps(report,indent=2));print(report)
