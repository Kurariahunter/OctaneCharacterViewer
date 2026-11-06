from exe_reader import *
f=struct.unpack('<I',read(0x1b2d29c+64,4))[0];print(hex(f));print(disasm(f,320))
