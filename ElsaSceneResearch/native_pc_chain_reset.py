"""Bounded two-particle native DynamicChain fixture. Reset only; does not model time stepping, collisions, or full loader state."""
import struct,math,json
from pathlib import Path
import numpy as np
from native_pc_lean_ik import u,sha
from evaluate_pc_arms import DN,get,quat,PROD,N,allnodes
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
BASE=0x11000000;PROC=BASE+0x1000;META=BASE+0x3000;STACK=BASE+0x1e000;STOP=0x10000100
u.mem_map(BASE,0x20000)

def invoke(fn,args=()):
 u.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),STOP,*args));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,PROC)
 try:u.emu_start(fn,STOP,count=2000000)
 except Exception as ex:raise RuntimeError(hex(u.reg_read(UC_X86_REG_EIP))+' '+str(ex))
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('no return')

def make(anchor,container,orientation=None,side="Left"):
 if side not in ('Left','Right','Hair'):raise ValueError('unknown PC dress side')
 processor=next(p for p in allnodes(N,"ProcessorNode")if int(p["value"])==(548 if side=="Hair" else 550 if side=="Left" else 551));refs=dict(zip(get(processor,"DataNodeAttributes"),get(processor,"DataNodeRefs")))
 u.mem_write(BASE,b'\0'*0x20000)
 nodes=[BASE+0x4000+256*i for i in range(22)]
 for n in nodes:
  u.mem_write(n+0x10,struct.pack('<I',META));u.mem_write(n+0x1c,struct.pack('<I',META))
 # Runtime inputs include frame, delta-time, previous frame, external force, source data.
 ins=nodes[:19];outs=nodes[19:21];ins[7]=0;ins[8]=0;ins[10]=0;ins[13]=0;ins[16]=0
 u.mem_write(PROC+0x18,struct.pack('<HBB',0x80,19,2));u.mem_write(PROC+0x80,struct.pack('<21I',*(ins+outs)));u.mem_write(PROC+0x38,struct.pack('<f',1))
 config=DN[refs['ChainData']];u.mem_write(ins[4]+0x34,struct.pack('<5f',get(config,'GlobalDamping'),get(config,'IterationRate'),*get(config,'ContainerExtent')));u.mem_write(ins[5]+0x34,struct.pack('<8f',*anchor));u.mem_write(ins[6]+0x34,struct.pack('<8f',*container))
 for slot,source in [(9,refs['Particle[0]']),(14,refs['Particle[1]'])]:
  n=ins[slot];p=DN[source];bt=next(c for c in p['children'] if c['name']=='BindTransform');fields={c['name']:c['value'] for c in bt['children']}
  q=fields.get('Orientation',[0,0,0,1]);t=fields.get('Translation',[0,0,0]);u.mem_write(n+0x40,struct.pack('<8f',*(q+t+[1])));u.mem_write(n+0x80,struct.pack('<I',1));u.mem_write(n+0x90,struct.pack('<I',get(p,'ConfigFlags')))
  if any(abs(v-1)>1e-6 for key in ['Scale','Unscale'] for v in fields.get(key,[1]*4)):raise ValueError('unsupported particle bind scale')
  if slot==9:root_bind_translation=t
  u.mem_write(n+0x94,struct.pack('<5f',get(p,'InverseMass'),1,get(p,'DampingFactor'),get(p,'NaturalFrequency'),get(p,'ConstraintLength')));u.mem_write(n+0xa8,struct.pack('<3f',*get(p,'RelativeTarget',[0,0,0])))
 # Runtime cached orientation reference (factory resolves literal ^.Orientation).
 if orientation is not None:
  cache=BASE+0x9000;rotation=nodes[21];u.mem_write(cache+8,struct.pack('<I',rotation));u.mem_write(rotation+0x34,struct.pack('<4f',*orientation));u.mem_write(PROC+0x34,struct.pack('<I',0x200));u.mem_write(PROC+0x200,struct.pack('<I',cache))
 # The caller replaces this bind-root default with the source control constraint.
 pos=np.array(anchor[4:7])+quat(anchor[:4])@(np.array(root_bind_translation)*anchor[7]);u.mem_write(ins[11]+0x34,struct.pack('<3f',*pos))
 u.mem_write(0x21aee78,struct.pack('<I',0));u.mem_write(0x21aee7c,struct.pack('<I',0))
 return ins,outs

def positions(outs):return [list(struct.unpack('<3f',u.mem_read(n+0x34,12))) for n in outs]
