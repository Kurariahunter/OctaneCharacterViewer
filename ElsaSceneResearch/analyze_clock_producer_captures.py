"""Interpret only the four-byte payload established by captured typed-node RTTI."""
import hashlib,json,struct,sys
from pathlib import Path
from analyze_runtime_map_capture import analyze
results=[]
for arg in sys.argv[1:]:
    p=Path(arg);raw=p.read_bytes();events=[json.loads(l) for l in raw.decode('utf-8').splitlines() if l.strip()]
    mapping=analyze(events);nodes={};state_checks=[]
    for event in events:
        for c in event.get('contributions',{}).values():
            state=c.get('controller_state',{});clock_inputs=state.get('clock_inputs',{})
            if state.get('state_header_hex128') and 'input_0' in clock_inputs and 'input_1' in clock_inputs:
                h=bytes.fromhex(state['state_header_hex128'])
                clock=struct.unpack('<f',bytes.fromhex(clock_inputs['input_0']['payload_hex20'])[:4])[0]
                token=struct.unpack('<I',bytes.fromhex(clock_inputs['input_1']['payload_hex20'])[:4])[0]
                state_checks.append({'clock_match':struct.unpack_from('<f',h,0x50)[0]==clock,
                                     'update_token_match':struct.unpack_from('<I',h,0x5c)[0]==token,
                                     'clock_lag':clock-struct.unpack_from('<f',h,0x50)[0],
                                     'token_lag':token-struct.unpack_from('<I',h,0x5c)[0]})
            for slot,n in clock_inputs.items():
                key=(slot,n['node']);g=nodes.setdefault(key,{'slot':slot,'node':n['node'],
                   'type':n.get('node_rtti_candidate'),'producer':n.get('producer'),
                   'observations':0,'samples':[]})
                assert g['producer']==n.get('producer') and g['type']==n.get('node_rtti_candidate')
                payload=bytes.fromhex(n['payload_hex20'])[:4]
                typ=g['type']
                if typ=='.?AV?$TypedDataNode@M@Samurai@@':value=struct.unpack('<f',payload)[0]
                elif typ=='.?AV?$TypedDataNode@I@Samurai@@':value=struct.unpack('<I',payload)[0]
                else:raise ValueError('Unknown clock input RTTI; do not assume float')
                g['observations']+=1
                if not g['samples'] or g['samples'][-1]['value']!=value:
                    g['samples'].append({'sequence':event.get('sequence'),'elapsed_ms':event.get('elapsed_ms'),'value':value})
    for g in nodes.values():
        g['value_changes']=[b['value']-a['value'] for a,b in zip(g['samples'],g['samples'][1:])]
    results.append({'capture':str(p.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),
                    'mapping_checks':{'checked':mapping['checked_contributions'],'matching':mapping['matching'],'errors':mapping['errors']},
                    'nodes':list(nodes.values()),'stop':events[-1],
                    'state_checks':{'observations':len(state_checks),
                                    'cached_clock_matches':sum(c['clock_match'] for c in state_checks),
                                    'cached_update_token_matches':sum(c['update_token_match'] for c in state_checks),
                                    'lag_pairs':sorted(set((c['clock_lag'],c['token_lag']) for c in state_checks))},
                    'scope':'RTTI establishes float and unsigned-int payload widths. Null producers mean values are externally supplied at observation time. Only first four payload bytes interpreted; remaining captured bytes can include padding/adjacent allocations. Float time units and integer counter semantics remain unverified.'})
out=Path(__file__).parent/'ControllerState/clock-producer-capture-analysis.json'
out.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
for result in results:print(json.dumps(result))
