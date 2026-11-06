import struct,math
"""Installed-PC packed command variant. Shared curve structure; no final bone mapping."""

import math

def decode(b):
 def u(fmt,p): return struct.unpack_from('<'+fmt,b,p)
 if len(b)<24: raise ValueError('short header')
 flag,n=u('HH',8)
 if flag!=1 or not 0<n<1024: raise ValueError('unsupported animated header')
 offsets=u('I'*(n+2),12);pool=offsets[0];starts=offsets[1:]
 if starts[0]!=12+4*(n+2) or not all(a<z for a,z in zip(starts,starts[1:])) or not starts[-1]<pool<=len(b): raise ValueError('bad offsets')
 if (len(b)-pool)%4:raise ValueError('unaligned float pool extent')
 regs,count=u('HH',starts[0]);order=u('H'*count,starts[0]+4)
 if count!=n or order!=tuple(range(n)): raise ValueError('unsupported curve permutation')
 curves=[];registers=[];max_error=0
 for ci,(s,e) in enumerate(zip(starts[1:],list(starts[2:])+[pool])):
  kind,size=u('HH',s);dims=kind>>10;segs=size//16
  flags=kind&0x3ff
  # PC walk/run curves additionally use boundary mode bits0x12/0x02/0x10. Native522cf0
  # extracts dimensions from bits10..19 and dispatches range handling using
  # low bits; the interior knot/coefficient layout is unchanged. Sampling in
  # the file reader uses the original native routine, including boundaries.
  if flags not in (0,2,0x10,0x12) or not 1<=dims<=128 or size%16 or segs<1: raise ValueError('unknown curve format')
  lo,hi=u('ff',s+4);meta=[u('4f',s+12+16*d) for d in range(dims)];p=s+12+16*dims;knots=u('H'*segs,p);p+=2*segs
  # Coefficients immediately follow knots; padding occurs at the block end.
  aligned=p
  if b[p:aligned] not in (b'',b'\xee\xee',b'\0\0'): raise ValueError('bad knot padding')
  p=aligned
  if not hi>lo or knots[0]!=0 or any(a>=z for a,z in zip(knots,knots[1:])): raise ValueError('bad time range')
  data=[]
  for k in range(segs):
   row=[]
   for d in range(dims):
    q=u('4h',p);p+=8;bias,scale=meta[d][2:];v=[bias+q[0]*scale]
    for delta in q[1:]:v.append(v[-1]+delta*scale)
    if not all(math.isfinite(x) for x in v):raise ValueError('nonfinite')
    row.append(v)
   data.append(row)
  if (p+3)//4*4!=e or b[p:e] not in (b'',b'\xee\xee',b'\0\0'):raise ValueError(f'boundary {ci}: {p} != {e}')
  errors=[]
  for d in range(dims):
   scale=meta[d][3]
   err=max([abs(data[k][d][-1]-data[k+1][d][0]) for k in range(segs-1)]+[0])
   errors.append(err/max(abs(scale),1e-30));max_error=max(max_error,errors[-1])
   registers.append({'curve':ci,'component':d})
  curves.append({'time_start':lo,'time_end':hi,'boundary_flags':flags,'knots':knots,'metadata':meta,'segments':data,'continuity_error_quantization_units':errors})
 if len(registers)!=regs:raise ValueError('register count mismatch')
 p=starts[0]+4+2*n;dynamic_bytes,num=u('HH',p);p+=4
 codes=u('H'*num,p);p+=2*num;commands=[]
 for code in codes:
  count=code>>13;port=code&0x1fff
  if not 1<=count<=7:raise ValueError('invalid packed command count')
  desc=[]
  for _ in range(count):
   op=u('H',p)[0];width=8 if op&0xf000==0x1000 else 4
   if op&0xf000!=0x1000 and op not in (17,18,19,22,23,24,26):raise ValueError('unsupported timed opcode '+hex(op))
   fields=u('H'*(width//2),p);p+=width
   refs=[fields[i+1] for i,shift in enumerate((4,2,0)) if ((op>>shift)&3)==1] if width==8 else fields[1:2]
   if any(ref>=regs for ref in refs):raise ValueError('register bounds')
   desc.append(list(fields))
  commands.append({'port':port,'descriptors':desc,'packed_code':code})
 if p!=starts[0]+dynamic_bytes:raise ValueError('packed dynamic extent mismatch')
 return {'curves':curves,'registers':registers,'commands':commands,'max_continuity_error_quantization_units':max_error,'static_commands_start':p,'static_commands_end':starts[1],'float_pool_start':pool}

def sample(result,reg,t):
 # Native 0x5232e1 quantizes time to uint16 before choosing a segment.
 # Preserve the SSE float32 operation order before truncation.
 def f(v):return struct.unpack('<f',struct.pack('<f',v))[0]
 r=result['registers'][reg];c=result['curves'][r['curve']];d=r['component']
 lo=c['time_start'];hi=c['time_end'];t=f(t)
 tick=max(0,min(65535,int(f(f(65535.0/f(hi-lo))*f(t-lo)))))
 knots=list(c['knots'])+[65535]
 k=next((i for i in range(len(knots)-1) if tick<knots[i+1]),len(knots)-2)
 x=(tick-knots[k])/(knots[k+1]-knots[k]);a,b,cc,dd=c['segments'][k][d]
 return (1-x)**3*a+3*(1-x)**2*x*b+3*(1-x)*x*x*cc+x**3*dd


def constants(b,layout):
 from decode_elsa_static_channels import WIDTHS
 start=layout['static_commands_start'];end=layout['static_commands_end'];pool=layout['float_pool_start']
 if (len(b)-pool)%4:raise ValueError('invalid float pool')
 values=struct.unpack_from('<'+'f'*((len(b)-pool)//4),b,pool)
 count=struct.unpack_from('<H',b,start)[0];p=start+2;codes=struct.unpack_from('<'+'H'*count,b,p);p+=count*2;tracks=[]
 for code in codes:
  n=code>>13;port=code&0x1fff
  if not 1<=n<=7:raise ValueError('invalid packed static count')
  descriptors=[]
  for _ in range(n):
   if p+4>end:raise ValueError('static descriptor overrun')
   op,index=struct.unpack_from('<HH',b,p);p+=4
   if op not in WIDTHS:raise ValueError('unknown static opcode')
   width=WIDTHS[op]
   if index+width>len(values):raise ValueError('constant pool bounds')
   v=list(values[index:index+width])
   if not all(math.isfinite(x) for x in v):raise ValueError('nonfinite constant')
   descriptors.append({'opcode':op,'index':index,'values':v})
  tracks.append({'port':port,'descriptors':descriptors,'packed_code':code})
 if (p+3)//4*4!=end or b[p:end] not in (b'',b'\x00\x00',b'\xee\xee'):raise ValueError('static extent mismatch')
 return {'tracks':tracks,'float_count':len(values)}
