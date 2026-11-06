"""Prepare an explicitly bind-relative diagnostic, not a faithful full animation."""
import json,zipfile,struct,math,hashlib,collections
from pathlib import Path
import numpy as np
from evaluate_elsa_head import T,N,DN,Eval,stored,allnodes,get,quat
ROOT=Path(__file__).parent
rawsamples=json.loads((ROOT/'named-control-samples.json').read_text())['samples']
# Skin palette and topology from the same original model as the motion graph.
geometry=next(n for n in allnodes(T,'Node') if any(c['name']=='Primitives' for c in n['children']))
influences=list(allnodes(geometry,'Influence'));names=[get(x,'Name') for x in influences]
if len(set(names))!=len(names):raise ValueError('ambiguous skin names')
lookup={name:i for i,name in enumerate(names)};basis={int(x['value']):x for x in allnodes(N,'Basis')};byname=collections.defaultdict(list)
for i,n in basis.items():byname[get(n,'Name')].append(i)
worlds=[np.linalg.inv(np.array(get(x,'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T) for x in influences];parents=[];parent_notes=[]
for name in names:
 if len(byname[name])!=1:
  if len(byname[name])>1:raise ValueError('ambiguous source Basis '+name)
  candidate=None
  if name.startswith(('LowerLid','UpperLid','eye','hair')):candidate='Head'
  for side in ('Left','Right'):
   aliases={'Shoulder_OL_'+side:'Shoulder_'+side,'Elbow_OL_'+side:'Elbow_'+side,'Forearm_OL_'+side:'Elbow_'+side,'Thumb2_'+side:'Thumb1_'+side,'Middle2_'+side:'Middle1_'+side,'Index2_'+side:'Index1_'+side}
   candidate=aliases.get(name,candidate)
  if candidate not in lookup:raise ValueError('unsupported preview helper '+name)
  parents.append(lookup[candidate]);parent_notes.append(name+' -> '+candidate+' (preview approximation, no Basis match)');continue
 par=get(basis[byname[name][0]],'ParentRef',-1);seen=set();mapped=-1
 while par>=0:
  if par in seen:raise ValueError('hierarchy cycle')
  seen.add(par);n=basis[par];pname=get(n,'Name')
  if pname in lookup:mapped=lookup[pname];break
  par=get(n,'ParentRef',-1)
 parents.append(mapped)
with zipfile.ZipFile('G:/Downloads/fro_elsa.zip') as z:
 vb=z.read('fro_elsa/fro_elsa_0.vbuf');ib=z.read('fro_elsa/fro_elsa_0.ibuf')
 primitives=list(allnodes(geometry,'Primitive'));positions=None;uvs=None;submeshes=[];weights={};remap=get(geometry,'InfluenceRemapInfluenceRefs');ranges=get(geometry,'InfluenceRemapPrimitiveData')
 for pi,primitive in enumerate(primitives):
  v=get(primitive,'Vdata');ind=get(primitive,'Idata')
  if len(v)!=8 or v[0]!=2 or v[2]!=0 or v[5]!=0 or v[4]!=24 or v[7]!=16:raise ValueError('unexpected historical vertex layout')
  count=v[1]
  if positions is None:
   if v[3]+count*24>len(vb) or v[6]+count*16>len(vb):raise ValueError('stream bounds')
   positions=[list(struct.unpack_from('<3f',vb,v[3]+i*24)) for i in range(count)]
   uvs=[list(struct.unpack_from('<2e',vb,v[3]+i*24+12)) for i in range(count)]
   normals=[list(struct.unpack_from('<3e',vb,v[6]+i*16)) for i in range(count)]
   if any(abs(sum(x*x for x in normal)-1)>.003 for normal in normals):raise ValueError('unexpected source normal length')
  if count!=len(positions) or ind[0]!=0 or ind[2]!=0 or (ind[1]+ind[3])*2>len(ib):raise ValueError('unexpected index layout')
  tri=list(struct.unpack_from('<'+'H'*ind[3],ib,ind[1]*2));start,palette=ranges[2*pi:2*pi+2]
  if any(i>=count for i in tri):raise ValueError('index bounds')
  for vi in set(tri):
   indices=struct.unpack_from('<4B',vb,v[3]+vi*24+16);raw=struct.unpack_from('<4B',vb,v[3]+vi*24+20);total=sum(raw)
   if total!=255:raise ValueError('unexpected weight normalization')
   merged=collections.defaultdict(float)
   for idx,w in zip(indices,raw):
    if not w:continue
    if idx>=palette:raise ValueError('palette bounds')
    mapped=remap[start+idx]
    if not 0<=mapped<len(names):raise ValueError('influence bounds')
    merged[mapped]+=w/total
   candidate=sorted(merged.items())
   if vi in weights and weights[vi]!=candidate:raise ValueError(f'inconsistent palette mapping vertex {vi}, primitive {pi}: {weights[vi]} vs {candidate}, raw {indices} weights {raw}')
   weights[vi]=candidate
  submeshes.append({'name':get(primitive,'MaterialName'),'reference':get(primitive,'MaterialReference'),'triangles':tri})
 if len(weights)!=len(positions):raise ValueError('unreferenced/unweighted vertices')
 mtb=z.read('fro_elsa/fro_elsa.mtb');texids=[];tp=mtb.find(b'TEXB')
 if tp>=0:
  texcount=struct.unpack_from('<I',mtb,tp+12)[0]
  if texcount>256 or tp+20+texcount*12>len(mtb):raise ValueError('texture table bounds')
  texids=[mtb[tp+20+i*12:tp+28+i*12].hex() for i in range(texcount)]
 textures=[]
 for item in z.infolist():
  if item.filename.endswith('.tbody'):
   b=z.read(item)
   if b[:4]==b'DDS ':
    dst=ROOT/'PreviewTextures'/(Path(item.filename).stem+'.dds');dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);textures.append(str(dst))
reflect=np.diag([-1,1,1,1]);bones=[]
for i,name in enumerate(names):bones.append({'name':name,'parent':parents[i],'world':(reflect@worlds[i]@reflect).flatten().tolist()})
flatweights=[]
for i in range(len(positions)):
 pairs=weights[i];flatweights.append({'indices':[x[0] for x in pairs]+[0]*(4-len(pairs)),'values':[x[1] for x in pairs]+[0]*(4-len(pairs))})
# The archived graph defaults do not equal skin bind. Preserve both as evidence.
validation=[];clips=[]
for name,node in [('Head',407),('Neck',398)]:
 i=lookup[name];local=np.linalg.inv(worlds[parents[i]])@worlds[i];e=Eval();actual=e.run(node);saved=stored(DN[node]);validation.append({'bone':name,'skin_bind_vs_graph_default_max_error':float(np.max(np.abs(local-actual))),'evaluated_vs_stored_graph_max_error':float(np.max(np.abs(saved-actual)))})
for left in (False,True):
 defaults=Eval(offset_left=left);rest={name:defaults.run(node) for name,node in [('Head',407),('Neck',398)]}
 for source in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
  rows=[r for r in rawsamples if r['clip']==source];times=sorted(set(r['time'] for r in rows));samples=[]
  for time in times:
   e=Eval(offset_left=left)
   for r in rows:
    if r['time']==time:e.overrides[r['data_node']]={'Orientation':[r['source_qx'],r['source_qy'],r['source_qz'],r['source_qw']]}
   transforms=[]
   for name,node in [('Head',407),('Neck',398)]:
    i=lookup[name];bind=np.linalg.inv(worlds[parents[i]])@worlds[i]
    # Diagnostic right-relative alignment, explicitly not source-exact retargeting.
    m=bind@np.linalg.inv(rest[name])@e.run(node)
    if np.max(np.abs(m[:3,:3].T@m[:3,:3]-np.eye(3)))>1e-5:raise ValueError('nonrigid sample')
    transforms.append({'bone':name,'matrix':(reflect@m@reflect).flatten().tolist()})
   samples.append({'time':time,'transforms':transforms})
  clips.append({'name':source+('_OffsetLeft' if left else '_OffsetRight'),'duration':times[-1],'samples':samples})
model={'scope':'Historical Elsa 24-byte position/skin stream, UV float16x2 at main offset 12; auxiliary float16 normals validated for unit length. Skin palette indices/weights checked.','positions':[x for p in positions for x in [-p[0],p[1],p[2]]],'normals':[x for n in normals for x in [-n[0],n[1],n[2]]],'uvs':[x for u in uvs for x in [u[0],1-u[1]]],'bones':bones,'weights':flatweights,'submeshes':submeshes,'texture_paths':textures,'texture_ids':texids,'parent_notes':parent_notes}
for sub in submeshes:
 for i in range(0,len(sub['triangles']),3):sub['triangles'][i+1],sub['triangles'][i+2]=sub['triangles'][i+2],sub['triangles'][i+1]
(ROOT/'elsa-preview-model.json').write_text(json.dumps(model,separators=(',',':')))
(ROOT/'elsa-preview-animation.json').write_text(json.dumps({'scope':'Bind-relative head/neck diagnostic. Source graph baseline aligned to skin bind; both unverified offset multiplication orders retained. Other controls held at model defaults. Not full original animation.','clips':clips},separators=(',',':')))
(ROOT/'graph-bind-validation.json').write_text(json.dumps(validation,indent=2))
print('VERTICES',len(positions),'BONES',len(bones),'TRIANGLES',sum(len(s['triangles'])//3 for s in submeshes),'CLIPS',len(clips),'TEXTURES',len(textures));print(validation)
