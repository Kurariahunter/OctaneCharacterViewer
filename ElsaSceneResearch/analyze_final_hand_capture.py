"""Describe mapped hand Float blender inputs/output without guessing blend rules."""
import collections,json,math,struct,sys
from pathlib import Path

def fl(n):
    raw=n.get('payload_hex4');return struct.unpack('<f',bytes.fromhex(raw))[0]if raw else None
def factor(n):return 1. if n.get('default_one')else fl(n)
def fresh(n):return n.get('node_stamp')is not None and n.get('node_stamp')==n.get('metadata_stamp')
def analyze(path,output):
    es=[json.loads(l)for l in Path(path).read_text().splitlines()];assert es[0]['schema']=='di3_final_hand_v1'
    pending={};pairs=[];rejected=[]
    for e in es:
        if e['event']=='scalar_before':
            if e['pair_key']in pending:raise ValueError('Ambiguous scalar entry')
            pending[e['pair_key']]=e
        elif e['event']in ('scalar_after','scalar_early'):
            before=pending.pop(e['pair_key'],None)
            try:
                assert before is not None,'Unpaired exit'
                assert before['processor']==e['processor']and before['sequence']==e['before_sequence']
                delta=0x50c if e['event']=='scalar_early'else 0x510
                assert int(before['stack'],16)-int(e['stack'],16)==delta,'Scalar frame mismatch'
                assert before['output']['node']==e['output']['node']and e['output']['producer']==e['processor']
                assert before['contribution_count']==e['contribution_count']
                contributors=[]
                for key,c in e['contributions'].items():
                    prior=before['contributions'][key];assert c['controller']==prior['controller']and c['slot']==prior['slot']and c['weight_index']==prior['weight_index']
                    source=c['source'];f2c=factor(c['factor2c']);f30=factor(c['factor30'])
                    coefficient=1. if c['filter_default_one']else(struct.unpack('<f',bytes.fromhex(c['filter_coefficient_hex4']))[0]if c.get('filter_coefficient_hex4')else None)
                    contributors.append(dict(controller=c['controller'],port=c.get('mapped_port'),source_node=source.get('node'),source_producer=source.get('producer'),
                        source_value=fl(source),source_fresh=fresh(source),factor2c=f2c,factor30=f30,filter_coefficient=coefficient,
                        factor2c_fresh=c['factor2c'].get('default_one',False)or fresh(c['factor2c']),factor30_fresh=c['factor30'].get('default_one',False)or fresh(c['factor30']),
                        priority=struct.unpack('<f',bytes.fromhex(c['priority_hex4']))[0],flag39=int(c['flag39_hex1'],16),packed_before=prior['packed_word'],packed_after=c['packed_word']))
                value=fl(e['output']);assert value is not None and math.isfinite(value),'Invalid final scalar'
                pairs.append(dict(before_sequence=before['sequence'],after_sequence=e['sequence'],processor=e['processor'],output_node=e['output']['node'],
                    mapped_ports=sorted({c['port']for c in contributors if c['port']is not None}),initial_value=fl(before['output']),final_value=value,
                    output_fresh=fresh(e['output']),exit_kind=e['event'],contributors=contributors))
            except (AssertionError,KeyError,ValueError,TypeError)as ex:rejected.append(dict(sequence=e['sequence'],reason=str(ex)))
    rejected.extend(dict(sequence=e['sequence'],reason='Unpaired entry at end')for e in pending.values())
    r=dict(capture=str(Path(path).resolve()),matched_pairs=len(pairs),pairs=pairs,rejected=rejected,
        scope='Observed final Float blender output and post-call cached source/factor states. Mapping reverse-checked by probe; no actor identity or full native scalar blend replay yet. Factors/priorities/flags reported separately; factor30 is not assumed a source weight.')
    Path(output).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');return r
if __name__=='__main__':
    r=analyze(sys.argv[1],Path(__file__).parent/'ControllerState/live-final-hand-analysis.json')
    print(json.dumps(dict(matched_pairs=r['matched_pairs'],rejected=r['rejected'],ports=sorted({p for r in r['pairs']for p in r['mapped_ports']}))))
