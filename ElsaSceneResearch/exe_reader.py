import struct,sys
from pathlib import Path
sys.path.insert(0,'C:/Users/Kurar/.codex/visualizations/2026/09/19/01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1/DI3ConverterValidation/YodaAnimationProbe/analysis_dependencies')
import capstone
PATH=Path('F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/DisneyInfinity3.exe')
b=PATH.read_bytes();pe=struct.unpack_from('<I',b,60)[0];n=struct.unpack_from('<H',b,pe+6)[0];opt=struct.unpack_from('<H',b,pe+20)[0];base=struct.unpack_from('<I',b,pe+52)[0]
sections=[]
for i in range(n):
 p=pe+24+opt+40*i;vs,rva,sz,raw=struct.unpack_from('<IIII',b,p+8);sections.append((rva,sz,raw))
def read(va,size):
 for r,s,p in sections:
  if r<=va-base and va-base+size<=r+s:return b[p+va-base-r:p+va-base-r+size]
 raise ValueError('VA outside file-backed section')
def disasm(va,size):
 return '\n'.join(f'{i.address:08X} {i.mnemonic} {i.op_str}' for i in capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(read(va,size),va))
if __name__=='__main__':print(disasm(int(sys.argv[1],0),int(sys.argv[2],0)))
