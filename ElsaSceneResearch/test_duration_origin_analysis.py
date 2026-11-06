"""Live linked chain plus rejection of changed forwarded/stored values."""
import json
from pathlib import Path
from analyze_duration_origin_capture import analyze
R=Path(__file__).resolve().parents[1]
p=R/'OctaneLiveInspector/Captures/ce_durationorigin_20261021_212000_251258593.jsonl'
r=analyze(p);assert r['verified_chains']==1 and not r['boundaries']
c=r['chains'][0];assert c['requested_duration']==c['stored_duration']==0 and c['playback_caller_preferred_va']=='0x1448cdb'
fixtures=R/'ElsaSceneResearch/ControllerState/DurationOriginFixtures';fixtures.mkdir(exist_ok=True)
for case in ['request_argument','stored_duration']:
 rows=[json.loads(l)for l in p.read_text().splitlines()]
 if case=='request_argument':
  row=next(x for x in rows if x['event']=='request');b=bytearray.fromhex(row['arguments_hex16']);b[12:16]=bytes.fromhex('00 00 80 3f');row['arguments_hex16']=b.hex()
 else:next(x for x in rows if x['event']=='duration_set')['stored_hex4']='00 00 80 3F'
 q=fixtures/(case+'.jsonl');q.write_text('\n'.join(json.dumps(x)for x in rows),encoding='utf-8');bad=analyze(q)
 assert bad['verified_chains']==0 and bad['boundaries']
print(json.dumps(dict(passed=True,verified_live_chain=1,corrupt_forwarding_rejected=True,corrupt_store_rejected=True)))
