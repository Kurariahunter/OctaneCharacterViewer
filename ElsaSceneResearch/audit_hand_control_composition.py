"""Audit current preview assignment stages and bounded live-source fingerprints."""
import hashlib,json,struct
from pathlib import Path
from types import SimpleNamespace
from pc_skin_palette import PC_RIG,DN,PROD,get
from read_pc_idle_files import Clip
from pc_graph_controls import apply

R=Path(__file__).parent
profiles=json.loads((R.parent/'OctaneCharacterViewer/native-preview-profiles.json').read_text())['profiles']
rels=json.loads((R/'pc-finger-native-probe.json').read_text())['relationships']
nodes=[i['node']for r in rels for i in r['inputs']]
catalog={}
for p in profiles:
    for item in [dict(name=p['name'],path=p['source'],sha256=p['source_sha256'])]+p['companions']:
        if item['name']=='human_bm_runf_lean_add':continue # validated lean targets are non-hand nodes
        assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
        catalog[item['name']]=Clip(item['path'],PC_RIG)
rows=[];fingerprints=[]
for p in profiles:
    stages=([('elsa_bm_idle_passive',0)] if p['kind']!='idle' else [])+[(p['name'],None)]
    if p['kind']!='idle':stages.append(('grl_bm_'+p['kind']+'_upbody_add',None))
    values_by_node={n:[]for n in nodes};sources={n:set()for n in nodes};writes=[]
    for step in range(61):
        phase=catalog[p['name']].duration*step/60;e=SimpleNamespace(overrides={});stagewrites=[]
        for name,fixed in stages:
            records=catalog[name].sample(phase if fixed is None else fixed)
            apply(e,records,allow_transform_scale=p['kind']=='run' and name==p['name'])
            for record in records.values():
                n=record['source_node']
                if n in values_by_node and n not in PROD:
                    assert '10'in record['channels'],'Unexpected non-scalar hand record'
                    sources[n].add(name)
                    if step==0:stagewrites.append(dict(node=n,source=name,value=e.overrides[n]['Value']))
        vals={n:float(e.overrides.get(n,{}).get('Value',get(DN[n],'Data')))for n in nodes}
        for n in nodes:values_by_node[n].append(vals[n])
        fingerprints.append(dict(profile=p['name'],phase=phase,values=vals))
        if step==0:writes=stagewrites
    rows.append(dict(profile=p['name'],stages=[x[0]for x in stages],phase_zero_writes=writes,
        inputs=[dict(node=n,path=PC_RIG.paths.get(n),sources=sorted(sources[n]),minimum=min(values_by_node[n]),maximum=max(values_by_node[n]))for n in nodes]))
known={r['sha256']:r for r in rels};comparisons=[]
for filename in ('ce_fingerworld_20261019_214443_79942390.jsonl','ce_fingerworld_20261019_215028_80287281.jsonl','ce_fingerfinal_20261019_215831_80770187.jsonl'):
    events=[json.loads(l)for l in (R.parent/'OctaneLiveInspector/Captures'/filename).read_text().splitlines()]
    for e in events:
        if e['event']!='relationship_seed':continue
        rel=known[hashlib.sha256(bytes.fromhex(e['relationship_blob_hex'])).hexdigest()]
        ns=[i['node']for i in rel['inputs']];v=[struct.unpack('<f',bytes.fromhex(e['inputs']['slot_'+str(i)]['payload_hex']))[0]for i in range(len(ns))]
        matches=[]
        for p in profiles:
            candidates=[f for f in fingerprints if f['profile']==p['name']]
            nearest=min(candidates,key=lambda f:max(abs(f['values'][n]-x)for n,x in zip(ns,v)))
            error=max(abs(nearest['values'][n]-x)for n,x in zip(ns,v))
            matches.append(dict(profile=p['name'],phase=nearest['phase'],max_input_error=error))
        comparisons.append(dict(capture=filename,sequence=e['sequence'],processor=rel['processor'],inputs=v,candidates=matches))
report=dict(profiles=rows,live_seed_comparisons=comparisons,
    scope='Current preview replacement-assignment semantics sampled at61 phases per profile, with passive initializer and upper body source order reproduced. Live seed nearest-pattern comparison is bounded61-phase search, not controller identification or proof that a source was playing; independent hand matching does not establish shared phase. Lean targets are disjoint from hand scalars. No composition change applied.')
(R/'ControllerState/hand-control-composition-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'profiles':[{ 'name':r['profile'],'hand_input_ranges':[(i['path'],i['minimum'],i['maximum'])for i in r['inputs'][:2]]}for r in rows],
 'seed_best_matches':[dict(capture=c['capture'],processor=c['processor'],best=min(c['candidates'],key=lambda x:x['max_input_error']))for c in comparisons[-4:]]},indent=2))
