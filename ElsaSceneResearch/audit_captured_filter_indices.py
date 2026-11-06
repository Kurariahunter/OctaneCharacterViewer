"""Cross-check previously logged blend indices against verified EXE masks; no new process access."""
import json,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).parent
p=ROOT.parent/'OctaneLiveInspector/Captures/ce_blendexec_20261017_204631_310307171.jsonl'
raw=p.read_bytes();rows=[]
for line in raw.decode().splitlines():
 r=json.loads(line)
 if r.get('event')!='blend':continue
 for key,c in r.get('contributions',{}).items():
  packed=int(c['packed_word'],16);source=packed&0xfff;index=(packed>>12)&0xfff
  if source!=c['slot']or index!=c['weight_index']:raise ValueError('Captured index disagrees with EXE bit extraction')
  rows.append(dict(sequence=r['sequence'],record=key,packed=c['packed_word'],source_index=source,filter_index=index,filter_missing=c.get('weight_default_one',False)))
report=dict(pass_=True,capture=str(p),capture_sha256=hashlib.sha256(raw).hexdigest(),contributions=len(rows),different_source_filter_indices=sum(r['source_index']!=r['filter_index']for r in rows),filter_missing=sum(r['filter_missing']for r in rows),distinct_pairs=len({(r['source_index'],r['filter_index'])for r in rows}),rows=rows,scope='Checks existing capture metadata against native index extraction; capture lacks verified actor ownership and complete source filter/port tables. No new game memory access, no new proof of authored channel mapping.')
report['pass']=report.pop('pass_');(ROOT/'pc-captured-filter-index-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='rows'},indent=2))
