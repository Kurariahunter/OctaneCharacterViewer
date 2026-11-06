"""Native instruction-window tests for blend property normalization and flag selection.
Property lookup / clip lookup / invalidation callbacks are explicit synthetic stubs.
This does not establish the missing track-to-clip mode transfer.
"""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDI,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
from exe_reader import disasm
R=Path(__file__).parent
STACK=0x10018000;DEST=0x10011000;PROP=0x10012000;VT=0x10013000;STUB=0x10014000;NET=0x10015000;CLIP=0x10016000

def write32(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
def run_loader(value,kind=3,subtype=3,present=True):
 u.mem_write(DEST,b'\xa5'*128);u.mem_write(PROP,b'\0'*128);u.mem_write(STACK,b'\0'*128);write32(STACK+0x1c,0x12345678)
 write32(PROP,VT);write32(VT+4,STUB);u.mem_write(STUB,b'\xb8'+struct.pack('<I',kind)+b'\xc3');write32(PROP+0x20,subtype);write32(PROP+0x18,value)
 def hook(uc,address,size,data):
  if address==0x7807a3:uc.reg_write(UC_X86_REG_EAX,PROP if present else 0);uc.reg_write(UC_X86_REG_EIP,0x7807a8)
 h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_X86_REG_EDI,DEST);u.reg_write(UC_X86_REG_ESP,STACK)
 try:u.emu_start(0x780796,0x7807e2,count=1000)
 finally:u.hook_del(h)
 assert u.reg_read(UC_X86_REG_EIP)==0x7807e2
 got=struct.unpack('<I',u.mem_read(DEST+8,4))[0];wanted=int(present and kind==3 and subtype==3 and value!=0);assert got==wanted
 return dict(value=value,kind=kind,subtype=subtype,present=present,output=got,expected=wanted)

def run_flag(network_bits,clip_mode,initial):
 u.mem_write(DEST,b'\0'*128);u.mem_write(NET,b'\0'*128);u.mem_write(CLIP,b'\0'*128);u.mem_write(STACK,b'\0'*128)
 write32(DEST+0x70,NET if network_bits is not None else 0);write32(NET+0x18,network_bits or 0);write32(CLIP+0x44,clip_mode or 0);u.mem_write(DEST+0x39,bytes([initial]));calls=[]
 def hook(uc,address,size,data):
  if address==0x78266a:uc.reg_write(UC_X86_REG_EAX,CLIP if clip_mode is not None else 0);uc.reg_write(UC_X86_REG_EIP,0x78266f)
  elif address==0x782686:calls.append('invalidation callback');uc.reg_write(UC_X86_REG_EIP,0x78268b)
 h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_X86_REG_ESI,DEST);u.reg_write(UC_X86_REG_ESP,STACK)
 try:u.emu_start(0x782658,0x78268b,count=1000)
 finally:u.hook_del(h)
 assert u.reg_read(UC_X86_REG_EIP)==0x78268b
 got=u.mem_read(DEST+0x39,1)[0];wanted=(network_bits&1)if network_bits is not None else int(clip_mode==1);assert got==wanted and len(calls)==int(initial!=wanted)
 return dict(network_bits=network_bits,clip_mode=clip_mode,initial=initial,output=got,expected=wanted,invalidation_calls=len(calls))
loader=[run_loader(v,subtype=t)for t in (0,3)for v in (0,1,2,-1)]+[run_loader(1,kind=2),run_loader(1,subtype=1),run_loader(1,present=False)]
flags=[run_flag(n,c,i)for n in (None,0,1,2,3)for c in (None,0,1,2)for i in (0,1)]
report=dict(exe_sha256=sha,loader_window=['0x780796','0x7807e2'],flag_window=['0x782658','0x78268b'],loader_cases=len(loader),flag_cases=len(flags),stubs=['property lookup return at call0x7807a3','property type virtual getter returns synthetic kind','resolved clip lookup return at call0x78266a','invalidation callback0x4bcc00 skipped and counted'],loader=loader,flags=flags,scope='Original native instruction windows and real getters4b1150/5253b0; synthetic isolated objects. Does not execute full loader or prove how track property reaches network flags/clip mode. No game memory access.')
(R/'pc-blend-loader-validation.json').write_text(json.dumps(report,indent=2))
for name,va,size in [('blend-property-loader',0x780770,0x18d),('blend-runtime-flag-selection',0x782658,0x33),('blend-network-flag-getter',0x4b1150,7),('blend-clip-mode-getter',0x5253b0,10),('blend-config-row-getter',0x76cc50,0x19),('blend-controller-getter',0x19368d0,4)]:
 (R/(name+'-disassembly.txt')).write_text(disasm(va,size))
print(json.dumps({k:report[k]for k in ['exe_sha256','loader_cases','flag_cases','stubs','scope']},indent=2))

