import json,struct
from pathlib import Path
from evaluate_elsa_head import N,DN,get,allnodes
d=json.loads(Path('F:/DisneyInfinityPortalTest/OctaneLiveInspector/Captures/octane_20261017_000852_1792210132334652700.json').read_text())
for p in allnodes(N,'ProcessorNode'):
 if get(p,'Type')=='IK2BRPLengthSquashZConstraint':print('SOURCE',p['value'],[(a,get(DN[i],'Data')) for a,i in zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')) if 'InitialPosition' in a])
for c in d['ik_candidates'][:2]:print('LIVE',c['address'],[(x['source_attribute'],struct.unpack('<'+'f'*x['float_count'],bytes.fromhex(x['payload_hex']))) for x in c['inputs'] if 'InitialPosition' in x['source_attribute']])
