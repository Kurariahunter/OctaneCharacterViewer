from exe_reader import *
for vt in [0x1b2eb94,0x1b2edac,0x1b2f164]:
 fn=struct.unpack('<I',read(vt+64,4))[0];print(hex(vt),hex(fn));print(disasm(fn,80))
