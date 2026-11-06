"""Compare recorded final matrices with preceding world values and viewer formula."""
import json,struct,sys
from pathlib import Path
import numpy as np
from evaluate_pc_arms import quat
from analyze_finger_world_capture import analyze

def compare(path,output):
    path=Path(path);output=Path(output)
    replay=analyze(path,output.with_suffix('.native.json'));assert replay['pass']
    es=[json.loads(l)for l in path.read_text().splitlines()]
    assert es[0]['schema']=='di3_finger_final_v1'
    byseq={e['sequence']:e for e in es if 'sequence'in e};rows=[]
    for e in es:
        if e['event']!='finger_matrix':continue
        prior=byseq[e['source_tag']['event_sequence']]
        assert prior['event']=='finger_world_dilation'
        same_payload=prior['output']['payload_hex']==e['input']['payload_hex']
        same_stamp=prior['output']['node_stamp']==e['input']['node_stamp']
        v=struct.unpack('<8f',bytes.fromhex(e['input']['payload_hex']))
        packed=struct.unpack('<12f',bytes.fromhex(e['output']['payload_hex']))
        actual=np.eye(4);actual[:3,:3]=np.array(packed[:9]).reshape(3,3).T;actual[:3,3]=packed[9:]
        viewer=np.eye(4);viewer[:3,:3]=quat(v[:4])*v[7];viewer[:3,3]=v[4:7]
        quadratic=viewer.copy();quadratic[:3,:3]+=np.eye(3)*(sum(x*x for x in v[:4])-1)*v[7]
        rows.append(dict(sequence=e['sequence'],source_sequence=prior['sequence'],slot=e['source_tag']['slot'],
            unchanged_payload=same_payload,unchanged_stamp=same_stamp,
            quaternion_norm_squared=sum(x*x for x in v[:4]),viewer_matrix_error=float(np.max(abs(actual-viewer))),
            quadratic_matrix_error=float(np.max(abs(actual-quadratic)))))
    r=dict(capture=str(path.resolve()),cases=len(rows),all_links_unchanged=all(x['unchanged_payload']and x['unchanged_stamp']for x in rows),
        max_viewer_matrix_error=max(x['viewer_matrix_error']for x in rows),
        max_quadratic_matrix_error=max(x['quadratic_matrix_error']for x in rows),rows=rows,
        scope='Live final second-joint matrices and preceding linked Dilation output, same payload/stamp checked. Viewer unit-rotor formula versus native quadratic formula. This does not compare independently composed viewer animation inputs, full skin palette, thumbs or renderer consumption.')
    output.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');return r

if __name__=='__main__':
    r=compare(sys.argv[1],Path(__file__).parent/'ControllerState/live-final-finger-viewer-comparison.json')
    print(json.dumps({k:v for k,v in r.items()if k not in ('rows','scope')}))
