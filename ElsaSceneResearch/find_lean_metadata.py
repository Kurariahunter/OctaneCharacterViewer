from exe_reader import *
for target in [0x54ad00,0x21bd5dc]:
 for r,s,p in sections:
  if base+r>0x1700000:continue
  data=b[p:p+s]
  for o in range(len(data)-4):
   if (target==0x54ad00 and data[o]==232 and base+r+o+5+struct.unpack_from('<i',data,o+1)[0]==target) or (target!=0x54ad00 and struct.unpack_from('<I',data,o)[0]==target):
    print(hex(target),hex(base+r+o));print(disasm(base+r+o-15,65))
