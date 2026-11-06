"""File-only installed-PC clip channel reader. No capture files or game process."""
import sys,json,struct,copy,hashlib,math
from pathlib import Path
R=Path(__file__).parent
sys.path.insert(0,str(R.parent/'TupleDecoderResearch'))
from decode_tup_safe import decode as tuple_decode
from pc_clip_decoder import decode,constants,sample as sample_python
from native_pc_clip_math import curve,rotation,sha

def walk(n):
 yield n
 for c in n.get('children',[]):yield from walk(c)
def get(n,key):return next(c['value'] for c in n['children'] if c['name']==key)
def shorts(v):
 b=bytes.fromhex(v['hex'])if isinstance(v,dict)else bytes(v)
 if len(b)%2:raise ValueError('odd mapping table')
 return struct.unpack('<'+'H'*(len(b)//2),b)
def tree(records):
 root={'name':'Root','children':[]};stack=[root]
 for rec in records:
  node=dict(rec,children=[]);stack=stack[:rec['depth']];stack[-1]['children'].append(node);stack.append(node)
 return root
class Rig:
 def __init__(self,model):
  data=Path(model).read_bytes();self.sha=hashlib.sha256(data).hexdigest()
  if self.sha!='38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d':raise ValueError('Only verified installed-PC Elsa model supported')
  self.root=tree(tuple_decode(data)['records']);self.net=next(n for n in walk(self.root)if n['name']=='SubNetwork');self.nodes={int(n['value']):n for n in walk(self.net)if n['name']=='DataNode'};link=next(n for n in walk(self.net)if n['name']=='BaseDataNodeLinks')
  used=get(self.net,'ConnectionMapUsedDataNodes');localused=shorts(get(link,'LocalUsedDataNodeIndices'));ports=shorts(get(link,'LocalToPortIndices'));reverse=shorts(get(link,'PortToLocalIndices'))
  if len(localused)!=len(ports) or sorted(localused)!=list(range(len(used))):raise ValueError('mapping not bijective')
  self.lookup={}
  for local,(slot,port) in enumerate(zip(localused,ports)):
   if reverse[port]!=local:raise ValueError('forward/reverse port mismatch')
   node=used[slot]
   if node not in self.nodes:raise ValueError('unresolved source node')
   self.lookup[port]=node
  self.parents={};cursor=1;layout=get(self.net,'HeaderLayout');indices=get(self.net,'HeaderStringIndices');strings=get(self.net,'HeaderStrings')
  for parent,count in zip(layout[::2],layout[1::2]):
   for i in range(cursor,cursor+count):self.parents[i]=parent
   cursor+=count
  if cursor-1!=len(indices):raise ValueError('header extent')
  self.paths={}
  for i,n in self.nodes.items():
   h=get(n,'Header');pieces=[];seen=set()
   while h:
    if h in seen:raise ValueError('header cycle')
    seen.add(h);pieces.append(strings[indices[h-1]]);h=self.parents[h]
   self.paths[i]='|'.join(reversed(pieces))
class Clip:
 def __init__(self,path,rig):
  self.path=Path(path);self.rig=rig;source=self.path.read_bytes();blocks=[r for r in tuple_decode(source)['records']if r['name']=='ClipDataBlock']
  if len(blocks)!=1:raise ValueError('expected one ClipDataBlock')
  self.b=bytes.fromhex(blocks[0]['value']['hex']);self.layout=decode(self.b);self.constants=constants(self.b,self.layout);self.duration=struct.unpack_from('<f',self.b,4)[0];self.sha=hashlib.sha256(self.b).hexdigest();n=struct.unpack_from('<H',self.b,10)[0];self.offsets=struct.unpack_from('<'+'I'*(n+2),self.b,12);pool=self.layout['float_pool_start'];self.pool=struct.unpack_from('<'+'f'*((len(self.b)-pool)//4),self.b,pool)
  self.unmapped=sorted({c['port'] for c in self.layout['commands']+self.constants['tracks']if c['port']not in rig.lookup})
 def sample(self,time):
  if not math.isfinite(time) or not 0<=time<=self.duration:raise ValueError('sample time outside clip')
  result={};cache={}
  def apply(port,op,vals):
   # Keep channels raw and typed. Static and timed opcodes share component IDs.
   row=result.setdefault(port,{'source_node':self.rig.lookup.get(port),'path':self.rig.paths.get(self.rig.lookup.get(port)),'channels':{}});row['channels'][str(op)]=vals
  for record in self.constants['tracks']:
   for desc in record['descriptors']:apply(record['port'],desc['opcode'],desc['values'])
  def operand(ref,dynamic):
   if not dynamic:
    if not 0<=ref<len(self.pool):raise ValueError('constant operand bounds')
    return self.pool[ref]
   reg=self.layout['registers'][ref];ci=reg['curve']
   if ci not in cache:
    a=self.offsets[ci+2];z=self.offsets[ci+3]if ci+3<len(self.offsets)else self.offsets[0];cache[ci]=curve(self.b[a:z],time,len(self.layout['curves'][ci]['metadata']))
   return cache[ci][reg['component']]
  for record in self.layout['commands']:
   for fields in record['descriptors']:
    op=fields[0]
    if op&0xf000==0x1000:
     if (op>>6)&7!=2:raise ValueError('unsupported Euler convention')
     flags=[(op>>shift)&3 for shift in (4,2,0)]
     if any(f not in (0,1)for f in flags):raise ValueError('unsupported axis source')
     vals=rotation([operand(ref,flag==1)for ref,flag in zip(fields[1:],flags)]);apply(record['port'],4,vals)
    else:apply(record['port'],op-16,[operand(fields[1],True)])
  return result

def main():
 rig=Rig(R/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct');clips=[]
 for name in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
  p=next((R/'InstalledGameAssetCheck/IdleMotions').rglob(name+'.oct'));clip=Clip(p,rig);frames=round(clip.duration*30);samples=[{'time':clip.duration*f/frames,'ports':clip.sample(clip.duration*f/frames)}for f in range(frames+1)]
  clips.append({'name':name,'path':str(p),'clipdata_sha256':clip.sha,'duration':clip.duration,'curves':len(clip.layout['curves']),'registers':len(clip.layout['registers']),'dynamic_records':len(clip.layout['commands']),'constant_records':len(clip.constants['tracks']),'unmapped_ports':clip.unmapped,'samples':samples})
 report={'scope':'File-only verified-PC Elsa packed clip channels. Original scalar curve and Euler routines executed offline. Structural source-port binding, not complete original loader validation. Unmapped template ports explicit; no full rig evaluation, blending, dynamics or Unity AnimationClip export. Raw per-channel values, not merged final transforms.','exe_sha256':sha,'model_sha256':rig.sha,'mapped_model_ports':len(rig.lookup),'clips':clips}
 (R/'pc-file-idle-channels.json').write_text(json.dumps(report,separators=(',',':')));print('MODEL PORTS',len(rig.lookup))
 for c in clips:print({k:v for k,v in c.items()if k!='samples'})
if __name__=='__main__':main()
