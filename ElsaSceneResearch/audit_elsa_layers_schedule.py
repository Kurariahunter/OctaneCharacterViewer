"""Source BENT inventory and static dependency-cycle audit; not a runtime scheduler."""
import sys,json,zipfile,hashlib
from pathlib import Path
sys.path.insert(0,'F:/DisneyInfinityPortalTest/TupleDecoderResearch')
from decode_tup_safe import decode
from evaluate_elsa_head import N,DN,PROD,get,allnodes
from decode_header_paths import paths
R=Path(__file__).parent
with zipfile.ZipFile('G:/Downloads/fro_elsa.zip') as z:raw=z.read('fro_elsa/fro_elsa.bent')
doc=decode(raw);assert doc['bytes_consumed']==len(raw)
root={'name':'Root','value':None,'children':[]};stack=[root]
for x in doc['records']:
 assert 1<=x['depth']<=len(stack)
 n=dict(x,children=[]);stack=stack[:x['depth']];stack[-1]['children'].append(n);stack.append(n)
def walk(n,anc=()):
 yield n,anc
 for c in n['children']:yield from walk(c,anc+(n,))
channels=[];bases=[];files=[]
for n,anc in walk(root):
 if n['name']=='Channel' and anc[-1]['name']=='Channels':channels.append(n)
 if n['name']=='Base':bases.append(n)
 if n['name']=='File' and anc[-1]['name']=='Files':
  fs=next(p['value'] for p in reversed(anc) if p['name']=='FileSet')
  files.append({'file_set':fs,'key':n['value'],'offset':n['offset'],'fields':n['children']})
stances=[f for f in files if f['file_set']=='Core:BaseMobility' and f['key'] in ['STANCE','STANCE_PASSIVE','STANCE_ACTIVE2PASSIVE']]
assert len(stances)==3
for s in stances:assert not any(c['name'] in ['Layers','Filter'] for c in s['fields'])
processors={int(p['value']):p for p in allnodes(N,'ProcessorNode')};deps={i:set() for i in processors};edges=[]
for i,p in processors.items():
 for attr,node in zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')):
  producer=PROD.get(node)
  if producer and producer[0] is not p:
   before=int(producer[0]['value']);deps[i].add(before);edges.append({'before':before,'after':i,'node':node,'attribute':attr,'kind':'explicit'})
def components(graph):
 index={};low={};stack=[];on=set();out=[]
 def visit(i):
  index[i]=low[i]=len(index);stack.append(i);on.add(i)
  for j in graph[i]:
   if j not in index:visit(j);low[i]=min(low[i],low[j])
   elif j in on:low[i]=min(low[i],index[j])
  if low[i]==index[i]:
   c=[]
   while True:
    j=stack.pop();on.remove(j);c.append(j)
    if j==i:break
   if len(c)>1 or i in graph[i]:out.append(sorted(c))
 for i in graph:
  if i not in index:visit(i)
 return out
def ancestors(i,graph):
 seen=set();todo=[i]
 while todo:
  j=todo.pop()
  if j in seen:continue
  seen.add(j);todo.extend(graph[j])
 return seen
explicit_cycles=components(deps);augmented={i:set(v) for i,v in deps.items()};implicit=[]
for chain,node in [(583,708),(585,724),(587,739)]:
 if chain==583:continue # Hair resolver target not independently confirmed in this audit.
 p=PROD[node][0];before=int(p['value']);augmented[chain].add(before);implicit.append({'before':before,'after':chain,'node':node,'path':paths[node],'kind':'cached sibling orientation; factory helper evidence, not DataNodeRefs'})
augcycles=components(augmented);upper={i:ancestors(int(PROD[i][0]['value']),deps) for i in [650,655]}
assert not any(get(processors[j],'Type')=='DynamicChain' for a in upper.values() for j in a)
assert all(not(set(c)&a) for c in augcycles for a in upper.values())
report={'scope':'Serialized source declarations and static producer dependencies only. No runtime active-channel selection, blend semantics, solver scheduling or name-resolver execution.','source_sha256':hashlib.sha256(raw).hexdigest(),'bent_bytes':len(raw),'record_count':len(doc['records']),'channels':channels,'bases':bases,'file_count':len(files),'files':files,'stance_entries':stances,'processor_count':len(processors),'explicit_edges':edges,'explicit_cycles':explicit_cycles,'cached_orientation_edges':implicit,'cycles_with_cached_references':augcycles,'upper_dress_processor_ancestors':{str(i):sorted(a) for i,a in upper.items()},'cycle_details':[[{'processor':i,'type':get(processors[i],'Type')} for i in c] for c in augcycles],'next_boundary':'Trace connection-map DefaultData loading and runtime channel defaults before assuming stored DataNode values are the correct untouched animation inputs. Dynamic orientation feedback cycles require original frame/update scheduling, but have no explicit upstream route to UpperDress650/655.'}
(R/'elsa-layer-schedule-audit.json').write_text(json.dumps(report,indent=2))
print('BENT',len(channels),'channels',len(bases),'bases',len(files),'file entries');print('GRAPH',len(processors),'processors',len(edges),'edges','explicit_cycles',explicit_cycles);print('CACHED CYCLES',report['cycle_details']);print('UPPER ANCESTORS',{i:len(a) for i,a in upper.items()})
