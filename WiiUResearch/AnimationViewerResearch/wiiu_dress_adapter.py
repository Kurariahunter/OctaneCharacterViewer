"""Source dress routing with validated PC chain parameters and chronological state."""
from wiiu_leg_adapter import SourceLegEval
from wiiu_pc_graph_adapter import get,refs,close,PC_NODES
from native_pc_chain_step import ChainStates
from native_pc_dress_math import aim,inverse_vector
from native_pc_transform_scale import point

class DressStates:
 def __init__(self,adapter):
  self.native=ChainStates(force=[0.,-9.8100004196167,0.],strict_types=True);self.mapping={550:548,552:550,553:551};self.evidence=[]
  seen=set()
  def clean(n):return {'value':n.get('value'),'children':{c['name']:clean(c)for c in n['children']if c['name']!='Header'}}
  for p,attribute in adapter.producers.values():
   pid=int(p['value'])
   if pid not in self.mapping or pid in seen:continue
   seen.add(pid);rr=refs(p)
   for name in ('Particle[0]','Particle[1]','ChainData'):
    source=rr[name];target=adapter.mapping[source];w=clean(adapter.nodes[source]);pc=clean(PC_NODES[target]);w['value']=pc['value']=None
    assert close(w,pc),'Different source chain parameters '+name
    self.evidence.append({'processor':pid,'pc_chain':self.mapping[pid],'source_node':source,'pc_node':target,'parameter_role':name,'equivalent':True})
  assert len(self.evidence)==9

class SourceDressEval(SourceLegEval):
 def __init__(self,adapter,audit,pc,states,frame,dt):
  super().__init__(adapter,audit,pc);self.states=states;self.frame=frame;self.dt=dt;self.chain_checks=[]
 def run(self,i):
  if i in self.cache:return self.cache[i]
  producer=self.a.producers.get(i)
  if producer:
   p,attribute=producer;pt=get(p,'Type');rr=refs(p);pid=int(p['value'])
   if pt=='DynamicChain':
    if pid not in self.states.mapping:raise ValueError('Source chain not adapted '+str(pid))
    anchor=self.run(rr['AnchorToWorld']);container=self.run(rr['Container']);constraint=self.run(rr['ConstraintPoint[0]'])
    values,check=self.states.native.step(self.states.mapping[pid],self.frame,self.dt,anchor,container,constraint)
    for node,value in zip((rr['Position[0]'],rr['Position[1]']),values):self.cache[node]=value.tolist()
    self.chain_checks.append({'source_processor':pid,**check});return self.cache[i]
   if pt=='AimConstraintProcessorNode'and i in (669,687,703):
    args=[self.run(rr[k])for k in ('AlignInput','AlignReference','UpInput','UpReference')]
    chain={669:548,687:550,703:551}[i];q=aim(*args,initial=self.states.native.states[chain]['q'])
    self.states.native.feedback(chain,q);self.cache[i]=q;return q
   if pt=='InverseTransformVectorWithTransform':
    value=inverse_vector(self.run(rr['Input']),self.run(rr['Converter']));self.cache[i]=value;return value
   if pt=='TransformPositionWithTransform':
    value=point(self.run(rr['Converter']),self.run(rr['Input'])).tolist();self.cache[i]=value;return value
  return super().run(i)
