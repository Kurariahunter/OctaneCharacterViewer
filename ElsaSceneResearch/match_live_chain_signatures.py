import json,struct
from pathlib import Path
from evaluate_elsa_head import N,DN,get,allnodes
r=Path('F:/DisneyInfinityPortalTest/OctaneLiveInspector');d=json.loads((r/'Captures/octane_20261016_224545_1792205145222838300.json').read_text());out=[]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
for live in d['candidates']:
 matches=[]
 for p in allnodes(N,'ProcessorNode'):
  if get(p,'Type')!='DynamicChain':continue
  refs=dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')));particles=[DN[refs[f'Particle[{i}]']] for i in range(len(live['particles'])) if f'Particle[{i}]' in refs]
  if len(particles)!=len(live['particles']):continue
  ok=True
  for source,actual in zip(particles,live['particles']):
   want=[f32(get(source,k)) for k in ['InverseMass','DampingFactor','NaturalFrequency','ConstraintLength']];got=[actual['scalars_raw5'][i] for i in [0,2,3,4]]
   ok &= want==got and get(source,'ConfigFlags')==actual['flags'] and [f32(v) for v in get(source,'RelativeTarget',[0,0,0])]==actual['relative_target']
  data=DN[refs['ChainData']];want=[get(data,k) for k in ['GlobalDamping','IterationRate']]+get(data,'ContainerExtent')
  ok &= [f32(x) for x in want]==live['chain_parameters_raw5']
  if ok:matches.append({'source_processor':int(p['value']),'source_anchor':refs['AnchorToWorld'],'source_container':refs['Container'],'particle_nodes':[int(x['value']) for x in particles]})
 out.append({'address':live['address'],'source_signature_matches':matches,'world_space_nonzero':any(x!=0 for pos in live['output_positions'] for x in pos)})
print(out)
(r/'live-source-chain-signatures.json').write_text(json.dumps({'scope':'Exact float32 parameter signatures against Elsa source, excluding unresolved slot98. Matching static configuration supports association but is not runtime character ownership proof.','matches':out},indent=2))
