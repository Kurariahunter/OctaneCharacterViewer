"""Validate six source turn previews and package them for the viewer picker."""
import hashlib,json,math
from pathlib import Path
R=Path(__file__).parent/'NativePreviews';clips=[];metadata=[];nodes=None;model=None
for angle in (45,90,180):
 for side,label in (('l','left'),('r','right')):
  path=R/f'native-turn{angle}{side}-full-palette.json';data=json.loads(path.read_text());v=json.loads(path.with_suffix('.validation.json').read_text())
  assert v['pass'] and v['source_bones']==v['palette_bones']==62 and not data['fallback_parents']
  assert data['profile']['kind']=='turn' and data['source_filter_configuration']['file_entry']==f'TURN{angle}{side.upper()}'
  assert hashlib.sha256(Path(data['source']).read_bytes()).hexdigest()==data['source_sha256']
  for row in data['profile']['companions']:assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
  if nodes is None:nodes=data['source_skin_nodes'];model=data['model_sha256']
  assert nodes==data['source_skin_nodes'] and model==data['model_sha256']
  c=data['clips'][0];previous=-1.;first={r['bone']:r['matrix']for r in c['samples'][0]['transforms']};change=0.
  for s in c['samples']:
   assert s['time']>previous;previous=s['time'];assert len(s['transforms'])==62 and {t['bone']for t in s['transforms']}==set(nodes)
   for t in s['transforms']:
    assert len(t['matrix'])==16 and all(math.isfinite(x)for x in t['matrix'])
    change=max(change,max(abs(a-b)for a,b in zip(t['matrix'],first[t['bone']])))
  assert change>.001 and abs(previous-c['duration'])<1e-8
  c['name']=f'Turn {angle} {label} (source motion)';clips.append(c);metadata.append(dict(name=c['name'],source=data['source'],source_sha256=data['source_sha256'],artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),validation=v,max_matrix_change_from_first=change))
report=dict(model_sha256=model,scope='Six PC Elsa source turn motions. Actor world-facing/yaw and runtime state selection are not reconstructed.',source_skin_nodes=nodes,fallback_parents={},fixture_assumptions=['Passive idle phase zero initializes absent leaf controls','Reset dynamics and fixture gravity; no collision scene','No guessed actor rotation or world displacement','Source skeletal turn motion, not a completed game turn controller'],timing_configuration=dict(mode='fixture'),profiles=metadata,clips=clips)
(R/'turn-pack.json').write_text(json.dumps(report,separators=(',',':')),encoding='utf-8');(R/'turn-pack-validation.json').write_text(json.dumps(dict(passed=True,clips=metadata,source_bones=62),indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,clips=[c['name']for c in clips],source_bones=62)))
