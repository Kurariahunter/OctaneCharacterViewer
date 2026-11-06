"""Compare observed parent/child times with original native time arithmetic."""
import json,struct,sys
from pathlib import Path
from native_pc_keyblend_time import evaluate
def value(s):return struct.unpack('<f',bytes.fromhex(s))[0]

def analyze(path,output):
    es=[json.loads(l)for l in Path(path).read_text().splitlines()];assert es[0]['schema']=='di3_parent_time_v1'
    parents={e['sequence']:e for e in es if e['event']=='parent_time'};checks=[];rejected=[]
    sites={'single_child_time':'0x5a1695','left_child_time':'0x5a16cd','right_child_time':'0x5a1722'}
    for e in es:
        if e['event'] not in sites:continue
        try:
            p=parents[e['parent_sequence']];assert p['context_key']==e['context_key'] and p['parent']==e['parent']
            delta=20 if e['event']=='single_child_time'else 32
            assert int(e['stack'],16)+delta==int(p['stack'],16),'Parent stack mismatch'
            children=[p['children']['slot_'+str(p[k])]for k in ('left_index','right_index')]
            selected=children[1 if e['event']=='right_child_time'else 0]
            assert e['child']==selected['pointer'],'Selected child mismatch'
            assert e['child_duration_hex4']==selected['duration_hex4'],'Child duration changed'
            result=evaluate(value(p['incoming_time_hex4']),value(p['duration_hex4']),[value(c['duration_hex4'])for c in children],value(p['alpha_hex4']))
            calls=[c for c in result['child_calls']if c['site']==sites[e['event']]];assert len(calls)==1,'Native branch mismatch'
            actual=value(e['child_time_hex4']);norm=value(e['normalized_parent_time_hex4'])
            checks.append(dict(parent_sequence=p['sequence'],child_sequence=e['sequence'],branch=e['event'],
                incoming_time=value(p['incoming_time_hex4']),parent_duration=value(p['duration_hex4']),child_duration=value(e['child_duration_hex4']),
                actual_time=actual,predicted_time=calls[0]['time'],actual_normalized=norm,predicted_normalized=result['normalized_time'],
                exact=actual==calls[0]['time']and norm==result['normalized_time']))
        except (AssertionError,KeyError,ValueError,TypeError)as ex:rejected.append(dict(sequence=e['sequence'],reason=str(ex)))
    r=dict(capture=str(Path(path).resolve()),parent_entries=len(parents),checked_child_calls=len(checks),exact_child_calls=sum(c['exact']for c in checks),checks=checks,rejected=rejected,
        scope='Original parent time arithmetic/control flow with child evaluation/buffer operations intercepted. Context links use parent/stack/selected pointer and stable duration; no thread identity, complete parent pose or blended output proof.')
    Path(output).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');return r
if __name__=='__main__':
    r=analyze(sys.argv[1],Path(__file__).parent/'ControllerState/live-parent-time-analysis.json')
    print(json.dumps({k:r[k]for k in ('parent_entries','checked_child_calls','exact_child_calls','rejected')}))
