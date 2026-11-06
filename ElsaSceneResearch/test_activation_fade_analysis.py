"""Recorded capture parity, continuity-gap reporting and corrupted output rejection."""
import json
from pathlib import Path
from analyze_activation_fade_capture import analyze
R=Path(__file__).resolve().parents[1]
p=R/'OctaneLiveInspector/Captures/ce_activationfade_20261021_210508_250366046.jsonl'
r=analyze(p);assert r['checked']==r['exact']==3 and not r['boundaries']and not r['continuous_numeric_chain']
assert r['rows'][1]['unobserved_changes_since_previous']==['0x24']
rows=[json.loads(l)for l in p.read_text().splitlines()]
next(x for x in rows if x['event']=='update')['after']['output']['payload']='00 00 00 00'
fixtures=R/'ElsaSceneResearch/ControllerState/ActivationFadeFixtures';fixtures.mkdir(exist_ok=True)
bad=fixtures/'bad-output.jsonl';bad.write_text('\n'.join(json.dumps(x)for x in rows),encoding='utf-8');negative=analyze(bad)
assert negative['checked']==3 and negative['exact']==2
print(json.dumps(dict(passed=True,live_records_exact=3,missing_duration_write_reported=True,corrupted_output_rejected=True)))
