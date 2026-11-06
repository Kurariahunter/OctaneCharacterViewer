from exe_reader import *
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.skipdata=True
print('CALLS')
for i in cs.disasm(read(0x5382f0,0x2000),0x5382f0):
 if i.mnemonic=='call':print(hex(i.address),i.op_str)
needle=struct.pack('<I',0x1b35744);start=0
while True:
 o=b.find(needle,start)
 if o<0:break
 start=o+1;v=next(base+r+o-p for r,s,p in sections if p<=o<p+s)
 if v<0x1700000:print('VTREF',hex(v),disasm(v-6,36))
