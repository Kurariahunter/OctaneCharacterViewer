"""Validate the state wrapper against independent recorded game outputs."""
import json
from pathlib import Path
from native_scalar_state import ScalarStates
R=Path(__file__).parent
report=json.loads((R/'ControllerState/idle-transition-analysis-201439.json').read_text())
bank=ScalarStates();n=0
for row in report['rows']:
 for d in row['details']:
  key=d['port'];bank.seed(key,d['previous_output'],d['previous_factor'],bool(d['processor_flags']&0x80000000))
  assert bank.update(key,d['source_scalar'],d['factor30'])==d['final_scalar']
  n+=1
assert n==306
fresh=ScalarStates();assert fresh.update('new',10.,.25)==2.5
# Separate controller keys must retain independent history.
bank=ScalarStates();bank.seed('a',2.,0.,False);bank.seed('b',20.,0.,False)
assert bank.update('a',10.,.5)==6.
assert bank.update('b',100.,.5)==60.
assert bank.update('a',10.,.75)==8.
result=dict(passed=True,captured_game_values_exact=n,independent_state_sequence=True,scope='Captured states are explicitly seeded; sparse observations are not assumed to be a complete frame stream.')
(R/'ControllerState/scalar-state-wrapper-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
