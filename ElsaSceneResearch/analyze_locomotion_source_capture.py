"""Summarize route evidence without inferring actor identity or nested calls."""
import collections,hashlib,json,struct,sys
from pathlib import Path
from match_live_clip_prefixes import match
from read_pc_idle_files import Clip
from pc_skin_palette import PC_RIG

def analyze(path,output):
    path=Path(path);output=Path(output)
    es=[json.loads(l)for l in path.read_text().splitlines()]
    assert es[0]['schema']=='di3_locomotion_source_v1'
    prefixes=match(path,output.with_suffix('.prefixes.json'))
    candidates={m['key']:m['candidates']for m in prefixes['matches']}
    first={};timeline=[]
    for e in es:
        if e['event']!='clip_sample':continue
        key=str(e.get('asset'))+':'+str(e.get('blob'))
        identity=(e['object'],key)
        if identity in first:continue
        first[identity]=True
        timeline.append(dict(sequence=e['sequence'],elapsed_ms=e['elapsed_ms'],object=e['object'],source_key=key,
            candidates=[c['path']for c in candidates.get(key,[])]))
    dispatch=[]
    for e in es:
        if e['event'] not in ('group_dispatch','buffer_dispatch'):continue
        weight=struct.unpack('<f',bytes.fromhex(e['weight_hex4']))[0]
        dispatch.append(dict(sequence=e['sequence'],kind=e['event'],object=e['object'],
            child=e.get('child'),child_rtti_candidate=e.get('child_rtti_candidate'),weight=weight,mode=e['mode'],filter=e['filter'],caller=e.get('caller')))
    ranges=[]
    for m in prefixes['matches']:
        for c in m['candidates']:
            if 'idle_specific03'not in c['path']:continue
            clip=Clip(c['path'],PC_RIG);ports=(483,485,486,487,488,489,805,510,512,513,514,515,516,812)
            sampled=[clip.sample(clip.duration*i/120)for i in range(121)]
            ranges.append(dict(path=c['path'],duration=clip.duration,port_ranges={str(p):[min(s[p]['channels']['10'][0]for s in sampled),max(s[p]['channels']['10'][0]for s in sampled)]for p in ports}))
    report=dict(capture=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        counts=dict(collections.Counter(e['event']for e in es)),stop=es[-1],sources=prefixes['matches'],first_observed_sources=timeline,dispatch=dispatch,specific_idle_file_ranges=ranges,
        scope='Bounded observed native sampler and dispatch sites. Prefix candidates only; first-observed timestamps do not establish continuous activity or exact transition time. File ranges describe extracted clip, not live sample phase. Group/dispatcher records not paired as nested calls; no actor/thread identity, complete source selection or walk/run proof. Quotas can omit repeated activity; older probe versions also suppressed changed sources on reused objects.')
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report

if __name__=='__main__':
    r=analyze(sys.argv[1],sys.argv[2]if len(sys.argv)>2 else Path(__file__).parent/'ControllerState/live-locomotion-source-analysis-221612.json')
    print(json.dumps(dict(counts=r['counts'],sources=len(r['sources']),dispatch=len(r['dispatch']))))
