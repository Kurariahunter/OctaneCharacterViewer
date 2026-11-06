"""Bounded ClipDataBlock command partitions; PC/Wii U byte order, no graph evaluation.
Each block owns its register order and template routing must be selected separately.
"""
import struct,math
STATIC_WIDTHS={0:3,1:1,2:1,3:1,4:4,5:3,6:1,7:1,8:1,10:1,12:1}

def read_command_blocks(b,endian='<'):
 if endian not in ('<','>'):raise ValueError('Invalid command byte order')
 def u(fmt,p,end=None):
  n=struct.calcsize(endian+fmt)
  if p<0 or p+n>(len(b)if end is None else end):raise ValueError('Command field outside block')
  return struct.unpack_from(endian+fmt,b,p)
 if len(b)<20:raise ValueError('Short command header')
 nc,nt=u('HH',8);pool=u('I',12)[0]
 if not 1<=nc<=64 or nt>1024:raise ValueError('Unsupported command/curve count')
 offsets=u('I'*(nc+nt),16)
 if offsets[0]!=16+4*(nc+nt)or not all(a<z for a,z in zip(offsets,offsets[1:]))or not offsets[-1]<pool<=len(b)or(len(b)-pool)%4:raise ValueError('Invalid command offsets/pool')
 pool_count=(len(b)-pool)//4;dims=[(u('I',at)[0]>>10)&1023 for at in offsets[nc:]];blocks=[];seen=[]
 for index,start in enumerate(offsets[:nc]):
  end=offsets[index+1]if index+1<len(offsets)else pool
  regs,count=u('HH',start,end);order=list(u('H'*count,start+4,end));seen.extend(order)
  if any(i>=nt for i in order)or len(set(order))!=count or regs!=sum(dims[i]for i in order):raise ValueError('Invalid block timeline/registers map')
  pos=start+4+2*count;size,num=u('HH',pos,end);pos+=4
  dynamic_end=start+size
  if not pos<=dynamic_end<=end:raise ValueError('Invalid dynamic command extent')
  codes=u('H'*num,pos,dynamic_end);pos+=2*num;records=[]
  for code in codes:
   n,port=code>>13,code&8191
   if not 1<=n<=7:raise ValueError('Invalid packed descriptor count')
   descriptors=[]
   for _ in range(n):
    op=u('H',pos,dynamic_end)[0];group=op&0xf000
    if group==0:
     fields=u('2H',pos,dynamic_end);pos+=4
     if op not in (0x11,0x12,0x13,0x16,0x17,0x18,0x1a,0x1c)or fields[1]>=regs:raise ValueError(f'Unsupported or out-of-range scalar descriptor op={op:#x} ref={fields[1]} regs={regs} block={index}')
    elif group==0x1000:
     fields=u('4H',pos,dynamic_end);pos+=8
     if (op>>6)&7!=2:raise ValueError('Unsupported Euler convention')
     for ref,shift in zip(fields[1:],(4,2,0)):
      mode=(op>>shift)&3
      if mode not in (0,1)or ref>=(regs if mode else pool_count):raise ValueError('Invalid Euler reference')
    else:raise ValueError(f'Unsupported timed descriptor class 0x{op:X}')
    descriptors.append(dict(opcode=hex(op),fields=list(fields),semantics_validated=True))
   records.append(dict(phase='timed',port=port,descriptors=descriptors))
  if pos!=dynamic_end:raise ValueError('Dynamic command size mismatch')
  num=u('H',pos,end)[0];pos+=2;codes=u('H'*num,pos,end);pos+=2*num
  for code in codes:
   n,port=code>>13,code&8191
   if not 1<=n<=7:raise ValueError('Invalid static descriptor count')
   descriptors=[]
   for _ in range(n):
    op,ref=u('2H',pos,end);pos+=4;width=STATIC_WIDTHS.get(op)
    if width is None or ref+width>pool_count:raise ValueError('Unsupported or out-of-range static descriptor')
    values=u('f'*width,pool+4*ref)
    if not all(math.isfinite(v)for v in values):raise ValueError('Nonfinite static pool value')
    descriptors.append(dict(opcode=hex(op),pool_index=ref,values=list(values)))
   records.append(dict(phase='static',port=port,descriptors=descriptors))
  padding=b[pos:end]
  if len(padding)>3 or any(v not in (0,0xee)for v in padding):raise ValueError('Unexpected command trailing bytes')
  blocks.append(dict(index=index,offset=start,end=end,registers=regs,timeline_order=order,dynamic_end=dynamic_end,records=records,padding_bytes=len(padding)))
 if sorted(seen)!=list(range(nt)):raise ValueError('Command blocks do not partition timelines')
 return blocks

