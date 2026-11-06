"""Check per-controller map snapshots against packed native blend contributions."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

def table_values(table):
    if not table.get('complete'):
        raise ValueError('Mapping table capture is incomplete')
    count=table.get('count')
    if not isinstance(count,int) or not 0<=count<=4096:
        raise ValueError('Invalid mapping table count')
    raw=bytes.fromhex(table['hex'])
    if len(raw)!=count*2:
        raise ValueError('Mapping table byte count does not match element count')
    return list(struct.unpack('<'+'H'*count,raw))

def analyze(events):
    maps={};checks=[];errors=[]
    for event in events:
        if event.get('event')=='runtime_map':
            key=event['map_key']
            if key in maps:
                errors.append({'map_key':key,'error':'Duplicate first-seen map key'})
                continue
            try:
                tables={name:table_values(event['tables'][name]) for name in
                        ['LocalUsedDataNodeIndices','LocalToPortIndices','PortToLocalIndices']}
                forward=tables['LocalToPortIndices'];reverse=tables['PortToLocalIndices']
                if len(forward)!=len(tables['LocalUsedDataNodeIndices']):
                    raise ValueError('Local mapping lengths differ')
                mismatches=[{'slot':s,'port':p} for s,p in enumerate(forward)
                            if p!=65535 and (p>=len(reverse) or reverse[p]!=s)]
                maps[key]={'controller':event['controller'],'mapping':event['mapping'],
                           'owner':event.get('owner'),'owner_name':event.get('owner_name'),
                           'tables':tables,'inverse_mismatches':mismatches}
            except (ValueError,KeyError,TypeError) as exc:
                errors.append({'map_key':key,'error':str(exc)})
        elif event.get('event')=='blend':
            for contribution in event.get('contributions',{}).values():
                key=contribution.get('mapping_key');mapping=maps.get(key)
                check={'map_key':key,'controller':contribution.get('controller'),
                       'sequence':event.get('sequence')}
                if mapping is None:
                    check['status']='missing_or_incomplete_map'
                elif mapping['controller']!=contribution.get('controller'):
                    check['status']='controller_mismatch'
                else:
                    word=int(contribution['packed_word'],16)
                    slot,port=word&4095,(word>>12)&4095
                    forward=mapping['tables']['LocalToPortIndices']
                    # Native registration uses -1 for absent/sentinel entries;
                    # the native builder retains its low 12 bits (0xFFF).
                    source=forward[slot] if slot<len(forward) else 65535
                    expected=source&4095
                    check.update(source_slot=slot,packed_filter_index=port,
                                 serialized_port=source,expected_packed_index=expected)
                    check['status']='match' if expected==port else 'packed_map_mismatch'
                checks.append(check)
    return {'maps':maps,'checks':checks,'errors':errors,
            'matching':sum(c['status']=='match' for c in checks),
            'checked_contributions':len(checks),
            'scope':'Each contribution uses only its captured controller mapping. Owner names are unverified source hints, not actor identity. First-seen snapshots cannot detect later in-place mutations.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('capture',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    raw=args.capture.read_bytes()
    report=analyze([json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()])
    report['capture_sha256']=hashlib.sha256(raw).hexdigest()
    out=args.output or args.capture.with_name(args.capture.stem+'_map_analysis.json')
    if out.resolve()==args.capture.resolve():
        raise ValueError('Output cannot overwrite input capture')
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'maps':len(report['maps']),'matching':report['matching'],
                      'checked':report['checked_contributions'],'errors':report['errors'],
                      'output':str(out)}))
