from exe_reader import *
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for va,size in [(0x4f09c0,0x170),(0x4f0f80,0x1a0),(0x4f1ae0,0x1f0)]:
 print(hex(va));print('\n'.join(f'{i.address:x} {i.mnemonic} {i.op_str}' for i in cs.disasm(read(va,size),va) if i.mnemonic=='call'))
