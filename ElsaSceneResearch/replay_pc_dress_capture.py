"""Offline native one-step replay from captured numeric state, never live pointers."""
import json,struct,math
from pathlib import Path
import numpy as np
from native_pc_chain_reset import make,invoke,positions,u,BASE,PROC,META,sha

R=Path(__file__).parent;CAPTURE=R.parent/'OctaneLiveInspector/Captures/octane_20261017_173236_1792272756642966600.json'

def payload(item):
 raw=bytes.fromhex(item['payload_hex']);values=list(struct.unpack('<'+'f'*(len(raw)//4),raw))
 if not all(math.isfinite(v)for v in values):raise ValueError('nonfinite captured payload')
 return values

def replay(a,b,side,orientation='previous',strict_types=True,staged=False,zero_force=False):
 da=a['dynamics'];db=b['dynamics'];sa={v['runtime_slot']:v for v in da['input_states']};sb={v['runtime_slot']:v for v in db['input_states']}
 if any(d['capsules']['count']!=0 for d in [da,db]):raise ValueError('capsules unsupported in replay')
 wa=da['read_window'];wb=db['read_window']
 if wa['stamps_changed']is not False or wb['stamps_changed']is not False or wb['frame_before']-wa['frame_before']!=1 or wb['last_frame_before']-wa['last_frame_before']!=1:raise ValueError('unsupported frame pair')
 for states in [sa,sb]:
  if any(bytes.fromhex(states[8].get('payload_hex')or'')):raise ValueError('nonempty reset event')
 q=payload((da if orientation=='previous'else db)['cached_orientation']['value'])
 ins,outs=make(payload(sa[5])[:8],payload(sa[6])[:8],orientation=q,side=side)
 # Only numeric particle ranges are copied. Headers, type/network/producer refs
 # and unresolved +84..+8f storage never come from the game address space.
 for particle,node in zip(da['particles'],[ins[9],ins[14]]):
  raw=bytes.fromhex(particle['object_prefix_hex180'])
  if len(raw)!=0xb4 or any(raw[0x84:0x90]):raise ValueError('unresolved nonzero particle storage')
  u.mem_write(node+0x34,raw[0x34:0x84]);u.mem_write(node+0x90,raw[0x90:0xb4])
 for slot in [12,17,18]:u.mem_write(ins[slot]+0x34,bytes.fromhex(sa[slot]['payload_hex']))
 for index,node in enumerate(outs):u.mem_write(node+0x34,bytes.fromhex(da['output_states'][index]['payload_hex']))
 for slot in [1,3,4,5,6,11]:u.mem_write(ins[slot]+0x34,bytes.fromhex(sb[slot]['payload_hex']))
 if zero_force:u.mem_write(ins[3]+0x34,struct.pack('<3f',0,0,0))
 u.mem_write(ins[0]+0x34,struct.pack('<I',wb['frame_before']));u.mem_write(ins[2]+0x34,struct.pack('<I',wa['last_frame_before']))
 # This cached scalar is state, not a pointer: previous uniform anchor scale.
 header=bytes.fromhex(da['processor_header_hex']);scale=struct.unpack_from('<f',header,0x38)[0]
 if not math.isfinite(scale)or scale<=0:raise ValueError('invalid cached scale')
 u.mem_write(PROC+0x38,header[0x38:0x3c])
 if strict_types:
  for address,value in [(0x21aee78,1),(0x21aee7c,0xffffffff),(0x213e48c,2),(0x213e490,0xffffffff),(0x21ae4c8,3),(0x21ae4cc,0xffffffff)]:u.mem_write(address,struct.pack('<I',value))
  for node,tag in [(ins[5],2),(ins[6],1)]:
   meta=META+tag*16;u.mem_write(meta,struct.pack('<I',tag));u.mem_write(node+0x10,struct.pack('<I',meta))
 else:
  for address in [0x21aee78,0x21aee7c,0x213e48c,0x213e490]:u.mem_write(address,struct.pack('<I',0))
 if staged:invoke(0x4acdb0,[struct.unpack('<I',bytes.fromhex(sb[1]['payload_hex']))[0]])
 else:invoke(0x4ae360)
 predicted=np.array(positions(outs));expected=np.array([payload(v)for v in db['output_states']]);error=np.linalg.norm(predicted-expected,axis=1)
 velocities=np.array([struct.unpack('<3f',u.mem_read(ins[s]+0x34,12))for s in [12,17]]);wanted=np.array([payload(sb[s])for s in [12,17]])
 prior=np.array([payload(v)for v in da['output_states']])
 return {'root_error':float(error[0]),'tip_error':float(error[1]),'velocity_component_error':float(np.max(abs(velocities-wanted))),'prior_to_next_tip_displacement':float(np.linalg.norm(prior[1]-expected[1])),'predicted':predicted.tolist(),'expected':expected.tolist(),'dt':payload(sb[1])[0]}

def main():
 data=json.loads(CAPTURE.read_text());rows=[]
 if data['identity']['sha256']!=sha:raise ValueError('capture/executable hash mismatch')
 for address,side in [('0x1e07fdd0','Left'),('0x1e07fe74','Right')]:
  frames=[next(c for c in s['chains']if c and c['address']==address)for s in data['samples']]
  for index in range(1,len(frames)):
   a,b=frames[index-1:index+1];wa=a['dynamics']['read_window'];wb=b['dynamics']['read_window']
   if wa['stamps_changed']is not False or wb['stamps_changed']is not False or wb['frame_before']-wa['frame_before']!=1 or wb['last_frame_before']-wa['last_frame_before']!=1:continue
   for orientation,strict,staged,zero in [('previous',True,False,False),('current',True,False,False),('previous',False,False,False),('previous',True,True,False),('previous',True,False,True)]:
    result=replay(a,b,side,orientation,strict,staged,zero);rows.append(dict(chain=address,sample_index=index,orientation=orientation,strict_types=strict,staged=staged,zero_force=zero,**result))
 summaries=[]
 for orientation,strict,staged,zero in [('previous',True,False,False),('current',True,False,False),('previous',False,False,False),('previous',True,True,False),('previous',True,False,True)]:
  group=[r for r in rows if(r['orientation'],r['strict_types'],r['staged'],r['zero_force'])==(orientation,strict,staged,zero)]
  summaries.append({'orientation':orientation,'strict_types':strict,'staged':staged,'zero_force':zero,'cases':len(group),'max_root_error':max(r['root_error']for r in group),'max_tip_error':max(r['tip_error']for r in group),'median_tip_error':float(np.median([r['tip_error']for r in group])),'below_1e_5':sum(r['tip_error']<1e-5 for r in group),'max_velocity_component_error':max(r['velocity_component_error']for r in group),'nonstatic_pairs':sum(r['prior_to_next_tip_displacement']>1e-6 for r in group)})
 if summaries[0]['max_tip_error']!=0 or summaries[0]['max_root_error']!=0 or summaries[0]['max_velocity_component_error']!=0 or summaries[0]['nonstatic_pairs']!=summaries[0]['cases']:raise ValueError('captured-step equivalence failed')
 if summaries[-1]['below_1e_5']!=0:raise ValueError('zero-force ablation unexpectedly matches')
 report={'capture':str(CAPTURE),'exe_sha256':sha,'scope':'Offline original native one-step replay from numeric particle, velocity, output and last-target state. Subsequent inputs from captured next snapshot. All pointers are synthetic; non-atomic snapshot/update-order qualifications remain. Fixed orientation/type/dispatch variants are reported separately, not fitted per sample.','summary':summaries,'rows':rows}
 (R/'pc-captured-dress-step-replay.json').write_text(json.dumps(report,indent=2));print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
