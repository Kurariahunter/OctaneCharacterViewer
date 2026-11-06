"""Native-generated paired fixtures plus pairing/output negative cases."""
import copy,json,struct
from pathlib import Path
from native_pc_raw_buffer_blend import replay
from analyze_post_blend_capture import analyze
R=Path(__file__).parent/'ControllerState'
def row(v):return struct.pack('<12fI',v,0,0,0,1,1,1,1,0,0,0,1,1)
def frame(b,ptr):return dict(frame='0x6000000',data=ptr,rows=1,hex52=b.hex())
dst=row(2);src=row(4);result=replay(dst,src,.5,1)
before=dict(event='blend_before',sequence=1,pair_key='fixture',manager='0x5000000',track='0x5300000',stack='0x5400000',depth=1,
    filter='0x00000000',mode=1,weight_hex4=struct.pack('<f',.5).hex(),source_before=frame(src,'0x6100000'),destination_before=frame(dst,'0x6200000'))
after=dict(event='blend_after',sequence=2,before_sequence=1,pair_key='fixture',manager=before['manager'],track=before['track'],
    stack='0x540000C',depth=0,destination_after=frame(result,'0x6200000'))
events=[dict(event='start',schema='di3_post_blend_v1'),before,after]
tests=[]
for case in ('valid','wrong_stack','wrong_destination','altered_output','parent_valid','parent_wrong_side'):
    es=copy.deepcopy(events)
    if case.startswith('parent_'):
        es[0]['schema']='di3_parent_blend_v1';es[1]['event']='right_before';es[2]['event']='right_after'
        for e in es[1:]:e.update(parent='0x5500000',side='right')
        es[1].update(selected_child=before['track'],alpha_hex4=struct.pack('<f',.5).hex(),child_header_hex32=bytes(32).hex())
        if case=='parent_wrong_side':es[2]['side']='left'
    if case=='wrong_stack':es[2]['stack']='0x5400010'
    if case=='wrong_destination':es[2]['destination_after']['data']='0x6300000'
    if case=='altered_output':es[2]['destination_after']['hex52']=row(99).hex()
    p=R/'post-blend-fixture.jsonl';out=R/'post-blend-fixture-result.json'
    p.write_text('\n'.join(json.dumps(e)for e in es));r=analyze(p,out)
    if case in ('valid','parent_valid'):assert r['byte_exact_pairs']==1 and not r['rejected']
    elif case=='altered_output':assert r['checked_pairs']==1 and r['byte_exact_pairs']==0
    else:assert r['rejected'] and r['checked_pairs']==0
    tests.append(dict(case=case,passed=True));p.unlink();out.unlink()
(R/'post-blend-analyzer-validation.json').write_text(json.dumps(dict(tests=tests,scope='Synthetic native-generated fixtures; no live post-blend capture yet.'),indent=2)+'\n')
print(tests)
