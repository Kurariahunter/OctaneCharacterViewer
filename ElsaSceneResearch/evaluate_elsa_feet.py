"""Opt-in Elsa-only native foot/IK graph research. Does not alter production Eval."""
import numpy as np
from evaluate_elsa_head import Eval,PROD,DN,get,quat,stored
from native_foot_relationship import run as relationship_run
from native_anchor_relationship import run as anchor_run
from native_leg_ik import native_ik

def rotor(m):
 r=np.array(m).T;t=np.trace(r)
 if t>0:
  s=np.sqrt(t+1)*2;q=[(r[2,1]-r[1,2])/s,(r[0,2]-r[2,0])/s,(r[1,0]-r[0,1])/s,.25*s]
 else:
  i=int(np.argmax(np.diag(r)));j=(i+1)%3;k=(i+2)%3;s=np.sqrt(1+r[i,i]-r[j,j]-r[k,k])*2;q=[0.,0.,0.,0.];q[i]=.25*s;q[j]=(r[j,i]+r[i,j])/s;q[k]=(r[k,i]+r[i,k])/s;q[3]=(r[k,j]-r[j,k])/s
 if np.max(abs(quat(q)-m))>1e-5:raise ValueError('rotor reconstruction')
 return q
class FootEval(Eval):
 def __init__(self):super().__init__();self.extra_busy=set()
 def run(self,i):
  if i in self.cache:return self.cache[i]
  prod=PROD.get(i)
  if not prod:return super().run(i)
  p,output=prod;typ=get(p,'Type');pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
  supported={'RelationshipProcessor','IK2BRPLengthSquashZConstraint','TransformPositionWithDilation','TransformDilationWithTransform','ConcatenateInverseTransformDilation','InvertConcatenateChainTransform','InvertConcatenateChainDilation','Position3dOffsetProcessor','FloatNegate','TransformComponentProcessorCompose'}
  if typ not in supported:return super().run(i)
  if i in self.extra_busy:raise ValueError('research graph cycle '+str(i))
  self.extra_busy.add(i)
  try:
   if typ=='RelationshipProcessor':
    if int(p['value']) not in (17,24,34):raise ValueError('unvalidated relationship processor '+str(p['value'])+' output '+str(i))
    rel=dict(pairs)['RelationshipData'];expected=get(DN[23 if int(p['value'])==17 else 39],'RelationshipDataBlock')['hex']
    if get(DN[rel],'RelationshipDataBlock')['hex']!=expected:raise ValueError('different relationship blob')
    ins=[(a,v) for a,v in pairs if a.startswith('Input[')];values=[float(self.run(v)) for a,v in ins]
    if any(abs(v)>100 for v in values):raise ValueError('unvalidated relationship control range')
    out=(anchor_run if int(p['value'])==17 else relationship_run)(values,full=True)['outputs']
    for (a,node),vals in zip([(a,v) for a,v in pairs if a.startswith('Output[')],out):
     m=np.eye(4);m[:3,:3]=quat(vals[:4])*vals[7];m[:3,3]=vals[4:7];self.cache[node]=m
   elif typ=='IK2BRPLengthSquashZConstraint':
    if int(p['value']) not in (408,412):raise ValueError('unvalidated IK processor')
    values=[]
    for a,v in pairs:
     if a.startswith('Output'):continue
     x=self.run(v);kind=get(DN[v],'Type')
     if kind=='Rotor':values.append(rotor(x))
     elif kind=='Float':values.append([float(x)])
     else:values.append(np.array(x).flatten().tolist())
    out=native_ik(values)
    for (a,node),vals in zip([(a,v) for a,v in pairs if a.startswith('Output')],out):self.cache[node]=quat(vals) if get(DN[node],'Type')=='Rotor' else np.array(vals)
   else:
    args={a:self.run(v) for a,v in pairs if not a.startswith('Output') and a!='Aggregate'}
    if typ=='TransformComponentProcessorCompose':
     # Source component attributes may list Scale before Orientation. Apply scale last.
     inputs={a:self.run(v) for a,v in pairs if a!='Aggregate'};m=stored(DN[i]).copy()
     if 'Orientation' in inputs:m[:3,:3]=inputs['Orientation']
     if 'Translation' in inputs:m[:3,3]=inputs['Translation']
     if 'Scale' in inputs:
      scale=np.array(inputs['Scale']);m[:3,:3]*=float(scale) if scale.ndim==0 else scale[:3]
    elif typ=='FloatNegate':m=-args['Input']
    elif typ=='Position3dOffsetProcessor':m=args['Input']+args['Offset']
    elif typ=='TransformPositionWithDilation':m=(args['Converter']@np.r_[args['Input'],1])[:3]
    elif typ=='TransformDilationWithTransform':m=args['Converter']@args['Input']
    elif typ=='ConcatenateInverseTransformDilation':m=np.linalg.inv(args['Right'])@args['Left']
    else:
     m=np.eye(4)
     for a,v in pairs:
      if a.startswith('Output'):continue
      m=m@np.linalg.inv(args[a])
    if not np.all(np.isfinite(m)):raise ValueError('nonfinite extra graph output')
    self.cache[i]=m
   return self.cache[i]
  finally:self.extra_busy.remove(i)
if __name__=='__main__':
 for i in [450,479,707,691,424,430,453,459,435,464]:
  e=FootEval()
  try:print(i,e.run(i))
  except Exception as ex:print('FAIL',i,str(ex))
