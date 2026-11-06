from exe_reader import *
vt=0x1b35744
for i in [2,16]:
 fn=struct.unpack('<I',read(vt+4*i,4))[0];print('slot',i,hex(fn),disasm(fn,6))
print('name',read(0x1b357b8,50).split(b'\0')[0])
