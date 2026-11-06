"""Validate isolated index captures with explicit identity limits."""
import collections,hashlib,json,struct,sys
from pathlib import Path
import numpy as np
from native_pc_dress_math import call
from native_pc_skin_matrix import dilation_matrix
ROOT=Path(__file__).resolve().parent
known={r['sha256']:r['processor']for r in json.loads((ROOT/'pc-finger-native-probe.json').read_text())['relationships']}
def values(n):
 assert n.get('node_stamp')is not None and n['node_stamp']==n.get('metadata_stamp'),'Stale node'
 b=bytes.fromhex(n['payload_hex']);return list(struct.unpack('<'+'f'*(len(b)//4),b))
def same(a,b):
 assert a['node']==b['node']and a['producer']==b['producer'],'Node/producer changed'
 assert a['node_stamp']==b['node_stamp']and bytes.fromhex(a['payload_hex'])==bytes.fromhex(b['payload_hex']),'Bytes/stamp changed'
def analyze(path):
 es=[json.loads(l)for l in path.read_text().splitlines()];assert es[0]['schema']=='di3_isolated_index_v1'
 seeds={};worlds={};checks=[];bad=[];scalars=[]
 for e in es:
  k=e['event']
  if k in ('start','stop'):continue
  try:
   if k=='relationship_seed':
    pid=known[hashlib.sha256(bytes.fromhex(e['relationship_blob_hex'])).hexdigest()]
    for n in e['outputs'].values():assert len(values(n))==8 and n['producer']==e['processor']
    seeds[e['sequence']]=(e,pid)
    for slot,n in e['inputs'].items():
     v=values(n)[0];link=e.get('scalar_links',{}).get(slot);matched=False
     if link:
      same(link['snapshot'],n);values(link['snapshot']);matched=True
     scalars.append(dict(sequence=e['sequence'],elapsed_ms=e['elapsed_ms'],pid=pid,slot=slot,value=v,linked=matched,contributors=link['contributors']if link else {}))
    continue
   tag=e['source_tag'];seed,pid=seeds[tag['seed_sequence']];local=seed['outputs']['slot_'+str(tag['slot'])]
   if k=='finger_world_transform':
    same(local,e['left']);pred=call(0x57cb30,[values(e['left']),values(e['right'])],'array',16);actual=values(e['output']);worlds[e['sequence']]=e
    error=max(abs(a-b)for a,b in zip(pred,actual))
   elif k=='finger_matrix':
    same(local,e['local_input']);w=worlds[e['converter_tag']['event_sequence']]
    assert w['source_tag']['seed_sequence']==tag['seed_sequence']and w['source_tag']['slot']==tag['slot']-1
    same(w['output'],e['converter'])
    pred=call(0x4d78d0,[values(e['local_input']),values(e['converter'])],'typed',8)
    actual=values(e['input']);err1=max(abs(a-b)for a,b in zip(pred,actual))
    packed=dilation_matrix(actual);err2=max(abs(a-b)for a,b in zip(packed,values(e['output'])))
    error=max(err1,err2)
   else:raise ValueError('Unknown event')
   checks.append(dict(sequence=e['sequence'],stage=k,pid=pid,slot=tag['slot'],max_error=error))
  except (AssertionError,KeyError,ValueError,TypeError)as ex:bad.append(dict(sequence=e['sequence'],reason=str(ex)))
 grouped=collections.defaultdict(list)
 for s in scalars:grouped[(s['pid'],s['slot'])].append(s['value'])
 report=dict(capture=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),seeds=len(seeds),checks=checks,rejected=bad,
  scalar_links=sum(s['linked']for s in scalars),scalar_observations=len(scalars),scalars=scalars,
  ranges=[dict(pid=p,slot=s,min=min(v),max=max(v),unique=len(set(v)))for(p,s),v in grouped.items()],
  max_error=max((c['max_error']for c in checks),default=None),pass_=bool(checks)and not bad and all(c['max_error']<=2e-5 for c in checks),
  scope='Hash-identified hand relationships, scalar links and continuous native world/matrix operations. Map owner is generic biped class; not independent Elsa renderer identity. Scene isolation supplied by user.')
 out=ROOT/'ControllerState'/('isolated-index-'+path.stem+'.json');out.write_text(json.dumps(report,indent=2),encoding='utf-8')
 return report
if __name__=='__main__':
 for name in sys.argv[1:]:
  r=analyze(Path(name));print(json.dumps({k:r[k]for k in ('capture','seeds','scalar_links','scalar_observations','max_error','pass_','rejected','ranges')}))
