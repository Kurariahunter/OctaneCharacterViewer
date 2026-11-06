import json,struct,base64
from pathlib import Path
P=Path(__file__).parent
def source_port_map(tree,endian='>',base_bind_name=None,network_index=None):
 if endian not in ('<','>'):raise ValueError('Invalid source byte order')
 def walk(n):
  yield n
  for c in n['children']:yield from walk(c)
 def get(n,k):return next((c['value']for c in n['children']if c['name']==k),None)
 nets=[n for n in walk(tree)if n['name']=='SubNetwork'and(network_index is None or str(n['value'])==str(network_index))]
 if len(nets)!=1:raise ValueError('Explicit unique source network selection required')
 net=nets[0];nodes={int(n['value']):n for n in walk(net)if n['name']=='DataNode'}
 links=[n for n in walk(net)if n['name']=='BaseDataNodeLinks'and(base_bind_name is None or get(n,'Name')==base_bind_name)]
 if len(links)!=1:raise ValueError('Explicit unique BaseBind name required')
 link=links[0]
 def shorts(x):
  b=base64.b64decode(x);return struct.unpack(endian+str(len(b)//2)+'H',b)
 used=get(net,'ConnectionMapUsedDataNodes');localused=shorts(get(link,'LocalUsedDataNodeIndices'));ports=shorts(get(link,'LocalToPortIndices'));reverse=shorts(get(link,'PortToLocalIndices'))
 if len(localused)!=len(ports)or len(set(localused))!=len(localused)or len(set(ports))!=len(ports):raise ValueError('Invalid local BaseBind map')
 if any(i>=len(used)for i in localused)or any(p>=len(reverse)for p in ports):raise ValueError('BaseBind map index out of range')
 lookup={}
 for local,(slot,port)in enumerate(zip(localused,ports)):
  if reverse[port]!=local or used[slot]not in nodes:raise ValueError('BaseBind reverse map or node mismatch')
  lookup[port]=used[slot]
 if any(v!=65535 and(v>=len(ports)or ports[v]!=p)for p,v in enumerate(reverse)):raise ValueError('Unexpected BaseBind reverse entry')
 # Header paths are source names, not guessed retail bone names.
 layout=get(net,'HeaderLayout');indices=get(net,'HeaderStringIndices');strings=get(net,'HeaderStrings');parents={};cursor=1
 for parent,count in zip(layout[::2],layout[1::2]):
  for i in range(cursor,cursor+count):parents[i]=parent
  cursor+=count
 assert cursor-1==len(indices)
 paths={}
 for i,n in nodes.items():
  h=get(n,'Header');path=[];seen=set()
  while h:
   assert h not in seen;seen.add(h);path.append(strings[indices[h-1]]);h=parents[h]
  paths[i]='|'.join(reversed(path))
 return dict(lookup=lookup,paths=paths,nodes=nodes,template=get(link,'ConnectionTemplate'),name=get(link,'Name'),network_index=net['value'],reverse_extent=len(reverse),sentinels=sum(x==65535 for x in reverse),local_used=list(localused),used_count=len(used))

def read_records(clip_path,tree_path=None,endian='>',command_block_index=None,verbose=True,base_bind_name=None,network_index=None):
 tree=json.loads((Path(tree_path)if tree_path is not None else P/'WiiUClips/fro_elsa.tree.json').read_text(encoding='utf-8'))
 mapping=source_port_map(tree,endian,base_bind_name,network_index);lookup=mapping['lookup'];paths=mapping['paths'];nodes=mapping['nodes']
 def get(n,k):return next((c['value']for c in n['children']if c['name']==k),None)
 if verbose:print('source ports',len(lookup),'reverse extent',mapping['reverse_extent'],'sentinel',mapping['sentinels'])
 from clip_command_blocks import read_command_blocks
 blocks=read_command_blocks(bytes(clip_path)if isinstance(clip_path,(bytes,bytearray))else Path(clip_path).read_bytes(),endian)
 if command_block_index is None:
  if len(blocks)!=1:raise ValueError('Multiple command blocks require explicit connection-template block selection')
  command_block_index=0
 if not isinstance(command_block_index,int)or not 0<=command_block_index<len(blocks):raise ValueError('Invalid command block selection')
 records=[]
 for source in blocks[command_block_index]['records']:
  row=dict(source,source_node=lookup.get(source['port']),path=paths.get(lookup.get(source['port'])),command_block_index=command_block_index)
  for descriptor in row['descriptors']:
   if row['source_node']is not None:
    if descriptor.get('semantics_validated')is False:
     raise ValueError(f"Opcode {descriptor['opcode']} semantics not implemented for used port {row['port']}")
    if descriptor['opcode']in('0x1c','0xc'):
     # Native direct-node opcode C has typed destinations, not Float.
     # Only the authored Bool target is admitted here; visibility and blended
     # output application have separate conversion rules, not assumed here.
     target_type=get(nodes[row['source_node']],'Type')
     if target_type!='Bool':raise ValueError(f"Switch opcode requires validated Bool target, got {target_type}")
  if row['source_node']is not None and any(d['opcode']in('0x1c','0xc')for d in row['descriptors']):
   row['descriptors']=[dict(d,target_type='Bool')if d['opcode']in('0x1c','0xc')else d for d in row['descriptors']]
  records.append(row)
 if records and not any(r['source_node']is not None for r in records):raise ValueError('No clip controls map to the selected source graph; connection-template routing required')
 return records
