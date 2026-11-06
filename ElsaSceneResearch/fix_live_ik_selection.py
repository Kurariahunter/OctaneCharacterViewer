from pathlib import Path
p=Path('validate_live_ik_replay.py');s=p.read_text().replace("if not set(x['network_reference_raw'] for x in candidate['outputs']) & networks:continue", "if not any(any(bytes.fromhex(x['payload_hex'])) for x in candidate['inputs'] if x['source_attribute']=='InputTargetTranslation'):continue")
s=s.replace("row={'address':candidate['address'],", "row={'address':candidate['address'],'shares_updating_chain_network':bool(set(x['network_reference_raw'] for x in candidate['outputs']) & networks),")
s=s.replace('Shared updating-chain network reference establishes instance association; source side matched by exact initial geometry signatures.', 'Network references compared explicitly; lack of a shared reference leaves actor association unresolved. Source side candidates use exact initial geometry signatures.')
p.write_text(s)
