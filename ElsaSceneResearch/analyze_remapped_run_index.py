"""Separate run-local matches from other poses in remapped live hand samples."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
live=R/'ElsaSceneResearch/ControllerState/remapped-index-running-20s.json';preview=R/'OctaneCharacterViewer/NativePreviews/native-run-full-palette.json'
d=json.loads(live.read_text());p=json.loads(preview.read_text());refs={}
for proc in p['finger_diagnostics']['samples'][0]['processors']:
 if proc['processor'] not in (165,171):continue
 side='Left'if proc['processor']==165 else'Right'
 refs[side]=[o['quaternion']+o['translation']+[o['scale']]for o in proc['outputs'][:2]]
def distance(a,b):
 q=min(max(abs(x-y)for x,y in zip(a[:4],b[:4])),max(abs(x+y)for x,y in zip(a[:4],b[:4])))
 return max(q,max(abs(x-y)for x,y in zip(a[4:],b[4:])))
rows=[];summary=[]
for obs in d['observations']:
 for h in obs['hands']:
  if not h['coherent']:continue
  local_error=max(distance(h['nodes'][k]['values'],ref)for k,ref in zip(('Local1','Local2'),refs[h['side']]))
  rows.append(dict(elapsed=obs['elapsed'],side=h['side'],stamp=h['nodes']['Hand']['stamp'],local_component_error=local_error,run_local_match=local_error<=2e-6,palette_component_error=h['best_run_comparison']['error']))
for side in ('Left','Right'):
 hs=[r for r in rows if r['side']==side];matches=[r for r in hs if r['run_local_match']];close=[r for r in matches if r['palette_component_error']<1e-5]
 summary.append(dict(side=side,coherent_samples=len(hs),unique_stamps=len({r['stamp']for r in hs}),run_local_matches=len(matches),matched_local_palette_within_1e_5=len(close),other_local_poses=len(hs)-len(matches),max_palette_error_with_matching_locals=max((r['palette_component_error']for r in matches),default=None),max_local_error_with_matching_locals=max((r['local_component_error']for r in matches),default=None)))
report=dict(live_sha256=hashlib.sha256(live.read_bytes()).hexdigest(),preview_sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),human_context='User reported Running now before20-second bridge sampling.',table_checks=d['table_checks'],summary=summary,rows=rows,scope='Coherent per-hand observations from a surviving captured geometry-copy palette. Classifies matching local index payloads against native file-driven run diagnostics; other poses are retained, not silently discarded. Palette comparison is hand-relative and nearest cached run phase; it is not full-body phase synchronization, clip identity or GPU draw proof.')
(R/'ElsaSceneResearch/ControllerState/remapped-running-index-analysis.json').write_text(json.dumps(report,indent=2));print(json.dumps(summary))
