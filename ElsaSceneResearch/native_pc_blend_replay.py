"""Bounded native4e35d0 blend replay with synthetic cached nodes and identity output.
No live memory; no source actor loader. Optional indexed filter/source fixtures preserve explicit packed indices.
"""
import struct,math
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
# Dedicated scratch region: the viewer also loads chain reset at11000000.
BASE=0x32000000;SIZE=0x30000;PROC=BASE+0x1000;OUT=BASE+0x2000;META=BASE+0x3000;TABLE=BASE+0x4000;STACK=BASE+0x18000;STOP=BASE+0x100
u.mem_map(BASE,SIZE)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def fp(a,v):u.mem_write(a,struct.pack('<f',v))
def node(a,values):
 u.mem_write(a,b'\0'*160);put(a+0x10,META);put(a+0x1c,META);u.mem_write(a+0x20,struct.pack('<H',1));u.mem_write(a+0x34,struct.pack('<'+'f'*len(values),*values))
def blend(contributors,build_entries=False,*,scalar=False,previous_output=0.,previous_factor=0.,bypass_fade=True,default_scalar=None,previous_dilation=None,transform=False,previous_transform=None):
 if scalar and transform:raise ValueError('Select one native output type')
 if not 1<=len(contributors)<=8:raise ValueError('requires1..8contributors')
 u.mem_write(BASE,b'\0'*SIZE);u.mem_write(META+0x20,struct.pack('<H',1))
 for a in (0x213e490,0x213e48c):put(a,0)
 for a in (0x213e6f0,0x213e6ec):put(a,0)
 identity=[0,0,0,1,0,0,0,1]+([1.]*8 if transform else []);node(OUT,identity);put(OUT+0x18,PROC)
 if previous_dilation is not None:
  if scalar or transform or len(previous_dilation)!=8 or not all(math.isfinite(v)for v in previous_dilation):raise ValueError('Finite eight-component Dilation prior required')
  u.mem_write(OUT+0x34,struct.pack('<8f',*previous_dilation))
 if previous_transform is not None:
  if not transform or len(previous_transform)!=16 or not all(math.isfinite(v)for v in previous_transform):raise ValueError('Finite sixteen-component Transform prior required')
  u.mem_write(OUT+0x34,struct.pack('<16f',*previous_transform))
 if scalar:fp(OUT+0x34,previous_output)
 # Bypass is explicit; typed prior-output/fade fixtures are optional.
 # Default-network pose is absent unless the scalar fixture below supplies one.
 put(PROC+0x18,0x80000000 if bypass_fade else 0);put(PROC+0x24,TABLE);put(PROC+0x28,0 if build_entries else len(contributors));put(PROC+0x2c,64 if build_entries else 0);put(PROC+0x30,OUT)
 if scalar or transform:fp(PROC+0x34,previous_factor)
 if default_scalar is not None:
  if not scalar or not math.isfinite(default_scalar):raise ValueError('Finite scalar default required')
  default=BASE+0x15000;indices=default+0x100;values=default+0x200
  put(PROC+0x1c,default);put(default+0xc,indices);put(default+0x14,values)
  u.mem_write(indices,struct.pack('<H',16));fp(values+16*4,default_scalar)
 for i,c in enumerate(contributors):
  vals=c['values'];assert len(vals)==16 and all(math.isfinite(v)for v in vals)
  a=BASE+0x5000+i*0x1000;ctrl=a;container=a+0x100;vt=a+0x200;array=a+0x300;inp=a+0x400;weights=a+0x500;wv=a+0x600
  node(inp,vals);put(container,vt);put(vt+4,0x7b2500);put(vt+0x14,0x4b4f00);put(container+0x20,1);put(container+0x1c,array);put(array,inp);put(ctrl+0x18,container)
  source_values=c.get('source_values')
  source_index=c.get('source_index',0);filter_index=c.get('filter_index',0)
  if not isinstance(source_index,int) or not isinstance(filter_index,int) or not 0<=source_index<4096 or not 0<=filter_index<4096:raise ValueError('invalid packed index')
  if source_values is not None:
   if not 1<=len(source_values)<=4 or source_index>=len(source_values):raise ValueError('source fixture bounds')
   put(container+0x20,len(source_values))
   for si,sv in enumerate(source_values):
    if len(sv)!=16 or not all(math.isfinite(v)for v in sv):raise ValueError('invalid source values')
    ptr=a+0xa00+si*0x100;node(ptr,sv);put(array+si*4,ptr)
  elif source_index!=0:raise ValueError('source index requires source array')
  fp(ctrl+0x34,c['priority']);u.mem_write(ctrl+0x39,bytes([c['flag']]))
  filter_values=c.get('filter_values')
  if filter_values is not None:
   if not 1<=len(filter_values)<=1024 or filter_index>=len(filter_values) or not all(math.isfinite(v)for v in filter_values):raise ValueError('filter fixture bounds')
   # Keep full authored arrays separate from the per-contributor scalar nodes.
   if len(filter_values)>64:wv=BASE+0x20000+i*0x1000
   put(ctrl+0x28,weights);put(weights+0x10,wv);u.mem_write(wv,struct.pack('<'+'f'*len(filter_values),*filter_values))
  elif c['weight']is not None:
   if filter_index!=0:raise ValueError('filter index requires filter array')
   put(ctrl+0x28,weights);put(weights+0x10,wv);fp(wv,c['weight'])
  for off,key,ptr in ((0x2c,'factor2c',a+0x700),(0x30,'factor30',a+0x800)):
   if c[key]is not None:node(ptr,[c[key]]);put(ctrl+off,ptr)
  if build_entries:
   put(STACK,STOP);put(STACK+4,ctrl);put(STACK+8,source_index);put(STACK+12,filter_index);u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,PROC);u.emu_start(0x5440c0,STOP,count=100000)
   if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('Native entry builder did not return')
  else:
   put(TABLE+i*8,ctrl);put(TABLE+i*8+4,(c.get('packed',0)&0xff000000)|source_index|(filter_index<<12))
 put(STACK,STOP);u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,PROC)
 try:u.emu_start(0x4e3050 if scalar else (0x4e3fc0 if transform else 0x4e35d0),STOP,count=500000)
 except Exception as e:raise RuntimeError('blend stopped at '+hex(u.reg_read(UC_X86_REG_EIP))+': '+str(e))from e
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('instruction budget/return failure')
 result=list(struct.unpack('<f' if scalar else ('<16f' if transform else '<8f'),u.mem_read(OUT+0x34,4 if scalar else (64 if transform else 32))))
 if not all(math.isfinite(v)for v in result):raise ValueError('nonfinite output')
 return result
