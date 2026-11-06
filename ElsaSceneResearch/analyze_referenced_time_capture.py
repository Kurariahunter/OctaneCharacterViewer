"""Compare bounded runtime child rows with source-file samples at observed time."""
import collections,json,math,struct,sys
from pathlib import Path
from types import SimpleNamespace
from match_live_clip_prefixes import match
from pc_skin_palette import PC_RIG
from read_pc_idle_files import Clip,walk,get,shorts,tuple_decode
from inspect_pc_run_lean import read_static

def analyze(path,output):
    path=Path(path);output=Path(output);es=[json.loads(l)for l in path.read_text().splitlines()]
    assert es[0]['schema']=='di3_referenced_time_v1'
    prefixes=match(path,output.with_suffix('.prefixes.json'));sources={m['key']:m['candidates']for m in prefixes['matches']}
    byseq={e['sequence']:e for e in es if 'sequence'in e}
    ports=shorts(get(next(n for n in walk(PC_RIG.net)if n['name']=='BaseDataNodeLinks'),'LocalToPortIndices'))
    indices={p:i for i,p in enumerate(ports)};clips={};checks=[];boundaries=[]
    for e in es:
        if e['event']!='group_dispatch':continue
        try:
            candidates=sources.get(e['asset']+':'+e['blob'],[])
            if len(candidates)!=1:raise ValueError('No unique extracted source candidate')
            source=candidates[0]['path']
            if source not in clips:
                if 'lean_add'in source:
                    v=next(r['value']for r in tuple_decode(Path(source).read_bytes())['records']if r['name']=='ClipDataBlock')
                    blob=bytes(v)if isinstance(v,list)else bytes.fromhex(v['hex'])
                    records={r['port']:dict(channels={str(d['opcode']):d['values']for d in r['descriptors']})for r in read_static(blob)['tracks']}
                    clips[source]=SimpleNamespace(duration=math.inf,sample=lambda t,records=records:records)
                else:clips[source]=Clip(source,PC_RIG)
            clip=clips[source];latest=e['latest_sample_observation'];s=byseq[latest['sequence']]
            assert s['event']=='referenced_sample' and s['track']==e['track'] and s['blob']==e['blob'] and s['asset']==e['asset']
            assert s['sequence']<e['sequence'] and s['time_hex4']==latest['time_hex4']
            t=struct.unpack('<f',bytes.fromhex(s['time_hex4']))[0]
            assert math.isfinite(t) and 0<=t<=clip.duration,'Time outside file range'
            assert e['row_count']==len(ports),'Buffer row extent differs from file rig map'
            b=bytes.fromhex(e['rows_hex52']);assert len(b)==52*len(ports)
            rows=[]
            for port,record in clip.sample(t).items():
                if port not in indices:continue
                values=struct.unpack_from('<12fI',b,52*indices[port]);mask=values[-1]
                for op,v in record['channels'].items():
                    if op=='10':start,width,flag=0,1,1
                    elif op=='0':start,width,flag=1,3,14
                    elif op in ('1','2','3'):start,width,flag=int(op),1,1<<int(op)
                    elif op=='4':start,width,flag=8,4,256
                    else:continue
                    if mask&flag!=flag:
                        rows.append(dict(port=port,opcode=op,missing_mask=True,mask=mask));continue
                    actual=values[start:start+width];assert all(map(math.isfinite,actual))
                    error=max(abs(a-x)for a,x in zip(actual,v))
                    rows.append(dict(port=port,opcode=op,error=error,mask=mask))
            errors=[r['error']for r in rows if 'error'in r]
            checks.append(dict(sequence=e['sequence'],sample_sequence=s['sequence'],track=e['track'],source=source,time=t,
                elapsed_gap_ms=e['elapsed_ms']-s['elapsed_ms'],comparisons=len(errors),missing_masks=sum(r.get('missing_mask',False)for r in rows),
                max_error=max(errors,default=None),rows=rows))
        except (KeyError,AssertionError,ValueError,TypeError) as ex:
            boundaries.append(dict(sequence=e['sequence'],reason=str(ex)))
    result=dict(capture=str(path.resolve()),checks=checks,boundaries=boundaries,
        compared_channels=sum(c['comparisons']for c in checks),
        checked_subset_matches=bool(checks) and all(c['comparisons']>0 and c['missing_masks']==0 and c['max_error']<=2e-5 for c in checks),
        scope='Observed sample time paired by track/source/latest sequence, not thread or call-stack identity. Uses file-derived112-row biped map; runtime row mapping not captured independently here. Scalar/translation/rotation only. Static lean separate. Child buffer before outer blend; no full graph or palette parity.')
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');return result

if __name__=='__main__':
    r=analyze(sys.argv[1],Path(__file__).parent/'ControllerState/live-referenced-time-analysis-223229.json')
    print(json.dumps(dict(checked=len(r['checks']),boundaries=collections.Counter(x['reason']for x in r['boundaries']),
        sources={Path(c['source']).name:[(x['comparisons'],x['missing_masks'],x['max_error'])for x in r['checks']if x['source']==c['source']]for c in r['checks']})))
