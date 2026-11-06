"""Conservative PC CICD encoder. Fixed segmentation; unsupported channels preserved."""
import struct,math
from .octane_scene import Scene
from .layout import inspect

def read(raw):
 scene=Scene.from_bytes(raw); nodes=list(scene.root.iter('ClipDataBlock'))
 if len(nodes)!=1:raise ValueError('Exactly one ClipDataBlock required')
 node=nodes[0]; blob=bytes(node.value)
 layout=inspect(blob,[],allowed_boundary_flags=(0,2,16,18,64),endian='<',allow_constant=True)
 channels=[]
 for row in layout['curves']:
  # Only ordinary hold-boundary CICD channels are editable in this version.
  if row['flags']!=0 or row['continuity_warnings']:continue
  at=row['offset']; dims=row['dimensions']; count=row['segments']; meta=at+12
  knots=struct.unpack_from('<'+'H'*count,blob,meta+16*dims)
  times=[row['range'][0]+k/65535*(row['range'][1]-row['range'][0]) for k in knots]+[row['range'][1]]
  coeff=meta+16*dims+2*count
  for d in range(dims):
   _,_,bias,scale=struct.unpack_from('<4f',blob,meta+16*d)
   segments=[]
   for k in range(count):
    q=struct.unpack_from('<4h',blob,coeff+8*(k*dims+d)); values=[bias+q[0]*scale]
    for delta in q[1:]:values.append(values[-1]+delta*scale)
    segments.append(values)
   channels.append({'id':f'curve_{row["index"]:03}_dim_{d:03}','curve':row['index'],'dimension':d,'times':times,'controls':segments})
 return scene,node,blob,layout,channels

def encode(raw,edited):
 scene,node,blob,layout,channels=read(raw); out=bytearray(blob); changed=[]; errors=[]
 byid={c['id']:c for c in channels}
 if set(edited)-set(byid):raise ValueError('Unknown or unsupported channel')
 for name,controls in edited.items():
  c=byid[name]; source=c['controls']; row=layout['curves'][c['curve']]; dims=row['dimensions']; d=c['dimension']
  if len(controls)!=len(source) or any(len(v)!=4 for v in controls):raise ValueError('Fixed segment count required')
  if any(not math.isfinite(v) for seg in controls for v in seg):raise ValueError('Nonfinite edited values')
  if max(abs(a-b) for x,y in zip(source,controls) for a,b in zip(x,y))<1e-10:continue
  for a,b in zip(controls,controls[1:]):
   if abs(a[3]-b[0])>1e-5:raise ValueError('Discontinuous edit unsupported')
  firsts=[v[0] for v in controls]; bias=(max(firsts)+min(firsts))/2
  deltas=[v[i]-v[i-1] for v in controls for i in range(1,4)]
  scale=max(max(abs(v-bias) for v in firsts)/32000,max(abs(v) for v in deltas)/32000,1e-12)
  # Quantize bias and scale first, then accumulate integer controls to limit drift.
  bias,scale=struct.unpack('<2f',struct.pack('<2f',bias,scale))
  meta=row['offset']+12+16*d; struct.pack_into('<4f',out,meta,controls[0][0],controls[-1][-1],bias,scale)
  base=row['offset']+12+16*dims+2*row['segments']; maximum=0
  for k,values in enumerate(controls):
   absolute=[round((v-bias)/scale) for v in values]; q=[absolute[0]]+[b-a for a,b in zip(absolute,absolute[1:])]
   if any(not -32768<=v<=32767 for v in q):raise ValueError('Quantization overflow')
   struct.pack_into('<4h',out,base+8*(k*dims+d),*q)
   maximum=max(maximum,max(abs(bias+a*scale-v) for a,v in zip(absolute,values)))
  changed.append(name);errors.append(maximum)
 if not changed:return raw,{'changed_channels':[],'byte_identical':True}
 node.value=list(out); result=scene.to_bytes(); read(result)
 return result,{'changed_channels':changed,'maximum_control_quantization_error':max(errors),'byte_identical':False,'scope':'PC CICD fixed-knot source channels; no inverse rig/graph evaluation'}

def replace_scalar_curves(raw,replacements):
 """Rebuild selected scalar CICD timelines while preserving commands and other curves."""
 scene,node,blob,layout,channels=read(raw);blocks={};errors=[]
 for index,spec in replacements.items():
  row=layout['curves'][index]
  if row['flags']!=0 or row['dimensions']!=1:raise ValueError('Scalar flags-zero CICD curves required')
  times=spec['times'];values=spec['values'];lo,hi=layout['time_range'];segments=len(times)-1
  if not 1<=segments<=4095 or len(values)!=len(times) or abs(times[0]-lo)>1e-7 or abs(times[-1]-hi)>1e-6:raise ValueError('Invalid sampled timeline')
  if any(not math.isfinite(v) for v in times+values):raise ValueError('Nonfinite sampled timeline')
  knots=[round((t-lo)/(hi-lo)*65535) for t in times[:-1]]
  if knots[0]!=0 or any(a>=b for a,b in zip(knots,knots[1:])) or knots[-1]>=65535:raise ValueError('Invalid normalized knots')
  controls=[[a,a+(b-a)/3,a+2*(b-a)/3,b] for a,b in zip(values,values[1:])]
  bias=(min(values)+max(values))/2;scale=max(max(abs(v-bias) for v in values)/32000,max(abs(b-a) for a,b in zip(values,values[1:]))/32000,1e-12)
  bias,scale=struct.unpack('<2f',struct.pack('<2f',bias,scale));payload=bytearray(struct.pack('<I6f',segments<<20|1<<10,lo,hi,values[0],values[-1],bias,scale));payload+=struct.pack('<'+'H'*segments,*knots);worst=0
  for vals in controls:
   absolute=[round((v-bias)/scale) for v in vals];q=[absolute[0]]+[b-a for a,b in zip(absolute,absolute[1:])]
   if any(not -32768<=x<=32767 for x in q):raise ValueError('Quantization overflow')
   payload+=struct.pack('<4h',*q);worst=max(worst,max(abs(bias+x*scale-v) for x,v in zip(absolute,vals)))
  payload+=bytes((-len(payload))%4);blocks[index]=bytes(payload);errors.append(worst)
 if not replacements:return raw,{'changed_curves':[],'byte_identical':True}
 command_start=struct.unpack_from('<I',blob,16)[0];command_end=layout['curves'][0]['offset'];head=bytearray(blob[:command_start]);parts=[blob[command_start:command_end]];offsets=[command_start];cursor=command_end
 for row in layout['curves']:
  offsets.append(cursor);block=blocks.get(row['index'],blob[row['offset']:row['end']]);parts.append(block);cursor+=len(block)
 struct.pack_into('<I',head,12,cursor);struct.pack_into('<'+'I'*len(offsets),head,16,*offsets)
 newblob=bytes(head)+b''.join(parts)+blob[layout['pool_offset']:]
 if len(newblob)>65535:raise ValueError('Edited payload exceeds this template byte-list width; reduce clip sampling density')
 node.value=list(newblob);result=scene.to_bytes();read(result)
 return result,{'changed_curves':sorted(replacements),'byte_identical':False,'maximum_control_quantization_error':max(errors),'sampling_hz':60,'scope':'Changed source Euler components sampled at 60 Hz; original commands, pool and other curves retained'}

def sample_channel(channel,time):
 """Ordinary CICD with native float32 time quantization; no weighted/boundary modes."""
 def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]
 times=channel['times'];lo,hi=times[0],times[-1]
 tick=max(0,min(65535,int(f(f(65535.0/f(hi-lo))*f(f(time)-lo)))))
 knots=[round((t-lo)/(hi-lo)*65535) for t in times]
 k=next((i for i in range(len(knots)-1) if tick<knots[i+1]),len(knots)-2)
 t=(tick-knots[k])/(knots[k+1]-knots[k]);a,b,c,d=channel['controls'][k]
 return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d

def replace_component_samples(raw,edits,hz=30):
 """Rebuild changed multi-component CICD blocks; report shared component resampling."""
 scene,node,blob,layout,channels=read(raw);bykey={(c['curve'],c['dimension']):c for c in channels};blocks={};errors=[];shared=[]
 if not edits:return raw,{'changed_curves':[],'byte_identical':True,'edited_components':[]}
 for index in sorted({k[0] for k in edits}):
  row=layout['curves'][index];dims=row['dimensions']
  if row['flags']!=0:raise ValueError('Only flags-zero CICD supported')
  anyspec=next(v for k,v in edits.items() if k[0]==index);times=anyspec['times'];lo,hi=layout['time_range'];segments=len(times)-1
  if not 1<=segments<=4095 or abs(times[0]-lo)>1e-7 or abs(times[-1]-hi)>1e-6:raise ValueError('Invalid sampled timeline')
  metadata=[];perdim=[]
  for d in range(dims):
   if (index,d) in edits:
    spec=edits[index,d]
    if spec['times']!=times:raise ValueError('Mismatched component times')
    values=spec['values']
   else:
    values=[sample_channel(bykey[index,d],t) for t in times];shared.append({'curve':index,'dimension':d})
   if len(values)!=len(times) or any(not math.isfinite(v) for v in values):raise ValueError('Invalid sampled values')
   controls=[[a,a+(b-a)/3,a+2*(b-a)/3,b] for a,b in zip(values,values[1:])];perdim.append(controls)
   bias=(min(values)+max(values))/2;scale=max(max(abs(v-bias) for v in values)/32000,max(abs(b-a) for a,b in zip(values,values[1:]))/32000,1e-12)
   bias,scale=struct.unpack('<2f',struct.pack('<2f',bias,scale));metadata.append((values[0],values[-1],bias,scale))
  knots=[round((t-lo)/(hi-lo)*65535) for t in times[:-1]]
  if knots[0]!=0 or any(a>=b for a,b in zip(knots,knots[1:])) or knots[-1]>=65535:raise ValueError('Invalid knots')
  payload=bytearray(struct.pack('<I2f',segments<<20|dims<<10,lo,hi))
  for meta in metadata:payload+=struct.pack('<4f',*meta)
  payload+=struct.pack('<'+'H'*segments,*knots);worst=0
  for k in range(segments):
   for d in range(dims):
    vals=perdim[d][k];bias,scale=metadata[d][2:];absolute=[round((v-bias)/scale) for v in vals];q=[absolute[0]]+[b-a for a,b in zip(absolute,absolute[1:])]
    if any(not -32768<=x<=32767 for x in q):raise ValueError('Quantization overflow')
    payload+=struct.pack('<4h',*q);worst=max(worst,max(abs(bias+x*scale-v) for x,v in zip(absolute,vals)))
  payload+=bytes((-len(payload))%4);blocks[index]=bytes(payload);errors.append(worst)
 command_start=struct.unpack_from('<I',blob,16)[0];head=bytearray(blob[:command_start]);parts=[blob[command_start:layout['curves'][0]['offset']]];offsets=[command_start];cursor=layout['curves'][0]['offset']
 for row in layout['curves']:
  offsets.append(cursor);block=blocks.get(row['index'],blob[row['offset']:row['end']]);parts.append(block);cursor+=len(block)
 struct.pack_into('<I',head,12,cursor);struct.pack_into('<'+'I'*len(offsets),head,16,*offsets)
 newblob=bytes(head)+b''.join(parts)+blob[layout['pool_offset']:]
 if len(newblob)>65535:raise ValueError('Edited clip exceeds validated template width; export fewer controls at once')
 node.value=list(newblob);result=scene.to_bytes();read(result)
 return result,{'changed_curves':sorted(blocks),'edited_components':[list(k) for k in edits],'shared_components_resampled':shared,'maximum_control_quantization_error':max(errors),'sampling_hz':hz,'byte_identical':False,'scope':'Direct arm/head Euler and native finger scalar controls; shared dimensions rebaked; no game-playback claim'}
