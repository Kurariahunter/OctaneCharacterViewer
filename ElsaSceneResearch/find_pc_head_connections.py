from exe_reader import *
for vt in [0x1b2d9cc,0x1b2d89c]:
 fn=struct.unpack('<I',read(vt+64,4))[0];print(hex(vt),hex(fn));print(disasm(fn,310))
