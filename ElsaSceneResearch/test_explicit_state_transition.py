"""File parameter -> native activation/fallback -> continuous observed fade endpoints."""
import json,struct
from pathlib import Path
from read_idle_state_parameters import read
from native_explicit_state_transition import ExplicitStateTransition
from analyze_activation_fade_capture import analyze
R=Path(__file__).resolve().parents[1]
source=R/'OctaneLiveInspector/Captures/ce_activationfade_20261021_210508_250366046.jsonl'
xml=Path('F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/assets/gamedb/animtree_includes/basicmobility.animtree')
params=read(xml,R/'ElsaSceneResearch/installed-elsa-bent-decoded.json')
state=next(s for s in params['states']if s['state_path'].endswith('/Passive_Group/IdleC'))
audit=analyze(source);assert audit['checked']==audit['exact']==3 and not audit['boundaries']
rows=[json.loads(l)for l in source.read_text().splitlines()];activation=next(r for r in rows if r.get('event')=='activation')
scalar=lambda n:struct.unpack_from('<f',bytes.fromhex(n['payload']))[0]
config=bytes.fromhex(activation['config_hex64']);units,parameter=struct.unpack_from('<if',config,0x24)
offset=struct.unpack('<f',bytes.fromhex(activation['global_clock_offset_hex4']))[0]
sequence=ExplicitStateTransition(state['ease_duration_units'],scalar(activation['after']['clock']),header=bytes.fromhex(activation['before']['header']),configuration_units=units,curve_parameter=parameter,clock_offset=offset)
checks=[]
for r in rows:
 if r.get('event')!='update':continue
 value=sequence.update(scalar(r['after']['clock']));expected=scalar(r['after']['output'])
 assert struct.pack('<f',value)==struct.pack('<f',expected)
 checks.append(dict(sequence=r['sequence'],clock=sequence.clock,predicted=value,captured=expected,exact=True))
# Deterministic offline clock timeline uses the same file property; no captured states between samples.
sequence=ExplicitStateTransition(state['ease_duration_units'])
timeline=[dict(clock=i/120,factor=sequence.update(i/120))for i in range(19)]
assert timeline[0]['factor']==0 and timeline[-1]['factor']==1
assert all(a['factor']<=b['factor']for a,b in zip(timeline,timeline[1:]))
try:sequence.update(-1.)
except ValueError:pass
else:raise AssertionError('Backwards clock accepted')
out=dict(passed=True,xml_sha256=params['xml_sha256'],selected_state=state,requested_duration_seconds=sequence.duration,stored_duration_seconds=sequence.stored_duration,captured_factor_endpoints=checks,offline_timeline=timeline,scope='Explicit activation, file EaseDuration selection and negative-duration replacement followed by two observed clock endpoints. Both factors match without reseeding intermediate headers. The capture omits intermediate updates; matching endpoints does not prove their timing/completion callbacks or automatic state scheduling. Source XML provenance of the live instance remains unverified. No viewer pose change.')
(R/'ElsaSceneResearch/ControllerState/explicit-state-transition-validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=True,exact_captured_endpoints=len(checks),offline_samples=len(timeline),duration=sequence.duration)))
