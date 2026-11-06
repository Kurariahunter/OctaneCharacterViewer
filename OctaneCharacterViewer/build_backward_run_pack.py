"""Validate and package three new backward run previews for the viewer picker."""
import hashlib,json,math
from pathlib import Path
R=Path(__file__).parent/'NativePreviews';clips=[];metadata=[];nodes=None;model=None
for suffix,title,weight in (('b','Backward run',.8),('rb','Backward-right run',.85),('lb','Backward-left run',.85)):
 path=R/f'native-run{suffix}-full-palette.json';data=json.loads(path.read_text());v=json.loads(path.with_suffix('.validation.json').read_text())
 assert v['pass'] and v['source_bones']==v['palette_bones']==62 and not data['fallback_parents']
 assert hashlib.sha256(Path(data['source']).read_bytes()).hexdigest()==data['source_sha256']
 for row in data['profile']['companions']:assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
 group=data['source_composition']['selected_group'];assert group['tracks'][1]['explicit_weight']==weight
 assert [Path(t['filename']).stem for t in group['tracks']]==['grl_bm_run'+suffix,'grl_bm_run_upbody_add','human_bm_run'+suffix+'_lean_add']
 if nodes is None:nodes=data['source_skin_nodes'];model=data['model_sha256']
 assert nodes==data['source_skin_nodes'] and model==data['model_sha256']
 clip=data['clips'][0];previous=-1.
 for sample in clip['samples']:
  assert sample['time']>previous;previous=sample['time'];assert {t['bone']for t in sample['transforms']}==set(nodes)
  assert len(sample['transforms'])==62 and all(len(t['matrix'])==16 and all(math.isfinite(x)for x in t['matrix'])for t in sample['transforms'])
 clip['name']=title;clips.append(clip);metadata.append(dict(name=title,artifact=str(path.resolve()),artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),profile=data['profile'],declared_group=group,validation=v))
out=R/'backward-run-pack.json';report=dict(model_sha256=model,scope='Three bounded native PC Elsa backward run previews; authored source groups with explicit preview timing/passive seed, not automatic direction selection.',source_skin_nodes=nodes,fallback_parents={},fixture_assumptions=['Passive idle phase zero seeds missing controls','Reset dynamics, measured gravity, no actor collision scene','Native main/upper/lean composition; runtime state/direction scheduling incomplete','PC Elsa rig only; no game parity or general character compatibility claim'],timing_configuration=dict(mode='fixture'),profiles=metadata,clips=clips)
out.write_text(json.dumps(report,separators=(',',':')),encoding='utf-8')
(R/'backward-run-pack-validation.json').write_text(json.dumps(dict(passed=True,clips=[dict(name=c['name'],duration=c['duration'],samples=len(c['samples']))for c in clips],source_bones=62,profiles=metadata),indent=2),encoding='utf-8');print(json.dumps(dict(passed=True,output=str(out.resolve()),clips=[c['name']for c in clips],source_bones=62)))
