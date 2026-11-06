"""Replay paired null-filter native group dispatches using captured raw rows."""
import hashlib,json,math,struct,sys
from pathlib import Path
from native_pc_raw_buffer_blend import replay,sha

def analyze(path,output):
    path=Path(path);raw=path.read_bytes();es=[json.loads(l)for l in raw.decode('utf-8').splitlines()]
    assert es[0]['schema'] in ('di3_post_blend_v1','di3_parent_blend_v1')
    parent_mode=es[0]['schema']=='di3_parent_blend_v1'
    pending={};checks=[];rejected=[]
    def data(frame):
        b=bytes.fromhex(frame['hex52']);assert len(b)==52*frame['rows'] and 0<frame['rows']<=256
        return b
    for e in es:
        if e['event'] in ('blend_before','left_before','right_before'):
            key=e['pair_key']
            if key in pending:raise ValueError('Ambiguous repeated entry')
            pending[key]=e
        elif e['event'] in ('blend_after','left_after','right_after'):
            before=pending.pop(e['pair_key'],None)
            try:
                assert before is not None,'Unpaired exit'
                assert before['sequence']==e['before_sequence']
                assert before['manager']==e['manager'] and before['track']==e['track']
                if parent_mode:
                    assert before['parent']==e['parent'] and before['side']==e['side']
                    assert before['selected_child']==before['track'],'Selected child mismatch'
                assert int(e['stack'],16)==int(before['stack'],16)+12,'Stack cleanup mismatch'
                assert e['depth']==before['depth']-1,'Buffer stack depth mismatch'
                assert int(before['filter'],16)==0,'Filtered branch unsupported'
                dst=before['destination_before'];after=e['destination_after']
                assert (dst['frame'],dst['data'],dst['rows'])==(after['frame'],after['data'],after['rows']),'Destination identity changed'
                initial=data(dst);source=data(before['source_before']);actual=data(after)
                weight=struct.unpack('<f',bytes.fromhex(before['weight_hex4']))[0]
                if parent_mode:
                    alpha=struct.unpack('<f',bytes.fromhex(before['alpha_hex4']))[0]
                    assert weight==(1. if before['side']=='left'else alpha),'Parent dispatch weight mismatch'
                    child_header=bytes.fromhex(before['child_header_hex32'])
                    assert len(child_header)==32
                    assert before['mode']==(1 if struct.unpack_from('<I',child_header,8)[0]==0 else 0),'Parent child mode mismatch'
                predicted=replay(initial,source,weight,before['mode'])
                errors=[];masks=[]
                for i in range(len(actual)//52):
                    a=struct.unpack_from('<12fI',actual,52*i);b=struct.unpack_from('<12fI',predicted,52*i)
                    masks.append(a[-1]==b[-1])
                    errors.extend(abs(x-y)for x,y in zip(a[:12],b[:12])if math.isfinite(x)and math.isfinite(y))
                checks.append(dict(before_sequence=before['sequence'],after_sequence=e['sequence'],track=e['track'],parent=before.get('parent'),side=before.get('side'),
                    rows=len(actual)//52,mode=before['mode'],weight=weight,byte_exact=actual==predicted,
                    masks_equal=all(masks),max_finite_component_error=max(errors,default=0),
                    differing_bytes=sum(x!=y for x,y in zip(actual,predicted))))
            except (KeyError,AssertionError,ValueError,TypeError) as ex:rejected.append(dict(sequence=e['sequence'],reason=str(ex)))
    rejected.extend(dict(sequence=e['sequence'],reason='Unpaired entry at capture end')for e in pending.values())
    report=dict(capture=str(path.resolve()),sha256=hashlib.sha256(raw).hexdigest(),exe_sha256=sha,
        checks=checks,rejected=rejected,checked_pairs=len(checks),byte_exact_pairs=sum(c['byte_exact']for c in checks),
        scope='Captured raw source and initial destination replayed through original5A14D0 null-filter dispatcher. Pair keyed by track/manager/stack and12byte cleanup, destination identity/depth checked. No actor/thread identity, preceding source sampling or complete graph scheduling proof.')
    Path(output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report

if __name__=='__main__':
    r=analyze(sys.argv[1],sys.argv[2]if len(sys.argv)>2 else Path(__file__).parent/'ControllerState/live-post-blend-analysis.json')
    print(json.dumps({k:r[k]for k in ('checked_pairs','byte_exact_pairs','rejected')}))
