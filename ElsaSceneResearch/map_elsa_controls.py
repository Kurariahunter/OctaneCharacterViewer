import sys,zipfile,json,struct
from pathlib import Path
sys.path.insert(0,'F:/DisneyInfinityPortalTest/TupleDecoderResearch')
from decode_tup_safe import decode
ROOT=Path(__file__).parent
with zipfile.ZipFile('G:/Downloads/fro_elsa.zip') as z:doc=decode(z.read('fro_elsa/fro_elsa.oct'))
root={'name':'Root','value':None,'children':[]};stack=[root]
for r in doc['records']:
 n={'name':r['name'],'value':r['value'],'children':[]};depth=r['depth'];stack=stack[:depth];stack[-1]['children'].append(n);stack.append(n)
def allnodes(n,name):
 for c in n['children']:
  if c['name']==name:yield c
  yield from allnodes(c,name)
def get(n,name,default=None):return next((c['value'] for c in n['children'] if c['name']==name),default)
def shorts(value):
 if isinstance(value,dict):raw=bytes.fromhex(value['hex'])
 else:raw=bytes(value)
 if len(raw)%2:raise ValueError('odd table')
 return list(struct.unpack('<'+'H'*(len(raw)//2),raw))
net=next(allnodes(root,'SubNetwork'));used=get(net,'ConnectionMapUsedDataNodes');nodes={int(n['value']):n for n in allnodes(net,'DataNode')};basis={int(n['value']):get(n,'Name') for n in allnodes(net,'Basis')}
link=next(allnodes(net,'BaseDataNodeLinks'))
links=get(link,'DataNodeLinks');print('USED',len(used),'LINKS',len(links),'MAX',max(x for x in links if x!=255))
ports=[i for i,x in enumerate(links) if x!=255];local=[links[i] for i in ports];reverse=links
print('LINKED_PORTS',len(ports),'UNIQUE_SLOTS',len(set(local)))
labels=get(net,'HeaderStrings');indices=get(net,'HeaderStringIndices');rows=[]
for slot,port in zip(local,ports):
 if slot>=len(used) or used[slot] not in nodes or port>=len(reverse):raise ValueError('bad mapping')
 node=nodes[used[slot]];header=get(node,'Header');h=header-1 if isinstance(header,int) else -1
 row={'mapping_hypothesis':'DataNodeLinks[port] indexes ConnectionMapUsedDataNodes; not runtime-validated','port':port,'used_slot':slot,'data_node':used[slot],'type':get(node,'Type'),'basis':basis.get(get(node,'BasisRef')),'header_reference':header,'header_name':labels[indices[h]] if 0<=h<len(indices) and 0<=indices[h]<len(labels) else None,'link_byte':links[port]}
 rows.append(row)
lookup={r['port']:r for r in rows}
report=json.loads((ROOT/'timed-curve-comparison.json').read_text());clips=[]
for clip in report['results']:
 if 'idle' not in clip['file'] or 'commands' not in clip:continue
 mapped=[]
 for cmd in clip['commands']:mapped.append(dict(cmd,model_control=lookup.get(cmd['port'])))
 clips.append({'file':clip['file'],'status':clip['status'],'commands':mapped,'unmapped_ports':[c['port'] for c in mapped if c['model_control'] is None]})
(ROOT/'elsa-control-mapping.json').write_text(json.dumps({'scope':'Source graph port mapping, not final skin-bone animation. Header names use source Header-1 indirection as in eye decoder.','rows':rows,'idle_clips':clips},indent=2))
(ROOT/'elsa-model-graph.json').write_text(json.dumps(root))
assert sorted(local)==list(range(len(used)));print('MAPPED_MODEL_PORTS',len(rows),'LINK_TABLE_IS_BIJECTION',True)
print('IDLE_COMMANDS',sum(len(c['commands']) for c in clips),'UNMAPPED',sum(len(c['unmapped_ports']) for c in clips))
