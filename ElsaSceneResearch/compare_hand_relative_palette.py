"""Compare captured finger palette transforms in hand space against saved viewer poses."""
import json,struct,sys
from pathlib import Path
import numpy as np
from pc_skin_palette import skin,reflect
from native_pc_skin_matrix import matrix,dilation_matrix
ROOT=Path(__file__).resolve().parent
capture=ROOT.parent/'OctaneLiveInspector/Captures/ce_worldchain_20261020_003610_90229843.jsonl'
es=[json.loads(l)for l in capture.read_text().splitlines()];by={e['sequence']:e for e in es if 'sequence'in e}
validation=json.loads((ROOT/'ControllerState/live-world-chain-analysis.json').read_text());assert validation['pass']
checked={c['sequence']:c for c in validation['checks']}
preview=ROOT.parent/'OctaneCharacterViewer/NativePreviews/native-composed-run-test.json'
poses=json.loads(preview.read_text())['clips'][0]['samples']
lookups=[{r['bone']:np.array(r['matrix']).reshape(4,4)for r in p['transforms']}for p in poses]
worldnodes={165:[178,206,212,218],171:[203,209,215,221]};bonebyid={v:k for k,v in skin.items()}
def vals(n):
 b=bytes.fromhex(n['payload_hex']);return struct.unpack('<'+'f'*(len(b)//4),b)
def affine(p):
 m=np.eye(4);m[:3,:3]=np.array(p[:9]).reshape(3,3).T;m[:3,3]=p[9:];return reflect@m@reflect
rows=[]
for e in es:
 if e['event']!='finger_matrix':continue
 spec=checked[e['sequence']];pid=spec['relationship_processor_in_file'];slot=spec['slot']
 d=by[e['source_tag']['event_sequence']];w=by[d['converter_tag']['event_sequence']]
 parent=affine(matrix(vals(w['right'])))
 side='Left'if pid==165 else 'Right';hand='Hand_'+side
 # Both first and second joints, each expressed relative to the captured hand.
 for node,world in [(worldnodes[pid][slot-1],affine(matrix(vals(w['output'])))),(worldnodes[pid][slot],affine(vals(e['output'])))]:
  bone=bonebyid[node];local=np.linalg.inv(parent)@world
  errors=[float(np.max(abs(np.linalg.inv(p[hand])@p[bone]-local)))for p in lookups]
  best=int(np.argmin(errors))
  rows.append(dict(sequence=e['sequence'],bone=bone,source_world_node=node,parent_hand=hand,
    best_preview_sample=best,min_hand_relative_matrix_error=min(errors),max_hand_relative_matrix_error=max(errors)))
report=dict(capture=str(capture),preview=str(preview),rows=rows,observations=len(rows),
 max_best_error=max(r['min_hand_relative_matrix_error']for r in rows),max_all_sample_error=max(r['max_hand_relative_matrix_error']for r in rows),
 bones=sorted({r['bone']for r in rows}),scope='Captured first/second index/middle skin transforms compared in Hand space, using file-derived bone associations and viewer palette. Removes parent placement/animation; no same-time or actor identity claim, no thumb/mesh/game-renderer validation.')
(ROOT/'ControllerState/hand-relative-palette-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items()if k not in ('rows','scope')}))
