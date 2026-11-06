"""Check exact-node scalar observations at relationship exits in one capture."""
import json
import sys
from pathlib import Path

def analyze(path, output):
    events = [json.loads(line) for line in Path(path).read_text().splitlines()]
    assert events[0]['schema'] == 'di3_hand_chain_v1'
    links = []
    for event in events:
        if event['event'] != 'relationship_exit':
            continue
        snapshot = event['snapshot']
        for slot, prior in snapshot['observed_scalar_links'].items():
            current = snapshot['inputs'][slot]
            same_bytes = bytes.fromhex(prior['payload_hex']) == bytes.fromhex(current['payload_hex'])
            same_stamp = prior.get('node_stamp') == current.get('node_stamp')
            fresh = current.get('node_stamp') is not None and current['node_stamp'] == current.get('metadata_stamp')
            prior_fresh = prior.get('node_stamp') is not None and prior['node_stamp'] == prior.get('metadata_stamp')
            producer_matches = current.get('producer') == prior.get('processor')
            ordered = 0 <= prior['elapsed_ms'] <= event['elapsed_ms']
            links.append(dict(sequence=event['sequence'], relationship=snapshot['processor'], slot=slot,
                node=current['node'], scalar_producer=prior['processor'],
                same_node=prior['node'] == current['node'], same_bytes=same_bytes,
                same_stamp=same_stamp, current_fresh=fresh, prior_fresh=prior_fresh,
                producer_matches=producer_matches, ordered=ordered,
                elapsed_ms=event['elapsed_ms']-prior['elapsed_ms'],
                exact_fresh_link=prior['node'] == current['node'] and same_bytes and same_stamp and fresh and prior_fresh and producer_matches and ordered))
    result = dict(capture=str(Path(path).resolve()), links=links,
        observed_links=len(links), exact_fresh_links=sum(row['exact_fresh_link'] for row in links),
        scope='Same-capture cached scalar-to-relationship links. Requires separate relationship hash/native replay checks. No thread identity, nesting or final skin proof.')
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result

if __name__ == '__main__':
    r=analyze(sys.argv[1], Path(__file__).parent/'ControllerState/live-hand-chain-links.json')
    print(json.dumps({k:v for k,v in r.items() if k != 'links'}))
