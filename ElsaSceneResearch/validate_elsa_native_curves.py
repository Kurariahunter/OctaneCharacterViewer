"""Evaluate isolated original math routine only; never launch the game."""
import sys,struct,json,ast,math,hashlib
from pathlib import Path
ROOT=Path(__file__).parent
sys.path.insert(0,'C:/Users/Kurar/.codex/visualizations/2026/09/19/01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1/DI3ConverterValidation/YodaAnimationProbe/analysis_dependencies')
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP
exe=Path('F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/DisneyInfinity3.exe')
assert hashlib.sha256(exe.read_bytes()).hexdigest()=='f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705'
pe=pefile.PE(str(exe));base=pe.OPTIONAL_HEADER.ImageBase
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image());u.mem_map(0x10000000,0x20000)
source=Path('C:/Users/Kurar/Disney Reloaded/Tools/YodaTimedHeadResearch/decode_timed_curves.py')
t=ast.parse(source.read_text());ns={};exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='sample'],type_ignores=[]),str(source),'exec'),ns)
def native_curve(data,t,dims):
 stack=0x10010000;curve=0x10002000;out=0x10008000;ptr=0x10009000;idx=ptr+16;stop=0x10000100
 assert len(data)<0x6000 and dims*4<0x1000
 u.mem_write(curve,data);u.mem_write(out,b'\0'*(dims*4));u.mem_write(ptr,struct.pack('<I',out));u.mem_write(idx,b'\0'*4);u.mem_write(stack,struct.pack('<IfIII',stop,t,curve,ptr,idx));u.reg_write(UC_X86_REG_ESP,stack)
 u.emu_start(0x522cf0,stop,count=200000)
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise RuntimeError('curve evaluator did not return')
 values=struct.unpack('<'+'f'*dims,u.mem_read(out,4*dims))
 if not all(math.isfinite(x) for x in values):raise ValueError('nonfinite native output')
 return values
rows=[]
for name in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
 b=(ROOT/(name+'.clipdata.bin')).read_bytes();r=json.loads((ROOT/(name+'-decoded-curves.json')).read_text());n=struct.unpack_from('<H',b,10)[0];o=struct.unpack_from('<'+'I'*(n+2),b,12)
 for ci,c in enumerate(r['curves']):
  dims=len(c['metadata']);start=o[ci+2];end=o[ci+3] if ci+3<len(o) else o[0];refs=[i for i,x in enumerate(r['registers']) if x['curve']==ci]
  for fraction in [0,.13,.37,.61,.89,1]:
   time=c['time_start']+(c['time_end']-c['time_start'])*fraction;actual=native_curve(b[start:end],time,dims);expected=[ns['sample'](r,j,time) for j in refs];err=max(abs(a-e) for a,e in zip(actual,expected));rows.append({'clip':name,'curve':ci,'time':time,'components':dims,'max_raw_error':err})
report={'routine':'0x522CF0','exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'case_count':len(rows),'max_raw_error':max(r['max_raw_error'] for r in rows),'cases':rows,'scope':'Native scalar curve evaluation only. Does not validate command flags, graph mapping or full animation.'}
(ROOT/'elsa-native-curve-validation.json').write_text(json.dumps(report,indent=2));print('CASES',len(rows),'MAX_RAW_ERROR',report['max_raw_error'])
