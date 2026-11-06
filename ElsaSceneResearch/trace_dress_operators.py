from exe_reader import *
for name in ['ConcatenateChainDilation','ConcatenateChainInverseDilation','InvertDilation']:
 start=0
 while True:
  off=b.find(name.encode()+b'\0',start)
  if off<0:break
  start=off+1;va=next(base+r+off-p for r,s,p in sections if p<=off<p+s)
  print(name,hex(va),b[off-12:off+len(name)+1])
  for shift in range(40):
   pat=struct.pack('<I',va-shift);o=0
   while True:
    o=b.find(pat,o)
    if o<0:break
    addr=next(base+r+o-p for r,s,p in sections if p<=o<p+s);o+=1
    if addr<0x1700000:print('shift',shift,disasm(addr-12,52))

