"""Validated Wii U CICD/CICDW curves through original PC native helpers.
Explicit source-template graph mapping; unvalidated layouts fail closed.
"""
from pathlib import Path
import struct,json,math,hashlib,sys
P=Path(__file__).parent;sys.path.insert(0,str(P.parents[1]/'ElsaSceneResearch'))
from native_pc_clip_math import curve,rotation
from inspect_wiiu_clip import inspect
from wiiu_port_records import read_records

class WiiUClip:
 def __init__(self,path=None,tree_path=None,endian='>',command_block_index=None):
  self.path=Path(path)if path is not None else P/'WiiUClips/elsa_bm_idle_specific01.oct.clipdata';self.b=self.path.read_bytes();self.sha=hashlib.sha256(self.b).hexdigest()
  if path is None:assert self.sha=='122f5851199b14e14a05a87403c765566dd0873a49570bef872ec1c0f4072e51'
  layout=inspect(self.b,[],allowed_boundary_flags=(0,2,0x10,0x12,0x40),endian=endian,allow_constant=True);self.lo,self.hi=layout['time_range'];self.records=read_records(self.path,tree_path,endian=endian,command_block_index=command_block_index);self.curves=[]
  for row in layout['curves']:
   raw=self.b[row['offset']:row['end']];dims=row['dimensions'];segments=row['segments'];out=bytearray(raw)
   meta=row['metadata_bytes_per_dimension'];shorts=row['coefficient_shorts_per_dimension']
   for at in range(0 if endian=='>'else 12+meta*dims,12+meta*dims,4):out[at:at+4]=raw[at:at+4][::-1]
   stop=12+meta*dims+2*segments+2*shorts*segments*dims
   for at in range(12+meta*dims if endian=='>'else stop,stop,2):out[at:at+2]=raw[at:at+2][::-1]
   self.curves.append((bytes(out),dims))
  self.pool=struct.unpack_from(endian+str(layout['pool_floats'])+'f',self.b,layout['pool_offset'])
  block=layout['command_layouts'][command_block_index if command_block_index is not None else 0]
  all_curves=self.curves;self.curves=[all_curves[i]for i in block['timeline_order']]
  assert sum(d for _,d in self.curves)==block['registers']

 def sample(self,time):
  if not math.isfinite(time)or not self.lo<=time<=self.hi:raise ValueError('Clip time out of range')
  registers=[v for blob,dims in self.curves for v in curve(blob,time,dims)];ports={}
  for phase in ('static','timed'):
   for row in self.records:
    if row['phase']!=phase or row['source_node']is None:continue
    target=ports.setdefault(str(row['port']),{'source_node':row['source_node'],'path':row['path'],'channels':{}})
    for descriptor in row['descriptors']:
     op=int(descriptor['opcode'],16)
     if phase=='static':
      values=list(descriptor['values']);index=descriptor['pool_index'];assert values==list(self.pool[index:index+len(values)]);target['channels'][str(op)]={'kind':'source constant','values':values}
      if op==12:target['channels']['12'].update(target_type='Bool',direct_node_value=values[0]>=.5)
     elif op&0xf000==0x1000:
      assert (op>>6)&7==2;values=[]
      for ref,shift in zip(descriptor['fields'][1:],(4,2,0)):
       flag=(op>>shift)&3;assert flag in (0,1);values.append(registers[ref]if flag else self.pool[ref])
      target['channels']['4']={'kind':'original-PC native Euler conversion on endian-adapted Wii U curves','values':values,'derived_quaternion_xyzw':rotation(values)}
     elif op==0x1c:
      value=registers[descriptor['fields'][1]]
      target['channels']['12']={'kind':'typed switch operand; direct-node conversion only','values':[value],'target_type':'Bool','direct_node_value':value>=.5}
     else:
      assert op in (0x11,0x12,0x13,0x16,0x17,0x18,0x1a)
      target['channels'][str(op-16)]={'kind':'original-PC native curve evaluation','values':[registers[descriptor['fields'][1]]]}
  return {'time':time,'ports':ports}
 def frames(self,hz=30):
  count=round((self.hi-self.lo)*hz)
  return [self.sample(self.lo+(self.hi-self.lo)*i/count)for i in range(count+1)]

if __name__=='__main__':
 clip=WiiUClip();frames=clip.frames();assert len(frames)==153
 (P/'wiiu-native-control-samples.json').write_text(json.dumps({'clipdata_sha256':clip.sha,'scope':'30 Hz explicit source time schedule; original PC native curve and Euler routines on endian-adapted Wii U data. Not Wii U execution or reconstructed actor clock.','samples':frames},separators=(',',':')),encoding='utf-8')
 print('PASS',len(frames),'direct curve-evaluated source-control samples; no pose interpolation')
