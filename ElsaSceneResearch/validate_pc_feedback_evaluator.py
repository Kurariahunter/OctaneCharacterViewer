"""Check the corrected evaluator's Aim feedback against captured local rotors."""
import json,struct,hashlib
from pathlib import Path
import numpy as np
from evaluate_pc_feedback_dress import FeedbackDressEval
from native_pc_lean_ik import sha

R=Path(__file__).parent
report=json.loads((R/'DenseCapture175321/Completed/pc-captured-dress-sequence-replay.json').read_text())
capture_path=Path(report['capture']);raw=capture_path.read_bytes()
assert hashlib.sha256(raw).hexdigest()==report['capture_sha256']
capture=json.loads(raw);assert capture['identity']['sha256']==sha
class State:
 def __init__(self,pid,q):self.states={pid:{'q':q}}
 def feedback(self,pid,q):self.states[pid]['q']=list(q)
 def step(self,*args):raise AssertionError('captured positions should terminate chain traversal')
def values(item):
 raw=bytes.fromhex(item['payload_hex']);return list(struct.unpack('<'+'f'*(len(raw)//4),raw))
feedback={};rows=[]
for row in report['rows']:
 if row['orientation']!='previous'or row['zero_force']:continue
 address=row['chain'];index=row['sample_index'];left=address=='0x1e07fdd0';pid=550 if left else 551
 chain=next(c for c in capture['samples'][index]['chains']if c['address']==address);d=chain['dynamics']
 key=(address,row['run'])
 if row['step']==1:
  previous=next(c for c in capture['samples'][index-1]['chains']if c['address']==address)
  feedback[key]=values(previous['dynamics']['cached_orientation']['value'])
 state=State(pid,feedback[key]);e=FeedbackDressEval(state,index,d['delta_time_seconds'][0])
 for node,p in zip((696,701)if left else(712,717),row['predicted']):e.cache[node]=np.array(p)
 anchor=next(v for v in d['input_states']if v['runtime_slot']==5)
 e.raw.cache[643 if left else 649]=values(anchor)
 e.run(689 if left else 705);q=state.states[pid]['q'];feedback[key]=q
 wanted=values(d['cached_orientation']['value']);error=min(max(abs(x-y)for x,y in zip(q,wanted)),max(abs(x+y)for x,y in zip(q,wanted)))
 rows.append(dict(chain=address,sample_index=index,step=row['step'],error=error))
summary=dict(cases=len(rows),carried_steps=sum(r['step']>1 for r in rows),max_component_error=max(r['error']for r in rows))
(R/'pc-feedback-evaluator-validation.json').write_text(json.dumps(dict(summary=summary,rows=rows,scope='Corrected graph evaluator Aim stage with captured anchors and replay-predicted particle positions; prior quaternion seeds once per run. Tests runtime integration of the prior-output initializer, not cloth collision.'),indent=2))
print(json.dumps(summary,indent=2));assert summary['max_component_error']==0
