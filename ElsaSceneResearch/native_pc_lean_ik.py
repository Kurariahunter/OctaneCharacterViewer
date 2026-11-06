"""Hash-pinned PC 8/3 solver adapter. Offline; no game process access.

Inputs remain runtime slots. Captured cached values are used without invoking
upstream producers. This is a research adapter, not a complete clip decoder.
"""
import sys,json,struct,hashlib,math
from pathlib import Path
sys.path.insert(0,'C:/Users/Kurar/.codex/visualizations/2026/09/19/01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1/DI3ConverterValidation/YodaAnimationProbe/analysis_dependencies')
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
R=Path(__file__).parent
exe=Path('F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/DisneyInfinity3.exe');sha=hashlib.sha256(exe.read_bytes()).hexdigest()
assert sha=='f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705'
pe=pefile.PE(str(exe));u=Uc(UC_ARCH_X86,UC_MODE_32);base=pe.OPTIONAL_HEADER.ImageBase;u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image());u.mem_map(0x10000000,0x20000)
def replay(p):
 assert p["input_count"]==8 and p["output_count"]==3
 assert len(p["inputs"])==8 and len(p["outputs"])==3
 proc=0x10001000;network=0x10003000;stack=0x10010000;stop=0x10000100
 h=bytearray.fromhex(p['processor_header_hex']);struct.pack_into('<H',h,0x18,0x80);u.mem_write(proc,bytes(h));u.mem_write(network,b'\0'*128)
 nodes=[]
 for i,item in enumerate(p['inputs']+p['outputs']):
  if item['node']=='0x0':nodes.append(0);continue
  ptr=0x10004000+256*i;nodes.append(ptr);h=bytearray.fromhex(item['header_hex']);struct.pack_into('<I',h,0x18,0);struct.pack_into('<I',h,0x1c,network);struct.pack_into('<H',h,0x20,0)
  u.mem_write(ptr,bytes(h)+bytes.fromhex(item['payload_prefix_hex64']))
 u.mem_write(proc+0x80,struct.pack('<11I',*nodes));u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc)
 try:u.emu_start(0x5382f0,stop,count=500000)
 except Exception as e:raise RuntimeError(f'{u.reg_read(UC_X86_REG_EIP):x}: {e}')
 assert u.reg_read(UC_X86_REG_EIP)==stop
 return [struct.unpack('<'+('4f' if i<2 else 'f'),u.mem_read(n+0x34,16 if i<2 else 4)) for i,n in enumerate(nodes[8:])]

def solve(values):
 """Numeric PC runtime slots; no captured header or cached output is used."""
 if len(values)!=8:raise ValueError('PC solver requires eight slots')
 expected=[3,3,3,3,3,4,1,1]
 for value,count in zip(values,expected):
  if value is not None and (len(value)!=count or not all(math.isfinite(v)for v in value)):raise ValueError('invalid solver slot')
 if any(values[i] is None for i in [0,1,2,3,4,6,7]):raise ValueError('missing required PC slot')
 h=bytearray(36);struct.pack_into('<HBB',h,0x18,0x80,8,3)
 rows=[]
 for value in values+[[0,0,0,1],[0,0,0,1],[1]]:
  payload=bytearray(64)
  if value is not None:struct.pack_into('<'+'f'*len(value),payload,0,*value)
  rows.append({'node':'0x1' if value is not None else '0x0','header_hex':bytes(52).hex(),'payload_prefix_hex64':payload.hex()})
 out=replay({'input_count':8,'output_count':3,'processor_header_hex':h.hex(),'inputs':rows[:8],'outputs':rows[8:]})
 if not all(math.isfinite(v)for row in out for v in row):raise ValueError('nonfinite PC IK result')
 return out
