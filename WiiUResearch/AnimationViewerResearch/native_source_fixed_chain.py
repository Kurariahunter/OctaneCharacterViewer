# INCOMPLETE research probe: dependency evaluation blocked before native witness.
# Not used by any published Ahsoka cache. No hard-chain equivalence result established.
"""Original native reset witness for source two-point hard-constrained chains."""
import struct,numpy as np
from native_pc_chain_reset import make,invoke,positions,u,BASE,META,PROC
from wiiu_pc_graph_adapter import get,refs

def witness(a,p,anchor,container,constraints):
 rr=refs(p);assert len(constraints)==2
 particles=[a.nodes[rr[f'Particle[{k}]']]for k in range(2)];assert all(get(v,'ConfigFlags')==5 for v in particles)
 ins,outs=make(anchor[:8],container[:8],side='Left');ins[16]=BASE+0xa000
 for slot,particle in zip([9,14],particles):
  bind=next(n for n in particle['children']if n['name']=='BindTransform');assert bind['value']=='Dilation';f={c['name']:c['value']for c in bind['children']};data=f.get('Orientation',[0,0,0,1])+f.get('Translation',[0,0,0])+[f.get('Scale',1.)]
  u.mem_write(ins[slot]+0x40,struct.pack('<8f',*data));u.mem_write(ins[slot]+0x80,struct.pack('<I',1));u.mem_write(ins[slot]+0x90,struct.pack('<I',5));u.mem_write(ins[slot]+0x94,struct.pack('<5f',get(particle,'InverseMass'),get(particle,'DragCoefficient'),get(particle,'DampingFactor'),get(particle,'NaturalFrequency'),get(particle,'ConstraintLength')));u.mem_write(ins[slot]+0xa8,struct.pack('<3f',*get(particle,'RelativeTarget',[0,0,0])))
 config=a.nodes[rr['ChainData']];u.mem_write(ins[4]+0x34,struct.pack('<5f',get(config,'GlobalDamping'),get(config,'IterationRate'),*get(config,'ContainerExtent')))
 for slot,target in zip([11,16],constraints):
  u.mem_write(ins[slot]+0x1c,struct.pack('<I',META));u.mem_write(ins[slot]+0x10,struct.pack('<I',META));u.mem_write(ins[slot]+0x34,struct.pack('<3f',*target))
 u.mem_write(PROC+0x80,struct.pack('<21I',*(ins+outs)));invoke(0x4acad0);out=positions(outs);error=float(np.max(abs(np.array(out)-constraints)));return out,error
