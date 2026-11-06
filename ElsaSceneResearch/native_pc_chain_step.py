"""Chronological PC dress-chain state. Zero external force; no capsule scene."""
import math,struct
import numpy as np
from native_pc_chain_reset import make,invoke,positions,u,BASE
from evaluate_pc_arms import DN,N,allnodes,get

class ChainStates:
 def __init__(self,mode='full',force=(0,0,0),strict_types=False):
  if mode not in ('full','staged'):raise ValueError('unknown dispatch mode')
  if len(force)!=3 or not all(math.isfinite(v)for v in force):raise ValueError('invalid chain force')
  self.mode=mode;self.states={};self.force=tuple(force);self.strict_types=strict_types
 def step(self,pid,frame,dt,anchor,container,constraint):
  if pid not in (548,550,551) or not math.isfinite(dt) or not 0<dt<=.1:raise ValueError('unsupported PC chain/time')
  if not all(math.isfinite(float(v))for row in [anchor,container,constraint]for v in row):raise ValueError('nonfinite chain input')
  for value in [anchor,container]:
   if len(value)>8 and (max(abs(value[j]-1)for j in [8,9,10,12,13,14,15])>1e-5 or abs(value[11]-value[7])>1e-5):raise ValueError('nonuniform PC chain anchor')
  if pid not in self.states:
   if frame!=0:raise ValueError('chain must begin at frame zero')
   ins,outs=make(anchor[:8],container[:8],orientation=[0,0,0,1],side='Hair'if pid==548 else'Left'if pid==550 else'Right')
   p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid);refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
   # Authored DragCoefficient matches scalar +0x98 in the connected PC capture.
   for slot,key in [(9,'Particle[0]'),(14,'Particle[1]')]:u.mem_write(ins[slot]+0x98,struct.pack('<f',get(DN[refs[key]],'DragCoefficient')))
   if self.strict_types:
    for slot,key in [(9,'Particle[0]'),(14,'Particle[1]')]:
     bind=next(c for c in DN[refs[key]]['children']if c['name']=='BindTransform');fields={c['name']:c['value']for c in bind['children']}
     if bind['value']=='Transform':
      scale=fields.get('Scale',[1]*4);unscale=fields.get('Unscale',[1]*4);raw=fields.get('Orientation',[0,0,0,1])+fields.get('Translation',[0,0,0])+[scale[3]]+scale+unscale;u.mem_write(ins[slot]+0x40,struct.pack('<16f',*raw));u.mem_write(ins[slot]+0x80,struct.pack('<I',2))
   u.mem_write(ins[2]+0x34,struct.pack('<I',0xfffffffe))
   self.states[pid]={'memory':bytes(u.mem_read(BASE,0x20000)),'inputs':ins,'outputs':outs,'q':[0,0,0,1],'last_frame':-1,'length':get(DN[refs['Particle[1]']],'ConstraintLength')}
  state=self.states[pid]
  if frame!=state['last_frame']+1:raise ValueError('nonchronological PC chain sample')
  u.mem_write(BASE,state['memory']);ins=state['inputs'];outs=state['outputs']
  u.mem_write(ins[0]+0x34,struct.pack('<I',frame));u.mem_write(ins[1]+0x34,struct.pack('<f',dt));u.mem_write(ins[5]+0x34,struct.pack('<8f',*anchor[:8]));u.mem_write(ins[6]+0x34,struct.pack('<8f',*container[:8]));u.mem_write(ins[11]+0x34,struct.pack('<3f',*constraint));u.mem_write(BASE+0x4000+21*256+0x34,struct.pack('<4f',*state['q']))
  u.mem_write(ins[3]+0x34,struct.pack('<3f',*self.force))
  # Cached numeric inputs only; native type fixture excludes recursive producers.
  for address in [0x21aee78,0x21aee7c]:u.mem_write(address,struct.pack('<I',0))
  if self.strict_types:
   from native_pc_chain_reset import META
   if len(anchor)!=16:raise ValueError('strict PC anchor requires Transform payload')
   u.mem_write(ins[5]+0x34,struct.pack('<16f',*anchor))
   for address,value in [(0x21aee78,1),(0x21aee7c,0xffffffff),(0x213e48c,2),(0x213e490,0xffffffff),(0x21ae4c8,3),(0x21ae4cc,0xffffffff)]:u.mem_write(address,struct.pack('<I',value))
   for node,tag in [(ins[5],2),(ins[6],1)]:meta=META+tag*16;u.mem_write(meta,struct.pack('<I',tag));u.mem_write(node+0x10,struct.pack('<I',meta))
  if self.mode=='full':invoke(0x4ae360)
  elif frame==0:invoke(0x4acad0)
  else:invoke(0x4acdb0,[struct.unpack('<I',struct.pack('<f',dt))[0]])
  values=np.array(positions(outs));root=float(np.linalg.norm(values[0]-constraint));length=abs(float(np.linalg.norm(values[1]-values[0]))-state['length']*anchor[7])
  if not np.isfinite(values).all()or max(root,length)>2e-5:raise ValueError(('PC temporal invariant',pid,frame,root,length))
  native_frame=struct.unpack('<I',u.mem_read(ins[2]+0x34,4))[0]
  state['memory']=bytes(u.mem_read(BASE,0x20000));state['last_frame']=frame
  return values,{'processor':pid,'root_error':root,'segment_length_error':length,'native_last_frame':native_frame}
 def feedback(self,pid,q):
  if pid not in self.states or not all(math.isfinite(v)for v in q)or abs(sum(v*v for v in q)-1)>1e-5:raise ValueError('invalid PC orientation feedback')
  self.states[pid]['q']=list(q)
