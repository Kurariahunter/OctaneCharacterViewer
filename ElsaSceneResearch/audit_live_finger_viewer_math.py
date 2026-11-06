"""Inject captured boundary inputs into actual viewer graph evaluators, not poses."""
import json,struct,sys
from pathlib import Path
import numpy as np
from analyze_finger_world_capture import analyze
from evaluate_pc_legs import LegEval,quat
from evaluate_pc_raw_transform import affine
from native_pc_skin_matrix import matrix

def unpack(n):
    b=bytes.fromhex(n['payload_hex']);return list(struct.unpack('<'+'f'*(len(b)//4),b))
def dilation_matrix(v):
    m=np.eye(4);m[:3,:3]=quat(v[:4])*v[7];m[:3,3]=v[4:7];return m

def audit(path,output):
    validation=analyze(path,Path(output).with_suffix('.native.json'))
    assert validation['pass'],'Native capture validation failed'
    es=[json.loads(l) for l in Path(path).read_text().splitlines()]
    final=es[0]['schema'] in ('di3_finger_final_v1','di3_world_chain_v1')
    # Source OCT relationship output and world-node associations.
    mapping={165:([176,204,210,216],[178,206,212,218],174),171:([201,207,213,219],[203,209,215,221],199)}
    checks={c['sequence']:c for c in validation['checks']};rows=[]
    for event in es:
        if event.get('sequence') not in checks:continue
        spec=checks[event['sequence']];pid=spec['relationship_processor_in_file'];slot=spec['slot']
        locals_,worlds,parent=mapping[pid];kind=event['event'];e=LegEval()
        if kind=='finger_world_transform':
            e.cache[locals_[slot]]=dilation_matrix(unpack(event['left']))
            e.raw.cache[locals_[slot]]=unpack(event['left'])
            e.raw.cache[parent]=unpack(event['right'])
            raw=e.raw.run(worlds[slot]);packed=matrix(raw)
            actual=affine(unpack(event['output']))
            actual_packed=matrix(unpack(event['output']))
            predicted=affine(raw)
            packed_error=float(np.max(np.abs(np.array(packed)-actual_packed)))
        elif kind=='finger_world_dilation':
            e.cache[locals_[slot]]=dilation_matrix(unpack(event['input']))
            e.raw.cache[locals_[slot]]=unpack(event['input'])
            e.raw.cache[worlds[slot-1]]=unpack(event['converter'])
            predicted=e.run(worlds[slot])
            from native_pc_skin_matrix import dilation_matrix as packed_dilation
            packed=packed_dilation(unpack(event['output']));actual=np.eye(4)
            actual[:3,:3]=np.array(packed[:9]).reshape(3,3).T;actual[:3,3]=packed[9:]
            packed_error=None
        else:
            if final:
                # Viewer exports Dilation skin nodes through e.run, as affine matrices.
                # Seed the actual local/converter dependencies from the same call chain.
                source=next(x for x in es if x.get('sequence')==event['source_tag']['event_sequence'])
                e.cache[locals_[slot]]=dilation_matrix(unpack(source['input']))
                e.raw.cache[locals_[slot]]=unpack(source['input'])
                e.raw.cache[worlds[slot-1]]=unpack(source['converter'])
                predicted=e.run(worlds[slot])
                packed=unpack(event['output']);actual=np.eye(4)
                actual[:3,:3]=np.array(packed[:9]).reshape(3,3).T;actual[:3,3]=packed[9:]
                packed_error=None
            else:
                packed=matrix(unpack(event['input']));actual_packed=unpack(event['output'])
                packed_error=float(np.max(np.abs(np.array(packed)-actual_packed)))
                predicted=np.array(packed);actual=np.array(actual_packed)
        error=float(np.max(np.abs(predicted-actual)))
        rows.append(dict(sequence=event['sequence'],stage=kind,processor=pid,slot=slot,
            max_matrix_error=error,max_packed_error=packed_error,pass_=error<=2e-5 and (packed_error is None or packed_error<=2e-5)))
    report={'pass':bool(rows) and all(r['pass_'] for r in rows),'cases':len(rows),'max_matrix_error':max(r['max_matrix_error']for r in rows),
        'max_packed_error':max(r['max_packed_error']for r in rows if r['max_packed_error'] is not None),'rows':rows,
        'scope':'Actual LegEval/NativeSkinEval routes with captured local and parent/converter boundary inputs, including Dilation affine export when captured. Not viewer clip composition, upstream parent production or render palette consumption. No corrections applied.'}
    Path(output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report

if __name__=='__main__':
    r=audit(sys.argv[1],Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).parent/'ControllerState/live-finger-viewer-math-audit.json')
    print(json.dumps({k:r[k] for k in ('pass','cases','max_matrix_error','max_packed_error')}))
