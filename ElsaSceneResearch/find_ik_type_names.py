from exe_reader import *
print(read(0x1b356e0,0x100))
for term in [b'IK2BRP',b'IK2B']:
 start=0
 while True:
  o=b.find(term,start)
  if o<0:break
  start=o+1
  if term==b'IK2B' and b[o:o+6]==b'IK2BRP':continue
  va=next(base+r+o-p for r,s,p in sections if p<=o<p+s)
  print(hex(va),b[o:o+120].split(b'\0')[0])
