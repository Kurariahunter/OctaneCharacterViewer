"""Original negative-duration guard/getter/setter window; no call-result stubs."""
import json,struct
from pathlib import Path
from native_transition_processor import resolve_duration,sha
R=Path(__file__).parent
capture=R.parent/'OctaneLiveInspector/Captures/ce_activationfade_20261021_210508_250366046.jsonl'
events=[json.loads(l)for l in capture.read_text().splitlines()]
a=next(x for x in events if x['event']=='activation');first=next(x for x in events if x['event']=='update')
initial=bytes.fromhex(a['after']['header']);rows=[]
for old in [-1.,-0.03333333507180214,0.,.1]:
 for replacement in [0.,0.10000000894069672,.25]:
  h=bytearray(initial);struct.pack_into('<f',h,0x24,old)
  actual=resolve_duration(h,replacement);value=struct.unpack_from('<f',actual,0x24)[0]
  expected=struct.unpack('<f',struct.pack('<f',replacement if old<0 else old))[0]
  assert value==expected
  for offset in [0x1c,0x20,0x28,0x2c,0x30,0x34,0x48,0x4c,0x50]:assert actual[offset:offset+4]==h[offset:offset+4]
  assert actual[0x54]==h[0x54]
  rows.append(dict(old_duration=old,supplied_replacement=replacement,output_duration=value))
# Check that the identified operation explains the observed field change when
# supplied the observed replacement. Its caller argument was NOT captured.
observed=bytes.fromhex(first['before']['header']);replacement=struct.unpack_from('<f',observed,0x24)[0]
candidate=resolve_duration(initial,replacement)
fields=list(range(0x1c,0x38,4))+[0x48,0x4c,0x50]
assert all(candidate[o:o+4]==observed[o:o+4]for o in fields)
r=dict(passed=True,exe_sha256=sha,cases=rows,observed_numeric_change_explained_with_supplied_replacement=True,scope='Native770364..77038C calls originalBD74B0 getter and525CB0 setter. Replacement sourced from captured later header for candidate linkage; not an independent observation of the live writer or its caller argument.')
(R/'ControllerState/transition-duration-fallback-validation.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows))))
