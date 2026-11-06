from native_pc_lean_ik import u
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from pathlib import Path
md=Cs(CS_ARCH_X86,CS_MODE_32);out=[]
for name,address,size in [('BaseTrackConstructor',0x5a2260,360),('CommonTrackLoader',0x780825,390)]:
 out.append(name)
 for ins in md.disasm(bytes(u.mem_read(address,size)),address):out.append(f'{ins.address:08X} {ins.mnemonic} {ins.op_str}')
for a in [0x1b4c2e8,0x1b35cb4]:out.append(hex(a)+' '+bytes(u.mem_read(a,80)).split(b'\0')[0].decode('ascii','replace'))
Path(__file__).with_name('pc-track-defaults-disassembly.txt').write_text('\n'.join(out));print('\n'.join(out[:160]));print('\n'.join(out[-2:]))
