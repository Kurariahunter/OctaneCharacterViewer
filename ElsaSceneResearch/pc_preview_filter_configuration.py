"""Verified file-level defaults for the bounded viewer profiles."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).parent
EXPECTED='7955df9ef7d54621c39f65c5c50eede179627dd30d8853920439e7e4503b6d89'
def configuration(profile):
    entry={'grl_bm_turn45l':'TURN45L','grl_bm_turn45r':'TURN45R','grl_bm_turn90l':'TURN90L','grl_bm_turn90r':'TURN90R','grl_bm_turn180l':'TURN180L','grl_bm_turn180r':'TURN180R','elsa_bm_idle_active':'STANCE','elsa_bm_idle_passive':'STANCE_PASSIVE',
           'elsa_bm_idle_specific01':'IDLE_BREAKA','elsa_bm_idle_specific02':'IDLE_BREAKB','elsa_bm_idle_specific03':'IDLE_BREAKC',
           'grl_bm_runb':'WALKRUN','grl_bm_runrb':'WALKRUN','grl_bm_runlb':'WALKRUN','grl_bm_walkb':'WALKRUN','grl_bm_walklb':'WALKRUN','grl_bm_walkrb':'WALKRUN','grl_bm_walkf':'WALKRUN','grl_bm_runf':'WALKRUN','grl_bm_runrf':'WALKRUN','grl_bm_runr':'WALKRUN'}[profile]
    bent=ROOT/'InstalledGameAssetCheck/Bent/fro_elsa/fro_elsa.bent'
    if hashlib.sha256(bent.read_bytes()).hexdigest()!=EXPECTED:
        raise ValueError('Preview BENT changed; reassess source configuration')
    audit=json.loads((ROOT/'AuthoredFilters/layer-filter-assignment-audit.json').read_text(encoding='utf-8'))
    if audit['bent_sha256']!=EXPECTED:raise ValueError('Stale source assignment audit')
    row=next((r for r in audit['selected_entries'] if r['file_entry']==entry),None)
    if row is None:
        # Inspect the pinned BENT itself for newly enabled single-file idle entries.
        from read_pc_idle_files import tuple_decode
        records=tuple_decode(bent.read_bytes())['records']
        start=next(i for i,r in enumerate(records) if r['name']=='File' and r['value']==entry)
        depth=records[start]['depth'];end=start+1
        while end<len(records) and records[end]['depth']>depth:end+=1
        children=records[start+1:end]
        filename=next(r['value'] for r in children if r['name']=='Filename')
        if Path(filename).stem!=profile:raise ValueError('BENT clip/profile mismatch')
        row=dict(filename=filename,filter_declarations=[r for r in children if r['name']=='Filter'],
                 layer_declarations=[r for r in children if r['name'] in ('Layers','Layer')])
    if row['filter_declarations'] or row['layer_declarations']:
        raise ValueError('Explicit filters/layers require a new configuration profile')
    return {'file_entry':entry,'source_filename':row['filename'],'bent_sha256':EXPECTED,
            'configuration_row_count':1,'filter_name':'','mirror_name':'',
            'selected_filter':None,'default_filter_coefficient':1.0,
            'evidence':'Native absent/empty Layers loader window, default-row constructor and empty-name filter resolver',
            'scope':'Selected file entry default only; concurrent runtime controllers and dynamic weights remain outside this evidence.'}
