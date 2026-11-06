"""Live chain replay and rejection of corrupted pre-selection evidence."""
import json,tempfile
from pathlib import Path
from analyze_node_duration_capture import analyze
R=Path(__file__).resolve().parents[1]
p=R/'OctaneLiveInspector/Captures/ce_nodeduration_20261021_214151_252569109.jsonl'
r=analyze(p);assert r['node_selection_verified_chains']==1 and not r['node_selection_boundaries']
c=r['node_selection_chains'][0]
assert c['configured_parameter']==3 and c['override']==-1 and not c['force_zero']
assert c['native_selected_duration']==c['requested_duration']==c['stored_duration']
with tempfile.TemporaryDirectory(dir=R/'ElsaSceneResearch/ControllerState')as temp:
 for case in ('flags','parameter','identifier','stack'):
  rows=[json.loads(x)for x in p.read_text().splitlines()];s=next(x for x in rows if x.get('event')=='request')['selection']
  if case=='flags':s['runtime_flags']=4
  elif case=='stack':s['stack']=0
  else:
   b=bytearray.fromhex(s['parameter_hex80']);b[0 if case=='identifier'else 0x14]^=1;s['parameter_hex80']=b.hex()
  q=Path(temp)/(case+'.jsonl');q.write_text('\n'.join(json.dumps(x)for x in rows),encoding='utf-8');bad=analyze(q)
  assert bad['node_selection_verified_chains']==0 and bad['node_selection_boundaries'],case
print(json.dumps(dict(passed=True,live_exact_chains=1,corruptions_rejected=4)))
