from exe_reader import *
for i in range(27):
 fn=struct.unpack('<I',read(0x1b35744+4*i,4))[0]
 print(i,hex(fn),disasm(fn,25) if 0x400000<fn<0x1700000 else '')
