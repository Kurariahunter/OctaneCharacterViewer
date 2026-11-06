"""Bounded native recomposition of the PC thigh-to-dress anchor paths.

Only descendants of the two traced thigh aggregates are recomputed. External
branches remain explicitly captured inputs; this is not whole-animation decoding.
"""
import json,struct,math
from pathlib import Path
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
R=Path(__file__).parent
SPECS={'ConcatenateChainDilation':(0x4d1cb0,8),'ConcatenateChainInverseDilation':(0x4d2b00,8),'InvertConcatenateChainDilation':(0x4d2370,8),'InvertDilation':(0x4d19c0,8),'ConcatenateDilationTransform':(0x57cb30,16)}
def raw(n,count):return list(struct.unpack('<'+'f'*count,bytes.fromhex(n['payload_prefix_hex64'])[:count*4]))
def native_array(row,args):
 fn,width=SPECS[row['operation']];proc=0x10001000;meta=0x10003000;stack=0x10010000;stop=0x10000100
 u.mem_write(proc,b'\0'*512);u.mem_write(meta,b'\0'*128)
 count=len(args);nodes=[0x10004000+256*i for i in range(count+1)]
 u.mem_write(proc+0x18,struct.pack('<HBB',0x80,count,1));u.mem_write(proc+0x80,struct.pack('<'+'I'*(count+1),*nodes))
 if row['operation']=='ConcatenateChainInverseDilation':u.mem_write(proc+0x1c,struct.pack('<I',row['normal_input_count_raw']))
 for ptr,values in zip(nodes,args+[raw(row,width)]):
  u.mem_write(ptr,b'\0'*128);u.mem_write(ptr+0x1c,struct.pack('<I',meta));u.mem_write(ptr+0x34,struct.pack('<'+'f'*len(values),*values))
 u.mem_write(stack,struct.pack('<I',stop));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,proc)
 try:u.emu_start(fn,stop,count=300000)
 except Exception as ex:raise RuntimeError(f'{row["operation"]} at {u.reg_read(UC_X86_REG_EIP):x}: {ex}')
 assert u.reg_read(UC_X86_REG_EIP)==stop
 out=list(struct.unpack('<'+'f'*width,u.mem_read(nodes[-1]+0x34,width*4)))
 if not all(math.isfinite(v) for v in out):raise ValueError('Nonfinite native graph output')
 return out
class AnchorGraph:
 def __init__(self,nodes,overrides):self.nodes=nodes;self.overrides=overrides;self.cache={};self.active=set();self.external=set();self.recomputed={};self.local_checks={}
 def depends(self,address,seen=None):
  if address in self.overrides:return True
  seen=set() if seen is None else seen
  if address in seen:return False
  seen.add(address)
  return any(self.depends(x['node'],seen) for x in self.nodes.get(address,{}).get('inputs',[]) if x['node']!='0x0')
 def run(self,address,width=8):
  if address in self.cache:return self.cache[address]
  if address in self.overrides:return self.overrides[address]
  if address in self.active:raise ValueError('Graph cycle')
  node=self.nodes[address]
  if not self.depends(address):self.external.add(address);return raw(node,width)
  self.active.add(address)
  try:
   children=[i['node'] for i in node.get('inputs',[]) if i['node']!='0x0'];op=node.get('operation')
   if op=='VariantAdapter_4dc8c0':
    # Only the observed one-input variant is validated in this path.
    if len(children)!=1 or node['inputs'][0]['node']!=children[0]:raise ValueError('Unsupported variant configuration')
    result=self.run(children[0],8)[:8]
   elif op in SPECS:
    args=[self.run(a,16 if op=='ConcatenateDilationTransform' and i==1 else 8) for i,a in enumerate(children)]
    result=native_array(node,args)
   else:raise ValueError('Unsupported descendant '+str(op)+' at '+address)
   if op=='VariantAdapter_4dc8c0':local=raw(self.nodes[children[0]],8)
   else:local=native_array(node,[raw(self.nodes[a],16 if op=='ConcatenateDilationTransform' and i==1 else 8) for i,a in enumerate(children)])
   self.local_checks[address]={'operation':op,'error':max(abs(a-b) for a,b in zip(local,raw(node,len(local))))}
   self.cache[address]=result;self.recomputed[address]={'operation':op,'values':result,'cached_component_error':max(abs(a-b) for a,b in zip(result,raw(node,len(result))))}
   return result
  finally:self.active.remove(address)
def main():
 cap=R.parent/'OctaneLiveInspector/Captures/octane_20261017_151848_1792264728047355700.json';d=json.loads(cap.read_text());rows=[];local_checks=[]
 for index,s in enumerate(d['samples']):
  nodes=s['upstream']['nodes'];seeds={}
  for a in ['0x1e073118','0x1e073300']:
   node=nodes[a];orientation=node['inputs'][0]['node'];connection=nodes[orientation];qnode=connection['inputs'][0]['node'];bind=raw(node,8)
   seeds[a]=raw(nodes[qnode],4)+bind[4:]
  graph=AnchorGraph(nodes,seeds)
  for root in s['upstream']['roots'][1:]:
   anchor=root['anchor'];out=graph.run(anchor,16);actual=raw(nodes[anchor],16)
   rows.append({'sample':index,'chain':root['chain'],'anchor':anchor,'predicted_transform_raw16':out,'captured_transform_raw16':actual,'max_component_error':max(abs(a-b) for a,b in zip(out,actual))})
  local_checks.extend(dict(sample=index,node=a,**v) for a,v in graph.local_checks.items())
  if index==0:operations={a:v['operation'] for a,v in graph.recomputed.items()};external=sorted(graph.external)
 summary={a:{'samples':sum(r['chain']==a for r in rows),'max_component_error':max(r['max_component_error'] for r in rows if r['chain']==a),'samples_below_1e_5':sum(r['max_component_error']<1e-5 for r in rows if r['chain']==a)} for a in sorted({r['chain'] for r in rows})}
 report={'capture':str(cap),'exe_sha256':sha,'scope':'Native recomposition only of descendants of captured same-graph thigh rotations. Remaining branches are captured external inputs. Uniform and other source transforms preserved from capture; no original clip decode, temporal simulation, or Unity basis conversion. Captures are non-atomic.','seed_nodes':sorted(seeds),'recomputed_operations':operations,'local_operation_checks':local_checks,'local_operation_summary':{op:{'checks':sum(c['operation']==op for c in local_checks),'max_error':max(c['error'] for c in local_checks if c['operation']==op),'checks_below_1e_5':sum(c['operation']==op and c['error']<1e-5 for c in local_checks)} for op in sorted({c['operation'] for c in local_checks})},'external_captured_nodes':external,'summary':summary,'rows':rows}
 (R/'pc-dress-anchor-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'summary':summary,'local_checks':report['local_operation_summary']},indent=2));assert len(rows)==120
if __name__=='__main__':main()
