"""Canonical authored-path adapter for comparing Wii U Elsa with the PC evaluator.
No evaluator globals are replaced, and source graph differences stay explicit.
"""
from pathlib import Path
import json,sys,collections,math,base64,struct,hashlib
P=Path(__file__).parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from evaluate_pc_arms import PC_RIG,DN as PC_NODES,PROD as PC_PRODUCERS

def walk(n):
 yield n
 for c in n.get('children',[]):yield from walk(c)
def get(n,k,default=None):return next((c.get('value')for c in n['children']if c['name']==k),default)
def refs(n):return dict(zip(get(n,'DataNodeAttributes',[]),get(n,'DataNodeRefs',[])))
def producer_map(net):
 result={}
 for n in walk(net):
  if n['name']!='ProcessorNode':continue
  typ=get(n,'Type')
  for k,v in refs(n).items():
   if k.startswith('Output')or(typ.endswith('ComponentProcessorCompose')and k=='Aggregate')or(typ.endswith('ComponentProcessorDecompose')and k!='Aggregate')or(typ=='DynamicChain'and k.startswith('Position['))or(typ=='IkLean2LinkProcessor'and k in ('StartOrientation','MidOrientation','Scale')):
    assert v not in result;result[v]=(n,k)
 return result
def close(a,b):
 if isinstance(a,(float,int))and isinstance(b,(float,int)):return math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-6)
 if isinstance(a,list)and isinstance(b,list):return len(a)==len(b)and all(close(x,y)for x,y in zip(a,b))
 if isinstance(a,dict)and isinstance(b,dict):return set(a)==set(b)and all(close(a[k],b[k])for k in a)
 return a==b

def relationship_little(blob):
 out=bytearray(blob);off=0;seen=set()
 def swap(p,n):
  assert 0<=p<=len(blob)-n;out[p:p+n]=blob[p:p+n][::-1]
 while True:
  assert off not in seen;seen.add(off)
  count=struct.unpack_from('>H',blob,off+14)[0];end=off+struct.unpack_from('>I',blob,off+16)[0];cmd=off+struct.unpack_from('>I',blob,off+20)[0]
  ptrs=[off+v for v in struct.unpack_from('>'+str(count)+'I',blob,off+24)]+[end]
  assert 0<=cmd<=ptrs[0]<=end<=len(blob)
  for at in range(off,off+12,4):swap(at,4)
  for at in range(off+12,off+16,2):swap(at,2)
  for at in range(off+16,off+24+4*count,4):swap(at,4)
  for at in range(cmd,ptrs[0],2):swap(at,2)
  for a,z in zip(ptrs,ptrs[1:]):
   word=struct.unpack_from('>I',blob,a+4)[0];dims=(word>>9)&2047;segments=word>>20
   for at in range(a,a+16+16*dims,4):swap(at,4)
   stop=a+16+16*dims+2*segments+8*segments*dims
   for at in range(a+16+16*dims,stop,2):swap(at,2)
   assert (stop+3)&~3==z
  nxt=struct.unpack_from('>I',blob,off+8)[0]
  if not nxt:break
  off=nxt
 return bytes(out)

class Adapter:
 def __init__(self):
  self.tree=json.loads((P/'WiiUClips/fro_elsa.tree.json').read_text());self.net=next(n for n in walk(self.tree)if n['name']=='SubNetwork')
  self.nodes={int(n['value']):n for n in walk(self.net)if n['name']=='DataNode'};self.producers=producer_map(self.net)
  parents={};cursor=1;layout=get(self.net,'HeaderLayout');indices=get(self.net,'HeaderStringIndices');strings=get(self.net,'HeaderStrings')
  for parent,count in zip(layout[::2],layout[1::2]):
   for i in range(cursor,cursor+count):parents[i]=parent
   cursor+=count
  assert cursor-1==len(indices);self.paths={}
  for i,n in self.nodes.items():
   header=get(n,'Header');parts=[];seen=set()
   while header:
    assert header not in seen;seen.add(header);parts.append(strings[indices[header-1]]);header=parents[header]
   self.paths[i]='|'.join(reversed(parts))
  wc=collections.Counter(self.paths.values());pc=collections.Counter(PC_RIG.paths.values());pc_by_path={p:i for i,p in PC_RIG.paths.items()if pc[p]==1}
  self.mapping={i:pc_by_path[path]for i,path in self.paths.items()if wc[path]==pc[path]==1}
  self.pc_producers=producer_map(PC_RIG.net)
 def signature(self,producer,paths):
  if producer is None:return None
  n,attr=producer
  return {'type':get(n,'Type'),'output_attribute':attr,'references':{k:paths[v]for k,v in refs(n).items()},'configuration':{c['name']:c.get('value')for c in n['children']if c['name']not in ('Type','Header','DataNodeAttributes','DataNodeRefs')}}
 def audit(self):
  rows=[]
  for source,target in self.mapping.items():
   w,p=self.nodes[source],PC_NODES[target]
   ws=self.signature(self.producers.get(source),self.paths);ps=self.signature(self.pc_producers.get(target),PC_RIG.paths)
   wf=next((c for c in w['children']if c['name']=='Data'),None);pf=next((c for c in p['children']if c['name']=='Data'),None)
   def data(n):return {c['name']:c.get('value')for c in n['children']}if n and n['children']else n.get('value')if n else None
   binary=None
   if get(w,'RelationshipDataBlock')is not None:
    converted=relationship_little(base64.b64decode(get(w,'RelationshipDataBlock')));pc_blob=get(p,'RelationshipDataBlock');pc_blob=bytes.fromhex(pc_blob['hex'])if isinstance(pc_blob,dict)else bytes(pc_blob)
    binary={'byte_equal':converted==pc_blob,'bytes':len(converted),'transcoded_sha256':hashlib.sha256(converted).hexdigest(),'pc_sha256':hashlib.sha256(pc_blob).hexdigest()}
   rows.append({'source_node':source,'pc_node':target,'path':self.paths[source],'same_type':get(w,'Type')==get(p,'Type'),'processor_equivalent':ws==ps,'stored_data_equivalent':close(data(wf),data(pf)),'relationship_equivalence':binary,'wiiu_producer':ws if ws!=ps else None,'pc_producer':ps if ws!=ps else None})
  return {'scope':'Unique authored-path mapping with processor reference/configuration comparison and stored Data tolerance 1e-6. RelationshipDataBlock binary equivalence is not covered by numeric Data comparison. No PC graph substitution or Wii U execution claim.','wiiu_nodes':len(self.nodes),'pc_nodes':len(PC_NODES),'mapped_nodes':len(self.mapping),'processor_equivalent':sum(r['processor_equivalent']for r in rows),'stored_data_equivalent':sum(r['stored_data_equivalent']for r in rows),'unmapped_wiiu':[{'node':i,'path':p}for i,p in self.paths.items()if i not in self.mapping],'rows':rows}
 def controls(self,frame):
  result={};self.skipped_controls=[]
  for port,row in frame['ports'].items():
   source=row['source_node'];assert source in self.mapping,'Unmapped source control'
   target=self.mapping[source]
   if source in self.producers or target in self.pc_producers:
    self.skipped_controls.append({'port':port,'source_node':source,'pc_node':target,'reason':'computed output; matches existing PC apply policy'});continue
   assert get(self.nodes[source],'Type')==get(PC_NODES[target],'Type')
   channels={}
   for op,c in row['channels'].items():
    values=c.get('derived_quaternion_xyzw',c['values']);assert all(math.isfinite(v)for v in values)
    if op=='4':assert len(values)==4,'Euler quaternion not resolved'
    channels[op]=values
   result[int(port)]={'source_node':target,'path':self.paths[source],'channels':channels}
  return result

if __name__=='__main__':
 adapter=Adapter();report=adapter.audit();frames=json.loads((P/'elsa-control-quaternions.json').read_text())['samples']
 controls=[]
 for frame in frames:
  ports=adapter.controls(frame);controls.append({'time':frame['time'],'ports':ports,'skipped':adapter.skipped_controls})
 (P/'wiiu-pc-graph-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 (P/'wiiu-controls-pc-canonical.json').write_text(json.dumps({'scope':'Wii U source controls mapped by authored path into PC canonical node IDs; no animation evaluation or graph substitution.','samples':controls},indent=2),encoding='utf-8')
 print({k:v for k,v in report.items()if k not in ('rows','unmapped_wiiu','scope')});print('Mapped',len(controls),'control snapshots')
