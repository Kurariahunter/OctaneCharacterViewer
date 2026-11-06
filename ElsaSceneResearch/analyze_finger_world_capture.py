"""Validate linked live finger records and replay their original PC operators."""
import collections, hashlib, json, math, struct, sys
from pathlib import Path
from native_pc_dress_math import call
from native_pc_skin_matrix import matrix,dilation_matrix
from native_pc_lean_ik import sha

def analyze(path, output):
    path=Path(path); raw=path.read_bytes()
    events=[json.loads(l) for l in raw.decode('utf-8').splitlines() if l.strip()]
    assert events[0]['schema'] in ('di3_finger_world_v1','di3_finger_final_v1','di3_world_chain_v1')
    strict=events[0]['schema']=='di3_world_chain_v1'
    final=events[0]['schema'] in ('di3_finger_final_v1','di3_world_chain_v1')
    base=int(events[0]['module_base'],16)
    known={r['sha256']:r['processor'] for r in json.loads((Path(__file__).parent/'pc-finger-native-probe.json').read_text())['relationships']}
    seeds={}; worlds={}; dilations={}; checks=[]; rejected=[]
    def continuous(prior, current):
        if not strict:return
        assert prior['node']==current['node'] and prior['producer']==current['producer'],'Producer/node continuity failed'
        assert bytes.fromhex(prior['payload_hex'])==bytes.fromhex(current['payload_hex']),'Payload changed since predecessor'
        assert prior.get('node_stamp') is not None and prior['node_stamp']==current.get('node_stamp'),'Evaluation stamp changed since predecessor'
    def node(n,width,vt,offset=52):
        assert int(n['vtable'],16)-base+0x400000==vt,'Unexpected payload type'
        assert n['payload_offset']==offset,'Unexpected payload offset'
        b=bytes.fromhex(n['payload_hex']); assert len(b)==width,'Unexpected payload width'
        v=list(struct.unpack('<'+'f'*(width//4),b)); assert all(map(math.isfinite,v)),'Nonfinite payload'
        assert n.get('node_stamp') is not None and n['node_stamp']==n.get('metadata_stamp'),'Stale payload'
        return v
    for e in events:
        kind=e['event']
        if kind in ('start','stop'):continue
        try:
            if kind=='relationship_seed':
                digest=hashlib.sha256(bytes.fromhex(e['relationship_blob_hex'])).hexdigest()
                assert digest in known,'Unknown relationship hash'
                for n in e['inputs'].values():node(n,4,0x1b329cc)
                for n in e['outputs'].values():
                    node(n,32,0x1b32724); assert n['producer']==e['processor']
                seeds[e['sequence']]=(e,known[digest]);continue
            tag=e['source_tag']; seed,pid=seeds[tag['seed_sequence']]
            slot=tag['slot']; local=seed['outputs']['slot_'+str(slot)]
            if kind=='finger_world_transform':
                assert slot in (0,2) and tag['processor']==seed['processor']
                assert e['left']['node']==local['node'] and e['left']['producer']==seed['processor']
                continuous(local,e['left'])
                a=node(e['left'],32,0x1b32724); b=node(e['right'],64,0x1b32d84)
                actual=node(e['output'],64,0x1b32d84)
                replay=call(0x57cb30,[a,b],'array',16)
                worlds[e['sequence']]=e
            elif kind=='finger_world_dilation':
                assert slot in (1,3) and tag['processor']==seed['processor']
                assert e['input']['node']==local['node']
                continuous(local,e['input'])
                w=worlds[e['converter_tag']['event_sequence']]
                assert w['source_tag']['seed_sequence']==tag['seed_sequence'] and w['source_tag']['slot']==slot-1
                assert e['converter']['node']==w['output']['node']
                continuous(w['output'],e['converter'])
                a=node(e['input'],32,0x1b32724); b=node(e['converter'],64,0x1b32d84)
                actual=node(e['output'],32,0x1b32724)
                replay=call(0x4d78d0,[a,b],'typed',8)
                dilations[e['sequence']]=e
            elif kind=='finger_matrix':
                w=(dilations if final else worlds)[tag['event_sequence']]
                assert w['source_tag']['seed_sequence']==tag['seed_sequence'] and w['source_tag']['slot']==slot
                assert e['input']['node']==w['output']['node']
                continuous(w['output'],e['input'])
                a=node(e['input'],32 if final else 64,0x1b32724 if final else 0x1b32d84)
                actual=node(e['output'],48,0x1b3302c,64)
                replay=(dilation_matrix if final else matrix)(a)
            else:raise ValueError('Unknown event')
            assert e['output']['producer']==e['processor'],'Output producer mismatch'
            err=max(abs(a-b) for a,b in zip(actual,replay))
            checks.append({'sequence':e['sequence'],'stage':kind,'relationship_processor_in_file':pid,'slot':slot,'max_component_error':err,'pass':err<=2e-5,'captured':actual,'replayed':replay})
        except (AssertionError,KeyError,ValueError,TypeError) as ex:
            rejected.append({'sequence':e.get('sequence'),'stage':kind,'reason':str(ex)})
    report={'capture':str(path.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'exe_sha256':sha,
        'counts':dict(collections.Counter(e['event'] for e in events)), 'seed_count':len(seeds),
        'checked_stages':dict(collections.Counter(c['stage'] for c in checks)), 'checks':checks,'rejected':rejected,
        'max_component_error':max((c['max_component_error'] for c in checks),default=None),
        'pass':bool(checks) and not rejected and all(c['pass'] for c in checks),'stop':events[-1],
        'scope':('Hash-joined relationship outputs, unchanged predecessor bytes/producers/stamps, typed fresh snapshots and native downstream operator replay. No relationship evaluator replay, actor identity, renderer consumption or full preview parity established.' if strict else 'Hash-joined provenance, typed fresh snapshots and native operator replay using captured downstream inputs. Seed payloads identify nodes, not subsequent-frame local values. No actor identity, renderer consumption or full preview parity established.')}
    Path(output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    r=analyze(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else Path(__file__).parent/'ControllerState/live-finger-world-linked-analysis.json')
    print(json.dumps({k:r[k] for k in ('pass','seed_count','checked_stages','max_component_error','rejected')}))
