"""Source-routed multi-command sampling; no actor scheduling or mesh attachment.

Block-local registers and ports remain separate, even when template names repeat.
Only explicit exact-template bindings may resolve ports into a model network.
"""
from pathlib import Path
import base64,struct,math,hashlib,json,sys
P=Path(__file__).parent
sys.path.insert(0,str(P.parents[1]/'ElsaSceneResearch'))
from native_pc_clip_math import curve,rotation
from inspect_wiiu_clip import inspect
from source_asset_tree import read_tree
from wiiu_port_records import read_records,source_port_map
from clip_layer_binds import read_layer_binds,select_layer_bind

def walk(n):
 yield n
 for c in n['children']:yield from walk(c)

def value(n,key):
 return next((c['value']for c in n['children']if c['name']==key),None)

class RoutedClip:
 def __init__(self,oct_path,clipdata_path=None,endian='<'):
  self.path=Path(oct_path);self.tree=read_tree(self.path);self.endian=endian
  blobs=[base64.b64decode(n['value'])for n in walk(self.tree)if n['name']=='ClipDataBlock']
  if len(blobs)!=1:raise ValueError('Expected one source ClipDataBlock')
  self.b=blobs[0]
  if clipdata_path is not None and Path(clipdata_path).read_bytes()!=self.b:raise ValueError('ClipDataBlock differs from source OCT')
  self.layout=inspect(self.b,[],allowed_boundary_flags=(0,2,0x10,0x12,0x40),endian=endian,allow_constant=True)
  self.lo,self.hi=self.layout['time_range']
  self.layer_binds=read_layer_binds(self.tree,self.layout['command_blocks'])
  self.routes={b['block_index']:b for b in self.layer_binds}
  self.curves=[]
  for row in self.layout['curves']:
   raw=self.b[row['offset']:row['end']];out=bytearray(raw);meta=row['metadata_bytes_per_dimension'];dims=row['dimensions'];n=row['segments'];shorts=row['coefficient_shorts_per_dimension']
   if endian=='>':
    for at in range(0,12+meta*dims,4):out[at:at+4]=raw[at:at+4][::-1]
    for at in range(12+meta*dims,12+meta*dims+2*n+2*shorts*n*dims,2):out[at:at+2]=raw[at:at+2][::-1]
   self.curves.append((bytes(out),dims))
  self.pool=struct.unpack_from(endian+str(self.layout['pool_floats'])+'f',self.b,self.layout['pool_offset'])

 def sample(self,time):
  if not math.isfinite(time)or not self.lo<=time<=self.hi:raise ValueError('Clip time out of range')
  # Evaluate once; each block independently flattens its own curve order.
  sampled=[curve(raw,time,dims)for raw,dims in self.curves];blocks=[]
  for block in self.layout['command_layouts']:
   registers=[v for i in block['timeline_order']for v in sampled[i]]
   if len(registers)!=block['registers']:raise ValueError('Block register extent mismatch')
   ports={}
   for phase in ('static','timed'):
    for record in block['records']:
     if record['phase']!=phase:continue
     channels=ports.setdefault(str(record['port']),{})
     for d in record['descriptors']:
      op=int(d['opcode'],16)
      if phase=='static':channels[str(op)]=dict(values=list(d['values']),kind='source constant')
      elif op&0xf000==0x1000:
       angles=[(registers if(op>>shift)&3 else self.pool)[ref]for ref,shift in zip(d['fields'][1:],(4,2,0))]
       channels['4']=dict(values=angles,derived_quaternion_xyzw=rotation(angles),kind='native Euler conversion')
      else:channels[str(op-16)]=dict(values=[registers[d['fields'][1]]],kind='native curve operand')
      # Switch values stay raw until the destination type/application is known.
      if op in(0xc,0x1c):channels['12']['requires_typed_application']=True
   blocks.append(dict(self.routes[block['index']],ports=ports))
  return dict(time=time,blocks=blocks)

 def sample_for_binding(self,time,template,layer_name=None):
  selected=select_layer_bind(self.layer_binds,template,layer_name)
  # All-block sampling remains an audit operation. Return only the selected
  # entry for a specific playback binding; never sum alternatives by default.
  return next(b for b in self.sample(time)['blocks']if b['block_index']==selected['block_index'])

 def sample_bound_layer(self,time,owner,tree_path,layer_name=None,base_bind_name=None,network_index=None):
  """Bind one explicitly selected layer to one source model owner.
  This is caller selection, not an inferred runtime left/right assignment.
  """
  tree=json.loads(Path(tree_path).read_text(encoding='utf-8'))
  mapping=source_port_map(tree,self.endian,base_bind_name,network_index)
  selected=self.sample_for_binding(time,mapping['template'],layer_name)
  result=self.bind(dict(time=time,blocks=[selected]),{owner:tree_path},base_bind_names={owner:mapping['name']},network_indices={owner:mapping['network_index']})
  result['selection_provenance']='explicit caller-selected layer and model; runtime attachment not inferred'
  return result

 def bind(self,frame,models,base_bind_names=None,network_indices=None):
  """models: explicit owner names -> source tree JSON paths.

  This matches source templates, not filenames or coincident port numbers.
  Unmatched/ambiguous routes remain in diagnostics and are never discarded.
  """
  candidates=[]
  base_bind_names=base_bind_names or {};network_indices=network_indices or {}
  for owner,path in models.items():
   tree=json.loads(Path(path).read_text(encoding='utf-8'))
   mapping=source_port_map(tree,self.endian,base_bind_names.get(owner),network_indices.get(owner))
   candidates.append((owner,path,mapping))
  outputs=[];unresolved=[]
  for block in frame['blocks']:
   matches=[c for c in candidates if c[2]['template']==block['template']]
   if len(matches)!=1:
    unresolved.append(dict(block_index=block['block_index'],name=block['name'],flags=block['flags'],is_additive=block['is_additive'],template=block['template'],ports=block['ports'],reason='no exact template binding'if not matches else'ambiguous template owners'));continue
   owner,path,source_mapping=matches[0]
   records=read_records(self.b,path,endian=self.endian,command_block_index=block['block_index'],verbose=False,base_bind_name=source_mapping['name'],network_index=source_mapping['network_index'])
   mapping={r['port']:r for r in records};ports={};unmapped=[]
   for port,channels in block['ports'].items():
    record=mapping[int(port)]
    if record['source_node']is None:unmapped.append(int(port));continue
    copied={k:dict(c)for k,c in channels.items()}
    if '12'in copied:copied['12'].update(target_type='Bool',direct_node_value=copied['12']['values'][0]>=.5)
    ports[port]=dict(source_node=record['source_node'],path=record['path'],channels=copied)
   outputs.append(dict(block_index=block['block_index'],name=block['name'],flags=block['flags'],is_additive=block['is_additive'],template=block['template'],owner=owner,base_bind_name=source_mapping['name'],network_index=source_mapping['network_index'],ports=ports,unmapped_ports=unmapped))
  return dict(time=frame['time'],bound_blocks=outputs,unresolved_blocks=unresolved,bindings_complete=not unresolved,
              scope='Template-routed controls; separate owners/block outputs, no attachment, controller blending or final mesh pose')
