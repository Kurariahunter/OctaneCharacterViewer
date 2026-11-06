"""Bounded Elsa head/neck graph evaluator. Fails on unsupported processors."""
import json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent
T=json.loads((ROOT/'elsa-model-graph.json').read_text())
def allnodes(n,name):
 for c in n['children']:
  if c['name']==name:yield c
  yield from allnodes(c,name)
def get(n,k,default=None):return next((c['value'] for c in n['children'] if c['name']==k),default)
N=next(allnodes(T,'SubNetwork'));DN={int(x['value']):x for x in allnodes(N,'DataNode')};PROD={}
for p in allnodes(N,'ProcessorNode'):
 pairs=list(zip(get(p,'DataNodeAttributes',[]),get(p,'DataNodeRefs',[])));typ=get(p,'Type')
 outputs=[(a,v) for a,v in pairs if a.startswith('Output') or (typ=='DynamicChain' and a.startswith('Position[')) or (typ.endswith('ComponentProcessorCompose') and a=='Aggregate') or (typ.endswith('ComponentProcessorDecompose') and a!='Aggregate')]
 for a,v in outputs:
  if v in PROD:raise ValueError('duplicate producer')
  PROD[v]=(p,a)
def quat(q):
 x,y,z,w=q
 if abs(sum(v*v for v in q)-1)>.005:raise ValueError('nonunit stored rotor')
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]).T
def stored(n):
 data=next((c for c in n['children'] if c['name']=='Data'),None);typ=get(n,'Type')
 if typ=='Rotor':return quat(data['value'])
 if typ=='EulerZXY':
  if data is None or data['value']!=[]:raise ValueError('unverified Euler defaults')
  return np.zeros(3)
 if typ in ('Vector','Position','Float','Scale'):return np.array(data['value'])
 fields={c['name']:c['value'] for c in data['children']} if data else {};m=np.eye(4);m[:3,:3]=quat(fields.get('Orientation',[0,0,0,1]));m[:3,3]=fields.get('Translation',[0,0,0]);scale=fields.get('Scale',1);m[:3,:3]*=scale if np.isscalar(scale) else scale[:3];return m
class Eval:
 def __init__(self,offset_left=False):self.cache={};self.overrides={};self.offset_left=offset_left;self.busy=set();self.visited=set()
 def run(self,i):
  if i in self.cache:return self.cache[i]
  if i in self.busy:raise ValueError('graph cycle')
  self.busy.add(i);self.visited.add(i);n=DN[i];producer=PROD.get(i)
  if producer:
   p,output=producer;typ=get(p,'Type');
   if typ.startswith('IK2BRP') or typ in ('RelationshipProcessor','DynamicChain'):raise ValueError('unsupported '+typ+' output '+str(i))
   pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
   if typ.endswith('ComponentProcessorCompose'):
    m=stored(n).copy()
    for a,v in pairs:
     if a=='Aggregate':continue
     value=self.run(v)
     if a in ('X','Y','Z') and m.shape==(3,):m['XYZ'.index(a)]=value
     elif a=='Orientation':m[:3,:3]=value
     elif a=='Translation':m[:3,3]=value
     elif a=='Scale':m[:3,:3]*=value if np.isscalar(value) or value.ndim==0 else value[:3]
     else:raise ValueError('unsupported compose '+a)
   elif typ.endswith('ComponentProcessorDecompose'):
    agg=self.run(dict(pairs)['Aggregate']);rot=agg[:3,:3];scales=np.linalg.norm(rot,axis=0)
    if np.min(scales)<1e-8:raise ValueError('singular decomposition')
    if output=='Orientation':m=rot/scales
    elif output=='Translation':m=agg[:3,3]
    elif output=='Scale':m=scales
    else:raise ValueError('unsupported decomposition '+output)
   else:
    args={a:self.run(v) for a,v in pairs if a!='Output'}
    if typ in ('ConcatenateChainDilation','ConcatenateChainInverseDilation','ConcatenateDilationTransform','ConcatenateTransformDilation','ConcatenateChainTransform'):
     m=np.eye(4)
     for a,v in pairs:
      if a=='Output':continue
      x=args[a];m=(np.linalg.inv(x) if a.startswith('Invert') else x)@m
    elif typ=='TransformDilationWithDilation':m=args['Converter']@args['Input']
    elif typ in ('InvertDilation','InvertTransform'):m=np.linalg.inv(args['Input'])
    elif typ in ('Position3dConnection','UnitRotor3dConnection','Scale3dConnection','FloatConnection'):m=args['Input'].copy()
    elif typ=='EulerZXYToRotorVariantProcessor':
     if np.max(np.abs(args['Input']))>1e-12:raise ValueError('nonzero Euler variant not implemented')
     m=np.eye(3)
    elif typ=='UnitRotor3dOffsetProcessor':m=args['Offset']@args['Input'] if self.offset_left else args['Input']@args['Offset']
    else:raise ValueError('unsupported '+typ+' output '+str(i))
  else:
   m=stored(n).copy()
   if i in self.overrides:
    data=self.overrides[i]
    if 'Value' in data:
     if get(n,'Type')!='Float':raise ValueError('scalar override on non-Float node')
     m=np.array(data['Value'],dtype=float)
    if 'Orientation' in data:m[:3,:3]=quat(data['Orientation'])
    if 'Translation' in data:m[:3,3]=data['Translation']
  if not np.all(np.isfinite(m)):raise ValueError('nonfinite graph result')
  self.busy.remove(i);self.cache[i]=m;return m
if __name__=='__main__':
 worlds={get(x,'Name'):np.linalg.inv(np.array(get(x,'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T) for x in allnodes(T,'Influence')}
 basis={get(x,'Name'):int(x['value']) for x in allnodes(N,'Basis')}
 for name,parent,node in [('Head','Neck',407),('Neck','Spine3',398)]:
  expected=np.linalg.inv(worlds[parent])@worlds[name]
  for left in (False,True):
   e=Eval(offset_left=left)
   try:
    m=e.run(node);print(name,'offset_left',left,'bind_error',np.max(np.abs(m-expected)),'visited',len(e.visited))
   except Exception as ex:print('FAIL',name,str(ex))
