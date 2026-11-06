import struct,math
"""Research-only timed curve reader. Does not emit bone animation or assume Euler order."""

import math

def decode(b):
 def u(fmt,p): return struct.unpack_from('<'+fmt,b,p)
 if len(b)<24: raise ValueError('short header')
 flag,n=u('HH',8)
 if flag!=1 or not 0<n<1024: raise ValueError('unsupported animated header')
 offsets=u('I'*(n+2),12);pool=offsets[0];starts=offsets[1:]
 if starts[0]!=12+4*(n+2) or not all(a<z for a,z in zip(starts,starts[1:])) or not starts[-1]<pool<=len(b): raise ValueError('bad offsets')
 regs,count=u('HH',starts[0]);order=u('H'*count,starts[0]+4)
 if count!=n or order!=tuple(range(n)): raise ValueError('unsupported curve permutation')
 curves=[];registers=[];max_error=0
 for ci,(s,e) in enumerate(zip(starts[1:],list(starts[2:])+[pool])):
  kind,size=u('HH',s);dims=kind>>10;segs=size//16
  if kind!=dims*1024 or not 1<=dims<=128 or size%16 or segs<1: raise ValueError('unknown curve format')
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
  curves.append({'time_start':lo,'time_end':hi,'knots':knots,'metadata':meta,'segments':data,'continuity_error_quantization_units':errors})
 if len(registers)!=regs:raise ValueError('register count mismatch')
 p=starts[0]+4+2*n;dynamic_bytes,num=u('HH',p);p+=4;commands=[]
 for _port in range(num):
  descriptor_count,port=u('HH',p);p+=4
  if descriptor_count&~0x1F:raise ValueError(f'unsupported descriptor flags {descriptor_count} at 0x{p-4:X}, port {port}')
  descriptor_flags=descriptor_count&0x10;descriptor_count&=15
  desc=[]
  for _ in range(descriptor_count):
   op=u('H',p)[0];width=8 if op&0xF000==0x1000 else 4
   if op&0xF000!=0x1000 and op not in (17,18,19,22,23,24,26):raise ValueError(f'unknown command 0x{op:04X} at payload offset 0x{p:X}')
   fields=u('H'*(width//2),p);p+=width
   refs=[fields[i+1] for i,shift in enumerate((4,2,0)) if ((op>>shift)&3)==1] if op&0xF000==0x1000 else fields[1:2]
   if any(x>=regs for x in refs):raise ValueError('register out of bounds')
   desc.append(list(fields))
  commands.append({'port':port,'descriptors':desc,'record_flags':descriptor_flags})
 if p!=starts[0]+dynamic_bytes:raise ValueError('dynamic boundary')
 return {'curves':curves,'registers':registers,'commands':commands,'max_continuity_error_quantization_units':max_error,'static_commands_start':p,'static_commands_end':starts[1],'float_pool_start':pool}

def sample(result,reg,t):
 r=result['registers'][reg];c=result['curves'][r['curve']];d=r['component'];knots=[c['time_start']+(c['time_end']-c['time_start'])*k/65535 for k in c['knots']]+[c['time_end']]
 k=next((i for i in range(len(knots)-1) if t<=knots[i+1]),len(knots)-2);x=max(0,min(1,(t-knots[k])/(knots[k+1]-knots[k])));a,b,cc,dd=c['segments'][k][d]
 return (1-x)**3*a+3*(1-x)**2*x*b+3*(1-x)*x*x*cc+x**3*dd
