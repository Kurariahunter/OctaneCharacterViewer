"""Join bounded left/right parent blend observations and replay both stages."""
import json,struct,sys
from pathlib import Path
from analyze_post_blend_capture import analyze
from native_pc_raw_buffer_blend import replay

def analyze_chains(path,output):
    path=Path(path);output=Path(output)
    validation=analyze(path,output.with_suffix('.pairs.json'))
    assert validation['checked_pairs']>0 and not validation['rejected'] and validation['checked_pairs']==validation['byte_exact_pairs']
    es=[json.loads(l)for l in path.read_text().splitlines()];byseq={e['sequence']:e for e in es if 'sequence'in e}
    after={e['before_sequence']:e for e in es if e['event']in ('left_after','right_after')}
    left={};chains=[];boundaries=[]
    def key(e,post=False):return(e['parent'],e['manager'],int(e['stack'],16)-(12 if post else 0))
    for e in es:
        if e['event']=='left_before':left.pop(key(e),None)
        elif e['event']=='left_after':left[key(e,True)]=e
        elif e['event']=='right_before':
            prior=left.pop(key(e),None)
            try:
                assert prior is not None,'No preceding left result for parent/manager/stack'
                start=byseq[prior['before_sequence']];end=after[e['sequence']]
                a=prior['destination_after'];b=e['destination_before']
                assert (a['frame'],a['data'],a['rows'])==(b['frame'],b['data'],b['rows']),'Destination identity changed between sides'
                assert bytes.fromhex(a['hex52'])==bytes.fromhex(b['hex52']),'Left result changed before right blend'
                assert start['alpha_hex4']==e['alpha_hex4']and start['left_index']==e['left_index']and start['right_index']==e['right_index'],'Parent selection changed between sides'
                initial=bytes.fromhex(start['destination_before']['hex52'])
                middle=replay(initial,bytes.fromhex(start['source_before']['hex52']),struct.unpack('<f',bytes.fromhex(start['weight_hex4']))[0],start['mode'])
                final=replay(middle,bytes.fromhex(e['source_before']['hex52']),struct.unpack('<f',bytes.fromhex(e['weight_hex4']))[0],e['mode'])
                actual=bytes.fromhex(end['destination_after']['hex52'])
                chains.append(dict(left_before=start['sequence'],left_after=prior['sequence'],right_before=e['sequence'],right_after=end['sequence'],
                    parent=e['parent'],left_child=start['track'],right_child=e['track'],rows=b['rows'],
                    alpha=struct.unpack('<f',bytes.fromhex(e['alpha_hex4']))[0],intermediate_bytes_exact=True,final_bytes_exact=final==actual))
            except (KeyError,AssertionError,ValueError,TypeError)as ex:boundaries.append(dict(sequence=e['sequence'],reason=str(ex)))
    r=dict(capture=str(path.resolve()),checked_chains=len(chains),exact_chains=sum(c['final_bytes_exact']for c in chains),chains=chains,boundaries=boundaries,
        scope='Two native dispatcher calls replayed in order with captured sources. Parent/manager/stack, unchanged selection, destination identity and intermediate bytes checked. No thread identity or proof that final controller output/rig consumed this buffer. Source generation/time verified separately in earlier captures.')
    output.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');return r

if __name__=='__main__':
    r=analyze_chains(sys.argv[1],Path(__file__).parent/'ControllerState/live-parent-blend-chain-analysis.json')
    print(json.dumps({k:r[k]for k in ('checked_chains','exact_chains','boundaries')}))
