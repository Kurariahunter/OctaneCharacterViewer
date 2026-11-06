"""Audit observed scalar pass-through; do not infer general blender behavior."""
import hashlib
import json
import struct
from pathlib import Path
from analyze_final_hand_capture import analyze

ROOT = Path(__file__).resolve().parent
CAPTURE = ROOT.parent / 'OctaneLiveInspector/Captures/ce_finalhand_20261020_002459_89558703.jsonl'

def audit():
    report = analyze(CAPTURE, ROOT / 'ControllerState/live-final-hand-analysis.json')
    reference = json.loads((ROOT / 'ControllerState/output-bridge-run-hand-comparison.json').read_text())
    expected = {}
    for row in reference['rows']:
        if row['processor'] == '0x090BCA00':
            for c in row['comparisons']:
                if c['port'] in expected:
                    assert expected[c['port']] == c['expected']
                expected[c['port']] = c['expected']
    events = [json.loads(line) for line in CAPTURE.read_text().splitlines()]
    by_sequence = {e['sequence']: e for e in events if 'sequence' in e}
    checks = []
    for pair in report['pairs']:
        assert len(pair['contributors']) == 1
        c = pair['contributors'][0]
        event = by_sequence[pair['after_sequence']]
        raw_source = next(iter(event['contributions'].values()))['source']['payload_hex4']
        raw_output = event['output']['payload_hex4']
        checks.append(dict(port=c['port'], sequence=pair['after_sequence'],
            source_producer=c['source_producer'], source_node=c['source_node'], output_node=pair['output_node'],
            source_output_byte_exact=bytes.fromhex(raw_source) == bytes.fromhex(raw_output),
            prior_preview_value_byte_exact=bytes.fromhex(raw_output) == struct.pack('<f', expected[c['port']]),
            caches_fresh=all((pair['output_fresh'], c['source_fresh'], c['factor2c_fresh'], c['factor30_fresh'])),
            unit_factors=c['factor2c'] == c['factor30'] == c['filter_coefficient'] == 1.,
            value=pair['final_value']))
    result = dict(capture=str(CAPTURE), sha256=hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
        pairs=len(checks), ports=sorted({c['port'] for c in checks}), rejected=report['rejected'],
        exact_source_outputs=sum(c['source_output_byte_exact'] for c in checks),
        exact_prior_preview_values=sum(c['prior_preview_value_byte_exact'] for c in checks),
        all_caches_fresh=all(c['caches_fresh'] for c in checks),
        all_unit_factors=all(c['unit_factors'] for c in checks), checks=checks,
        scope='Observed single-source native Float blender outputs only. Prior preview comparison is across captures, not a synchronized end-to-end replay. No general multi-source blender, actor identity, relationship-to-world, or final skin palette proof.')
    (ROOT / 'ControllerState/final-hand-value-audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result

if __name__ == '__main__':
    r = audit()
    print(json.dumps({k:v for k,v in r.items() if k not in ('checks', 'scope', 'capture')}))
