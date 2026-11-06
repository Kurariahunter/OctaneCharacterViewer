"""Original executable default-table readers, isolated without runtime blending."""
import json,struct,random
from pathlib import Path
import numpy as np
from evaluate_elsa_head import N,DN,get,stored,quat
from native_leg_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_XMM0
R=Path(__file__).parent
OBJ=0x10006000;OUT=0x10007000;POOL=0x10008000;INDEX=0x10009000;STACK=0x10018000;STOP=0x10000100

def read_transform(words,pool,slot):
 u.mem_write(OBJ,b'\0'*64);u.mem_write(OBJ+12,struct.pack('<I',INDEX));u.mem_write(OBJ+20,struct.pack('<I',POOL));u.mem_write(INDEX,struct.pack('<'+'H'*len(words),*words));u.mem_write(POOL,struct.pack('<'+'f'*len(pool),*pool));u.mem_write(OUT,b'\xcc'*64)
 u.mem_write(STACK,struct.pack('<III',STOP,OUT,slot&0xffffffff));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,OBJ);u.emu_start(0x4b23d0,STOP,count=1000)
 return list(struct.unpack('<16f',u.mem_read(OUT,64)))

def read_scalar(words,pool,slot):
 # Isolate the unmodified table-lookup basic block, before weight multiplication.
 u.mem_write(OBJ+12,struct.pack('<I',INDEX));u.mem_write(OBJ+20,struct.pack('<I',POOL));u.mem_write(INDEX,struct.pack('<'+'H'*len(words),*words));u.mem_write(POOL,struct.pack('<'+'f'*len(pool),*pool));u.reg_write(UC_X86_REG_EAX,slot);u.reg_write(UC_X86_REG_EDX,OBJ);u.emu_start(0x4e33d0,0x4e33f0,count=100)
 raw=int(u.reg_read(UC_X86_REG_XMM0)).to_bytes(16,'little');return struct.unpack('<f',raw[:4])[0]

rng=random.Random(20261016);errors=[]
for case in range(100):
 pool=[rng.uniform(-4,4) for _ in range(48)];offset=rng.randrange(0,32);flag=rng.randrange(8)<<13;words=[flag|offset]
 actual=read_transform(words,pool,0);expected=list(struct.unpack('<16f',struct.pack('<16f',*pool[offset:offset+16])));assert actual==expected
 value=read_scalar(words,pool,0);want=struct.unpack('<f',struct.pack('<f',pool[offset]))[0];assert value==want
 errors.append({'word':hex(words[0]),'offset':offset,'transform_exact':True,'scalar_exact':True})
words=list(struct.unpack('<90H',bytes(get(N,'DefaultDataIndices'))));pool=list(struct.unpack('<17f',bytes(get(N,'DefaultData'))));used=get(N,'ConnectionMapUsedDataNodes');rows=[]
for slot,node in enumerate(used):
 typ=get(DN[node],'Type');old=stored(DN[node]);offset=words[slot]&8191
 if typ=='Float':
  value=read_scalar(words,pool,slot);err=abs(float(old)-value)
 else:
  assert typ in ['Transform','Dilation'],typ
  raw=read_transform(words,pool,slot);m=np.eye(4);m[:3,:3]=quat(raw[:4])*raw[7];m[:3,3]=raw[4:7]
  # Elsa table is identity: scale/unscale must corroborate before matrix comparison.
  assert raw[8:]==[1.0]*8
  err=float(np.max(abs(m-old)));value=raw
 assert err<1e-7,(node,err)
 rows.append({'slot':slot,'node':node,'type':typ,'word':hex(words[slot]),'offset_floats':offset,'default':value,'stored_error':err})
report={'exe_sha256':sha,'scope':'Native table lookup only. Transform64-byte getter and scalar lookup basic block. High-bit runtime component participation, active channel selection and blend weighting remain unvalidated. Reading a Dilation uses the common identity record; no universal Dilation getter claim.','object_layout':{'indices_ptr':12,'index_count':16,'float_pool_ptr':20,'float_count':24},'loader_copy':'0x4b41d0 stores ushort table and float pool counts, called by0x5012b5; association to named properties corroborated structurally, property-hash names not independently decoded.','transform_getter':'0x4b23d0','scalar_basic_block':['0x4e33d0','0x4e33f0'],'formula':'pool[packed_word & 0x1fff]; byte address=pool_base+4*offset','random_cases':errors,'elsa_rows':rows,'max_default_vs_stored_error':max(x['stored_error'] for x in rows)}
(R/'native-channel-default-validation.json').write_text(json.dumps(report,indent=2));print('PASS',len(errors),'random transform+scalar pairs;',len(rows),'Elsa slots; max error',report['max_default_vs_stored_error'])
