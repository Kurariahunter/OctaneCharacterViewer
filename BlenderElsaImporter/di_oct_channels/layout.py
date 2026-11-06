"""Read-only inspector for Wii U ClipDataBlock CICD cubic timelines.
Not a skeleton player or native-code emulator. Verified against one Wii U Elsa idle.
"""
from pathlib import Path
import struct,json,math,hashlib,sys

def inspect(b,sample_times=None,allowed_boundary_flags=(0,),endian='>',allow_constant=False):
 if endian not in ('<','>'):raise ValueError('Invalid byte order')
 def u(fmt,p):
  size=struct.calcsize(endian+fmt)
  if p<0 or p+size>len(b):raise ValueError('Field outside ClipDataBlock')
  return struct.unpack_from(endian+fmt,b,p)
 if len(b)<20:raise ValueError('Short clip header')
 lo,hi=u('ff',0);ncommands,ncurves=u('HH',8);pool=u('I',12)[0]
 if not math.isfinite(lo+hi)or hi<=lo or not 0<ncommands<=64 or not (0<=ncurves<=1024 if allow_constant else 0<ncurves<=1024):raise ValueError(f'Unsupported clip header: range=({lo},{hi}), command_blocks={ncommands}, timelines={ncurves}')
 offsets=u('I'*(ncommands+ncurves),16);end_header=16+4*len(offsets)
 if offsets[0]!=end_header or not all(a<z for a,z in zip(offsets,offsets[1:]))or not offsets[-1]<pool<=len(b)or(len(b)-pool)%4:raise ValueError('Invalid offsets/pool')
 # Only this measured command-block layout is used to audit curve register counts.
 if ncommands!=1:raise ValueError('Multiple command blocks not yet validated')
 registers,count=u('HH',offsets[0]);order=u('H'*count,offsets[0]+4)
 if count!=ncurves or sorted(order)!=list(range(ncurves)):raise ValueError('Invalid timeline map')
 curves=[];regcount=0
 for i,start in enumerate(offsets[ncommands:]):
  end=offsets[ncommands+i+1]if i+1<ncurves else pool
  word=u('I',start)[0];dims=(word>>10)&1023;segments=word>>20;flags=word&1023
  if flags not in allowed_boundary_flags or not 1<=dims<=128 or not 1<=segments<=4095:raise ValueError(f'Unsupported curve type{flags:X}: dimensions={dims}, segments={segments}, offset={start}')
  t0,t1=u('ff',start+4)
  if not math.isfinite(t0+t1)or t1<=t0:raise ValueError('Invalid curve range')
  kind=flags&0x3c0
  if kind not in (0,0x40):raise ValueError('Unsupported timeline encoding')
  weighted=kind==0x40;meta_width=20 if weighted else 16;coefficient_width=7 if weighted else 4
  metadata=[u('5f'if weighted else'4f',start+12+meta_width*d)for d in range(dims)];p=start+12+meta_width*dims
  if not all(math.isfinite(v)for row in metadata for v in row):raise ValueError('Nonfinite curve metadata')
  knots=u('H'*segments,p);p+=2*segments
  if knots[0]!=0 or any(a>=z for a,z in zip(knots,knots[1:])):raise ValueError('Invalid knots')
  data=[]
  for k in range(segments):
   values=[]
   for d in range(dims):
    q=u('7h'if weighted else'4h',p);p+=2*coefficient_width;bias,scale=metadata[d][2:4]
    if scale<0 or not math.isfinite(bias+scale):raise ValueError('Invalid quantization')
    if weighted:
     if metadata[d][4]<0:raise ValueError('Invalid weighted quantization')
     # CICDW has seven shorts and a separate fifth metadata float. Its
     # weighted time inversion is evaluated by the original native routine;
     # do not run the ordinary four-control Python interpolation on it.
     values.append(q);continue
    v=[bias+q[0]*scale]
    for delta in q[1:]:v.append(v[-1]+delta*scale)
    if not all(math.isfinite(x)for x in v):raise ValueError('Invalid controls')
    values.append(v)
   data.append(values)
  if (p+3)&~3!=end:raise ValueError(f'Curve{i} extent mismatch')
  discontinuities=[]
  for k in range(0 if weighted else segments-1):
   for d in range(dims):
    jump=abs(data[k][d][-1]-data[k+1][d][0])
    if jump>max(8*metadata[d][3],1e-6):
     discontinuities.append({'segment':k,'dimension':d,'decoded_jump':jump})
     if sample_times!=[]:raise ValueError(f'Discontinuous curve{i} requires native sampling')
  if flags and sample_times!=[]:raise ValueError('Nonzero boundary flags require native sampler')
  samples=[]
  for time in (sample_times if sample_times is not None else [t0,(t0+t1)/2,t1]):
   if time<t0:
    samples.append({"time":time,"values":[v[0] for v in data[0]],"boundary":"flags0 hold decoded start"});continue
   if time>t1:
    samples.append({"time":time,"values":[m[1] for m in metadata],"boundary":"flags0 hold stored metadata end"});continue
   phase=(time-t0)/(t1-t0);normalized=[x/65535 for x in knots];seg=max(k for k,v in enumerate(normalized)if phase>=v);a=normalized[seg];z=normalized[seg+1]if seg+1<segments else 1;t=(phase-a)/(z-a)
   samples.append({'time':time,'values':[(1-t)**3*v[0]+3*(1-t)**2*t*v[1]+3*(1-t)*t*t*v[2]+t**3*v[3]for v in data[seg]]})
  curves.append({'index':i,'offset':start,'end':end,'flags':flags,'encoding':'CICDW'if weighted else'CICD','metadata_bytes_per_dimension':meta_width,'coefficient_shorts_per_dimension':coefficient_width,'dimensions':dims,'segments':segments,'range':[t0,t1],'continuity_warnings':discontinuities,'samples':samples});regcount+=dims
 if regcount!=registers:raise ValueError('Computed registers do not match command block')
 return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'time_range':[lo,hi],'command_blocks':ncommands,'timelines':ncurves,'registers':regcount,'pool_offset':pool,'pool_floats':(len(b)-pool)//4,'curves':curves,'scope':'Structural validation and cubic samples only; no command dispatch, bone mapping or game-parity claim.'}
if __name__=='__main__':
 report=inspect(Path(sys.argv[1]).read_bytes());Path(sys.argv[2]).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='curves'},indent=2))
