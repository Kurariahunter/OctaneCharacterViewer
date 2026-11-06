"""Checked historical interleaved constant-channel table reader."""
import struct,math,json
from pathlib import Path
ROOT=Path(__file__).parent
WIDTHS={0:3,1:1,2:1,3:1,4:4,5:3,6:1,7:1,8:1,9:1,10:1,11:1,12:1}
def decode(b,layout):
 start=layout['static_commands_start'];end=layout['static_commands_end'];pool=layout['float_pool_start']
 if not 0<=start<end<=pool<=len(b) or (len(b)-pool)%4:raise ValueError('invalid extent')
 constants=struct.unpack_from('<'+'f'*((len(b)-pool)//4),b,pool);p=start
 def take(fmt):
  nonlocal p
  width=struct.calcsize('<'+fmt)
  if p+width>end:raise ValueError('constant descriptor overrun')
  v=struct.unpack_from('<'+fmt,b,p);p+=width;return v
 count=take('H')[0];tracks=[]
 for _ in range(count):
  packed,port=take('HH');n=packed&15;flags=packed&0x10
  if packed&~31 or not 1<=n<=7:raise ValueError('unsupported record flags/count')
  desc=[]
  for _ in range(n):
   op,index=take('HH')
   if op not in WIDTHS:raise ValueError('unsupported constant opcode '+hex(op))
   width=WIDTHS[op]
   if index+width>len(constants):raise ValueError('constant index range')
   values=list(constants[index:index+width])
   if not all(math.isfinite(x) for x in values):raise ValueError('nonfinite constant')
   if op==4 and abs(sum(x*x for x in values)-1)>.002:raise ValueError('nonunit constant quaternion')
   desc.append({'opcode':op,'index':index,'values':values})
  tracks.append({'port':port,'record_flags':flags,'descriptors':desc})
 if (p+3)//4*4!=end or b[p:end] not in (b'',b'\0\0',b'\xee\xee'):raise ValueError('constant boundary mismatch')
 return {'tracks':tracks,'consumed_end':p,'aligned_end':end,'float_count':len(constants)}
if __name__=='__main__':
 for name in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
  layout=json.loads((ROOT/(name+'-decoded-curves.json')).read_text());b=(ROOT/(name+'.clipdata.bin')).read_bytes();r=decode(b,layout);(ROOT/(name+'-constant-channels.json')).write_text(json.dumps(r,indent=2));print(name,'CONSTANT_TRACKS',len(r['tracks']),'EXACT_END',r['aligned_end'])
  for track in r['tracks']:
   if track['port'] in [308,370,397,399,400]:print(track)
  for malformed in [b[:layout['float_pool_start']],b[:-1]]:
   try:decode(malformed,layout)
   except (ValueError,struct.error):pass
   else:raise AssertionError('malformed accepted')
