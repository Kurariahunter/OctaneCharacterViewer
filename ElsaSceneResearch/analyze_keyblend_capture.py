"""Replay observed effective KeyBlend parameters; no guessed Speed/Direction label."""
import json,math,struct,sys
from pathlib import Path
from native_pc_keyblend_selector import select

def analyze(path,output):
    es=[json.loads(l)for l in Path(path).read_text().splitlines()]
    assert es[0]['schema']=='di3_key_blend_v1'
    base=int(es[0]['module_base'],16);pending={};checks=[];rejected=[]
    for e in es:
        if e['event']=='selector_before':
            if e['pair_key']in pending:raise ValueError('Ambiguous entry')
            pending[e['pair_key']]=e
        elif e['event']=='selector_after':
            before=pending.pop(e['pair_key'],None)
            try:
                assert before is not None,'Unpaired exit'
                assert before['sequence']==e['before_sequence'] and before['parent']==e['parent']
                assert int(e['stack'],16)==int(before['stack'],16)+16,'Stack mismatch'
                header=bytes.fromhex(before['parent_header_hex84']);assert len(header)==84
                assert struct.unpack_from('<I',header)[0]-base+0x400000==0x1b38e94,'Unexpected KeyBlend vtable'
                raw=bytes.fromhex(before['keys_hex4']);assert len(raw)==4*before['key_count']
                keys=list(struct.unpack('<'+'f'*before['key_count'],raw))
                value=struct.unpack('<f',bytes.fromhex(before['effective_parameter_hex4']))[0]
                alpha,left,right=struct.unpack_from('<fII',header,0x48)
                predicted=select(value,keys,before['child_count'],(left,right,alpha))
                actual=dict(left=e['left_index'],right=e['right_index'],alpha=struct.unpack('<f',bytes.fromhex(e['alpha_hex4']))[0])
                assert math.isfinite(actual['alpha'])
                children=before['children'];assert 0<=actual['left']<before['child_count'] and 0<=actual['right']<before['child_count']
                checks.append(dict(before_sequence=before['sequence'],after_sequence=e['sequence'],parent=e['parent'],
                    effective_parameter=value,keys=keys,child_count=before['child_count'],captured=actual,predicted=predicted,
                    exact=actual==predicted,left_child=children['slot_'+str(actual['left'])],right_child=children['slot_'+str(actual['right'])]))
            except (AssertionError,KeyError,ValueError,TypeError)as ex:rejected.append(dict(sequence=e['sequence'],reason=str(ex)))
    rejected.extend(dict(sequence=e['sequence'],reason='Unpaired entry at end')for e in pending.values())
    r=dict(capture=str(Path(path).resolve()),checked_pairs=len(checks),exact_pairs=sum(c['exact']for c in checks),checks=checks,rejected=rejected,
        scope='Effective parameter fed to original selector with captured keys/count/prior output. Expression evaluation itself not replayed. Child identities are pointer/header observations, not actor or motion names. No parent dispatch/buffer scheduling proof.')
    Path(output).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');return r

if __name__=='__main__':
    r=analyze(sys.argv[1],Path(__file__).parent/'ControllerState/live-keyblend-analysis.json')
    print(json.dumps({k:r[k]for k in ('checked_pairs','exact_pairs','rejected')}))
