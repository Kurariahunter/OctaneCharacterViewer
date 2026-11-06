from exe_reader import *
for mask in [0x1fff,0xe000]:
 needle=struct.pack('<I',mask);start=0;found=[]
 while True:
  off=b.find(needle,start)
  if off<0:break
  start=off+1
  try:va=next(base+r+off-p for r,s,p in sections if p<=off<p+s)
  except StopIteration:continue
  if 0x480000<va<0x590000:found.append(hex(va))
 print(hex(mask),found)
