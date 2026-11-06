"""Source Wii U eyelid paths, original-PC math on byte-equivalent relationship.
Stops at head-local outputs; never substitutes the stored unevaluated Head pose.
"""
from pathlib import Path
import json,sys,math
P=Path(__file__).parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from native_pc_relationship import run
from native_pc_head_connections import connect
from native_pc_lean_ik import sha

def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
def get(n,k,default=None):return next((c['value']for c in n['children']if c['name']==k),default)
def refs(n):return dict(zip(get(n,'DataNodeAttributes',[]),get(n,'DataNodeRefs',[])))
r=json.loads((P/'WiiUClips/fro_elsa.tree.json').read_text());net=next(n for n in walk(r)if n['name']=='SubNetwork');nodes={int(n['value']):n for n in walk(net)if n['name']=='DataNode'};processors=[n for n in walk(net)if n['name']=='ProcessorNode'];rel=next(n for n in processors if n['value']=='178');ref=refs(rel)
layout=get(net,'HeaderLayout');indices=get(net,'HeaderStringIndices');strings=get(net,'HeaderStrings');parents={};cursor=1
for parent,count in zip(layout[::2],layout[1::2]):
 for i in range(cursor,cursor+count):parents[i]=parent
 cursor+=count
paths={}
for i,n in nodes.items():
 h=get(n,'Header');parts=[];seen=set()
 while h:
  assert h not in seen;seen.add(h);parts.append(strings[indices[h-1]]);h=parents[h]
 paths[i]='|'.join(reversed(parts))
scene={int(n['value']):n for pool in walk(r)if pool['name']=='SceneTreeNodePool'for n in pool['children']if n['name']=='Node'}
bindings=[]
for a in walk(r):
 if a['name']!='Association'or get(a,'Type')!='SkinInfluence':continue
 ids=[i for i,path in paths.items()if path==get(a,'NodeName')];assert len(ids)==1;matrix=ids[0];assert get(nodes[matrix],'Type')=='Matrix4x4'
 for scene_ref,influence_ref in zip(get(a,'SceneTreeNodeRefs'),get(a,'InfluenceRefs')):
  influences=next(c for c in scene[scene_ref]['children']if c['name']=='Influences')['children'];matches=[n for n in influences if int(n['value'])==influence_ref];assert len(matches)==1
  bindings.append({'bone':get(matches[0],'Name'),'influence':influence_ref,'scene_node':scene_ref,'matrix_node':matrix,'path':paths[matrix]})
assert len(bindings)==64 and len({x['bone']for x in bindings})==64
(P/'wiiu-skin-associations.json').write_text(json.dumps(bindings,indent=2))
blob=(P/'WiiUClips/elsa-eyelids.pc-endian.bin').read_bytes();equivalence=json.loads((P/'eyelid-endian-equivalence.json').read_text());assert equivalence['byte_equal']
frames=json.loads((P/'elsa-control-quaternions.json').read_text())['samples'];results=[]
for frame in frames:
 by_node={v['source_node']:v for v in frame['ports'].values()};values=[by_node[ref[f'Input[{i}]']]['channels']['10']['values'][0]for i in range(4)];outputs=run(blob,values,4);local=[]
 for i,value in enumerate(outputs):
  proxy=ref[f'Output[{i}]'];conversion=[p for p in processors if get(p,'Type')=='TransformDilationWithDilation'and refs(p).get('Input')==proxy];assert len(conversion)==1;cv=refs(conversion[0]);data=next(c for c in nodes[cv['Converter']]['children']if c['name']=='Data');fields={c['name']:c['value']for c in data['children']};assert fields=={'Translation':[0,0,0],'Orientation':[0,0,0,1],'Scale':1}
  connection=[p for p in processors if get(p,'Type')=='DilationOrientationConnection'and refs(p).get('Input')==cv['Output']];assert len(connection)==1;connection=connection[0];cr=refs(connection);assert set(cr)=={'Input','Output'}
  data=next(c for c in nodes[cr['Output']]['children']if c['name']=='Data');initial={c['name']:c['value']for c in data['children']};payload=initial['Orientation']+initial['Translation']+[initial['Scale']]
  transformed=connect(value,[0,0,0,1],payload,False)
  assert all(math.isfinite(x)for x in transformed);assert abs(sum(x*x for x in transformed[:4])-1)<1e-5
  assert max(abs(x-y)for x,y in zip(transformed[4:7],initial['Translation']))<1e-7
  world=[p for p in processors if get(p,'Type')=='TransformDilationWithTransform'and refs(p).get('Input')==cr['Output']];assert len(world)==1;wr=refs(world[0]);assert wr['Converter']==388
  matrix=[p for p in processors if get(p,'Type')=='DilationToMatrix4x4VariantProcessor'and refs(p).get('Input')==wr['Output']];assert len(matrix)==1;mr=refs(matrix[0]);skin=next(b for b in bindings if b['matrix_node']==mr['Output'])
  local.append({'bone':skin['bone'],'proxy_node':proxy,'head_local_node':cr['Output'],'head_local_dilation_xyzw_t_scale':transformed,'head_world_dependency':388,'world_dilation_node':wr['Output'],'matrix_node':mr['Output'],'skin_influence':skin['influence']})
 results.append({'time':frame['time'],'relationship_inputs':values,'outputs':local})
report={'scope':'Historical stored-identity-converter fixture; converter nodes have producers and these are NOT evaluated head-local graph results. See HEAD_WORLD.md. Wii U source binding and explicit three-sample fixture. Byte-equivalent relationship evaluated by original PC native routine; source identity converter verified; original PC orientation-only connection preserves source translation. Stops before unresolved animated Head world388; not a full Wii U palette or viewer playback. Source curve samples retain approximate Python interior timing.','pc_exe_sha256':sha,'source_skin_associations':len(bindings),'samples':results}
(P/'wiiu-eyelid-local-outputs.json').write_text(json.dumps(report,indent=2));print('PASS64source skin associations;12native-evaluated head-local eyelid outputs; Head world dependency explicit')
