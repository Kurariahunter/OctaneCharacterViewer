"""Native full frame dispatch versus staged DynamicChain reset/step fixture."""
import json,struct,math
from pathlib import Path
import numpy as np
from native_dynamic_chain_fixture import *
from evaluate_elsa_head import quat
F32=lambda x:struct.unpack('<I',struct.pack('<f',x))[0]
ins,outs=make(orientation=[0,0,0,1]);initial=bytes(u.mem_read(BASE,0x20000));runs=[]
for mode in ['full','staged']:
 u.mem_write(BASE,initial);u.mem_write(ins[2]+0x34,struct.pack('<I',0xfffffffe));frames=[]
 for frame in range(120):
  t=frame/30;anchor=[0,0,0,1,.03*math.sin(t*2),0,0,1];container=anchor.copy();container[6]=.3010336757
  u.mem_write(ins[0]+0x34,struct.pack('<I',frame));u.mem_write(ins[1]+0x34,struct.pack('<f',1/30));u.mem_write(ins[5]+0x34,struct.pack('<8f',*anchor));u.mem_write(ins[6]+0x34,struct.pack('<8f',*container));u.mem_write(ins[11]+0x34,struct.pack('<3f',anchor[4],0,.01))
  if mode=='full':invoke(0x4ae360)
  else:invoke(0x4acad0 if frame==0 else 0x4acdb0,[] if frame==0 else [F32(1/30)])
  actual=np.array(positions(outs));assert np.isfinite(actual).all();frames.append(actual.tolist())
 runs.append(frames)
err=float(np.max(abs(np.array(runs[0])-runs[1])));root=max(float(np.linalg.norm(np.array(f[0])-[.03*math.sin(j/30*2),0,.01])) for j,f in enumerate(runs[0]));length=max(abs(float(np.linalg.norm(np.array(f[1])-f[0]))-.37) for f in runs[0]);lag=max(abs(f[1][0]-f[0][0]) for f in runs[0]);assert err<1e-7 and root<1e-7 and length<1e-5,(err,root,length)
report={'exe_sha256':sha,'scope':'120-frame moving-anchor fixture, two source-like particles, explicit identity cached orientation, zero external force, source container extent. Full native dispatch versus native staged helpers. Cached orientation feedback and actual original loader remain separate checks.','frames':120,'max_full_vs_staged_position_error':err,'max_root_constraint_error':root,'max_chain_length_error':length,'max_tip_lag':lag,'cached_reference_literal':'^.Orientation','correction':'Earlier capsule-parent interpretation was incorrect: processor+34 caches a reference to an orientation data node. Capsule constraints are separately at+3c/+3e.','frames_full':runs[0]}
Path('dynamic-chain-step-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='frames_full'})
