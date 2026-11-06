from exe_reader import *
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
cs.skipdata=True
for i in cs.disasm(read(0x4b0000,0x5000),0x4b0000):
 if any(t in i.op_str for t in ['0x1fff','0xe000','0x2000','0x4000','0x8000']):print(f'{i.address:x} {i.mnemonic} {i.op_str}')

