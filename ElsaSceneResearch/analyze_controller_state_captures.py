"""Summarize controller state and cross-check authored coefficients in live logs."""
import collections,hashlib,json,struct,sys
from pathlib import Path
from analyze_runtime_map_capture import analyze
ROOT=Path(__file__).parent
filters=json.loads((ROOT/'AuthoredFilters/biped-filters.json').read_text(encoding='utf-8'))['filters']
results=[]
for arg in sys.argv[1:]:
    p=Path(arg);raw=p.read_bytes();events=[json.loads(l) for l in raw.decode('utf-8').splitlines() if l.strip()]
    maps=analyze(events);owners={e['map_key']:e.get('owner_name') for e in events if e.get('event')=='runtime_map'}
    groups={};coefficient_checks=[]
    for event in events:
        for c in event.get('contributions',{}).values():
            state=c.get('controller_state',{});names=state.get('configuration_names',{})
            key=(c.get('controller'),state.get('source_asset'),state.get('configuration_index'),names.get('Filter'))
            g=groups.setdefault(key,{'controller':key[0],'source_asset':key[1],'configuration_index':key[2],
               'configuration_names':names,'controller_type':state.get('controller_rtti_candidate'),
               'source_type':state.get('source_rtti_candidate'),'resolved_type':state.get('resolved_rtti_candidate'),
               'mapping_owner':owners.get(c.get('mapping_key')),'contributions':0,'state_samples':[]})
            g['contributions']+=1
            if state.get('state_header_hex128'):
                g['state_samples'].append({'sequence':event.get('sequence'),'elapsed_ms':event.get('elapsed_ms'),
                                          'hex':state['state_header_hex128']})
            name=names.get('Filter');payload=c.get('weight_hex4');port=c.get('weight_index')
            if name in filters and payload and g['mapping_owner']=='characters/biped/biped.ct':
                actual=struct.unpack('<f',bytes.fromhex(payload))[0]
                expected=filters[name][port] if 0<=port<len(filters[name]) else None
                coefficient_checks.append({'filter':name,'port':port,'actual':actual,'expected':expected,
                                           'match':actual==expected})
    for g in groups.values():
        samples=g.pop('state_samples');g['raw_state_sample_count']=len(samples)
        g['raw_state_fields']={}
        for offset in [0x50,0x54]:
            vals=[struct.unpack_from('<f',bytes.fromhex(s['hex']),offset)[0] for s in samples]
            if vals:g['raw_state_fields'][hex(offset)]={'min':min(vals),'max':max(vals),'distinct':len(set(vals))}
        g['state_field_status']='Observed float interpretations only; time/phase semantics not verified'
    summary={'capture':str(p.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),
             'stop':events[-1],'mapping_checks':{'matching':maps['matching'],'checked':maps['checked_contributions'],'errors':maps['errors']},
             'controllers':list(groups.values()),'authored_coefficient_checks':coefficient_checks,
             'coefficient_matches':sum(r['match'] for r in coefficient_checks),
             'scope':'Controller/source/config identity and selected coefficient reads, not unique actor identity, frame scheduling or full cycle timing. Captured RTTI is reported verbatim.'}
    results.append(summary)
out=ROOT/'ControllerState/controller-capture-analysis.json'
out.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
for r in results:
    print(json.dumps({'file':Path(r['capture']).name,'mapping':r['mapping_checks'],
                      'groups':len(r['controllers']),'authored_coefficients':len(r['authored_coefficient_checks']),
                      'coefficient_matches':r['coefficient_matches']}))
