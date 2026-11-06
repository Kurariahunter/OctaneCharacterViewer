"""Serialized LayerBind records, backed by labeled Wii U loader evidence.
Metadata/selection only: does not create runtime target networks or blend poses.
"""

def walk(node):
 yield node
 for child in node['children']:yield from walk(child)

def fields(node):
 result={}
 for child in node['children']:
  if child['name']in result:raise ValueError('Duplicate LayerBind field')
  if child['children']:raise ValueError('Nested LayerBind field not implemented')
  result[child['name']]=child['value']
 return result

def read_layer_binds(tree,command_blocks):
 data_nodes={int(n['value']):n for n in walk(tree)if n['name']=='DataNode'
             and any(c['name']=='Type'and c['value']=='ClipData'for c in n['children'])}
 if len(data_nodes)!=1:raise ValueError('LayerBind loader currently requires one source ClipData node')
 result=[];names=set();blocks=set()
 for node in walk(tree):
  if node['name']!='LayerBind':continue
  f=fields(node);name=f.get('Name','');template=f.get('ConnectionTemplate');block=f.get('ClipDataCommandBlockOffset',0);ref=f.get('ClipDataNodeRef',-1);flags=f.get('Flags',0)
  # Empty is a valid native string-map key (present in townspeople assets).
  if not isinstance(name,str)or name in names:raise ValueError('Invalid/duplicate LayerBind name')
  if not isinstance(template,str)or not template:raise ValueError('Invalid LayerBind template')
  if type(ref)is not int or ref not in data_nodes:raise ValueError('Unresolved LayerBind ClipDataNodeRef')
  if type(block)is not int or not 0<=block<command_blocks or block in blocks:raise ValueError('Invalid/ambiguous LayerBind command block')
  if type(flags)is not int or not 0<=flags<=0xffffffff:raise ValueError('Invalid LayerBind flags')
  if f.get('DriveCommands')or f.get('ProxyCommands'):raise ValueError('LayerBind drive/proxy connections require separate dispatch')
  names.add(name);blocks.add(block)
  result.append(dict(name=name,template=template,block_index=block,clip_data_node=ref,flags=flags,
                     is_additive=bool(flags&1),unsupported_flags=flags&~1,source_fields=f))
 if blocks!=set(range(command_blocks)):raise ValueError('Incomplete source LayerBind routing')
 return result

def select_layer_bind(binds,template,name=None):
 """An explicit name can disambiguate repeated compatible templates.
 Native pool iteration returns its first compatible entry; we do not assume
 serialized/insertion order reproduces the native map iteration order.
 """
 matches=[b for b in binds if b['template']==template and(name is None or b['name']==name)]
 if not matches:raise ValueError('No compatible LayerBind')
 if len(matches)!=1:raise ValueError('Multiple compatible LayerBinds require an explicit layer name')
 selected=matches[0]
 if selected['unsupported_flags']:raise ValueError('Unimplemented LayerBind flags')
 return selected
