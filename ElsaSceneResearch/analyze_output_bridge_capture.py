"""Replay typed buffer-to-node bridge pairs; omitted node kinds stay explicit."""
import hashlib,json,sys
from pathlib import Path
from native_pc_output_bridge import replay,GLOBALS

def analyze(path,output):
    path=Path(path);raw=path.read_bytes();es=[json.loads(l)for l in raw.decode('utf-8').splitlines()]
    assert es[0]['schema']=='di3_output_bridge_v1'
    pending={};checks=[];rejected=[]
    for e in es:
        if e['event']=='bridge_before':
            if e['pair_key']in pending:raise ValueError('Ambiguous repeated entry')
            pending[e['pair_key']]=e
        elif e['event']=='bridge_after':
            before=pending.pop(e['pair_key'],None)
            try:
                assert before is not None,'Unpaired exit'
                assert before['sequence']==e['before_sequence']and before['processor']==e['processor']
                assert int(e['stack'],16)==int(before['stack'],16)+4,'Stack return mismatch'
                assert before['depth']==0,'Unverified nonzero buffer depth'
                assert before['output_count']==e['output_count']==before['row_count']
                raw_globals={int(k,16):int(v,16)for k,v in before['type_test_globals'].items()}
                assert set(raw_globals)==set(GLOBALS),'Incomplete native type-test globals'
                nodes=[];skipped=[]
                for i in range(before['output_count']):
                    a=before['outputs']['slot_'+str(i)];b=e['outputs']['slot_'+str(i)]
                    assert a.get('node')==b.get('node'),'Output node identity changed'
                    if a.get('payload_width')not in (4,32,64):nodes.append(None);skipped.append(dict(slot=i,reason=a.get('boundary')));continue
                    assert a['rtti_candidate']==b['rtti_candidate']and a['type_word']==b['type_word']
                    payload=bytes.fromhex(a['payload_hex']);assert len(payload)==a['payload_width']==b['payload_width']
                    nodes.append(dict(payload=payload,type_word=a['type_word'],node_stamp=a['node_stamp'],metadata_stamp=a['metadata_stamp']))
                predicted=replay(bytes.fromhex(before['rows_hex52']),nodes,raw_globals);results=[]
                for i,p in predicted.items():
                    actual=e['outputs']['slot_'+str(i)]
                    results.append(dict(slot=i,node=actual['node'],type=actual['rtti_candidate'],payload_bytes_exact=p['payload']==bytes.fromhex(actual['payload_hex']),stamp_exact=p['node_stamp']==actual['node_stamp']))
                assert results,'No supported typed output nodes'
                checks.append(dict(before_sequence=before['sequence'],after_sequence=e['sequence'],processor=e['processor'],supported_nodes=len(results),skipped=skipped,
                    exact=all(x['payload_bytes_exact']and x['stamp_exact']for x in results),nodes=results))
            except (KeyError,AssertionError,ValueError,TypeError)as ex:rejected.append(dict(sequence=e['sequence'],reason=str(ex)))
    rejected.extend(dict(sequence=e['sequence'],reason='Unpaired entry at end')for e in pending.values())
    r=dict(capture=str(path.resolve()),sha256=hashlib.sha256(raw).hexdigest(),checked_pairs=len(checks),exact_pairs=sum(x['exact']for x in checks),
        checks=checks,rejected=rejected,scope='Original52B3C0 replay from captured row data, typed payload initialization, type descriptor words/predicate globals and metadata stamps. Other node kinds omitted explicitly. No actor identity or downstream rig consumption proof.')
    Path(output).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');return r

if __name__=='__main__':
    r=analyze(sys.argv[1],Path(__file__).parent/'ControllerState/live-output-bridge-analysis.json')
    print(json.dumps({k:r[k]for k in ('checked_pairs','exact_pairs','rejected')}))
