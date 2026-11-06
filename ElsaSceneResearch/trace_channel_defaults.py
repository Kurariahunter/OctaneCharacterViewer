from exe_reader import *
import json
names=['DefaultDataIndices','DefaultData','ConnectionMapUsedDataNodes','BaseDataNodeLinks','ChannelIndex','PriorityOrder']
rows=[]
for name in names:
 start=0
 while True:
  off=b.find(name.encode()+b'\0',start)
  if off<0:break
  start=off+1;va=next(base+r+off-p for r,s,p in sections if p<=off<p+s)
  refs=[];o=0;needle=struct.pack('<I',va)
  while True:
   o=b.find(needle,o)
   if o<0:break
   addr=next(base+r+o-p for r,s,p in sections if p<=o<p+s);o+=1
   if addr<0x1700000:refs.append(hex(addr))
  row={'name':name,'address':hex(va),'references':refs};rows.append(row);print(row)
Path('channel-default-string-references.json').write_text(json.dumps(rows,indent=2))
