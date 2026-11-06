"""Hash-join paired live relationships and replay original native evaluator."""
import hashlib,json,math,struct,sys
from pathlib import Path
from native_pc_relationship import run
from native_pc_lean_ik import sha

FLOAT_VT=0x1B329CC
DILATION_VT=0x1B32724

def analyze(path,output):
    path=Path(path);raw=path.read_bytes();events=[json.loads(l) for l in raw.decode('utf-8').splitlines() if l.strip()]
    assert events[0]['schema'] in ('di3_relationship_pose_v1', 'di3_hand_chain_v1')
    base=int(events[0]['module_base'],16)
    catalog=json.loads((Path(__file__).parent/'pc-finger-native-probe.json').read_text(encoding='utf-8'))
    known={r['sha256']:r for r in catalog['relationships']}
    pending={};pairs=[];rejected=[]
    def unpack_nodes(snapshot,field,width,vt):
        count=snapshot['input_count' if field=='inputs' else 'output_count'];rows=[]
        for i in range(count):
            item=snapshot[field]['slot_'+str(i)]
            assert int(item['vtable'],16)-base+0x400000==vt,'Unexpected '+field+' payload type'
            b=bytes.fromhex(item['payload_hex']);assert len(b)==width,'Wrong payload width'
            values=list(struct.unpack('<'+'f'*(width//4),b));assert all(math.isfinite(v)for v in values)
            rows.append(values)
        return rows
    for e in events:
        if e['event'] not in ('relationship_entry','relationship_exit'):continue
        key=e['pair_key']
        if e['event']=='relationship_entry':
            if key in pending:
                rejected.append({'pair_key':key,'reason':'Ambiguous repeated entry'});pending[key]=None
            else:pending[key]=e
            continue
        entry=pending.pop(key,None)
        if not entry:rejected.append({'pair_key':key,'reason':'Unpaired/ambiguous exit'});continue
        try:
            before,after=entry['snapshot'],e['snapshot']
            blob=bytes.fromhex(after['relationship_blob_hex']);digest=hashlib.sha256(blob).hexdigest()
            assert digest in known,'Unknown full relationship hash'
            assert hashlib.sha256(bytes.fromhex(before['relationship_blob_hex'])).hexdigest()==digest,'Relationship changed within pair'
            spec=known[digest]
            assert before['input_count']==after['input_count']==len(spec['inputs'])
            assert before['output_count']==after['output_count']==len(spec['outputs'])
            for snap in (before,after):
                header=bytes.fromhex(snap['header_hex104']);assert len(header)==104
                assert struct.unpack_from('<I',header,0x64)[0]==0,'Nonzero relationship selector not supported'
            for field in ('inputs','outputs'):
                for i in range(len(after[field])):assert before[field]['slot_'+str(i)]['node']==after[field]['slot_'+str(i)]['node'],'Node changed within pair'
            initial=unpack_nodes(before,'outputs',32,DILATION_VT)
            values=[r[0]for r in unpack_nodes(after,'inputs',4,FLOAT_VT)]
            actual=unpack_nodes(after,'outputs',32,DILATION_VT)
            replay=run(blob,values,len(actual),initial_outputs=initial)
            error=max(abs(a-b)for row,expected in zip(actual,replay)for a,b in zip(row,expected))
            pairs.append({'pair_key':key,'entry_sequence':entry['sequence'],'exit_sequence':e['sequence'],'relationship_processor_in_file':spec['processor'],
                'relationship_sha256':digest,'inputs':values,'initial_outputs':initial,'captured_outputs':actual,'replayed_outputs':replay,'max_component_error':error,'pass':error<=2e-5,
                'exit_input_stamp_matches':[after['inputs']['slot_'+str(i)].get('node_stamp')is not None and after['inputs']['slot_'+str(i)].get('node_stamp')==after['inputs']['slot_'+str(i)].get('metadata_stamp') for i in range(len(values))]})
        except (AssertionError,KeyError,ValueError,TypeError) as ex:
            rejected.append({'pair_key':key,'reason':str(ex)})
    rejected += [{'pair_key':k,'reason':'Unpaired entry at end of capture'}for k in pending]
    report={'capture':str(path.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'exe_sha256':sha,'matched_pairs':len(pairs),'pairs':pairs,'rejected':rejected,
            'pass':bool(pairs)and all(p['pass']for p in pairs),'max_component_error':max((p['max_component_error']for p in pairs),default=None),
            'scope':'Full blob hashes, typed widths and paired node identities checked; original native evaluator replayed using entry output initialization and exit inputs. No actor identity or final skinning parity. Rejected pairs excluded; zero matched pairs cannot pass.'}
    Path(output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    p=Path(sys.argv[1]);out=Path(sys.argv[2])if len(sys.argv)>2 else Path(__file__).parent/'ControllerState/live-relationship-pose-analysis.json'
    r=analyze(p,out);print(json.dumps({k:r[k]for k in ('pass','matched_pairs','max_component_error','rejected')}))
