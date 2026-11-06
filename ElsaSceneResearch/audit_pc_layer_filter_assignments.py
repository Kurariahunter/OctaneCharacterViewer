"""Source declarations only: do not infer active layers or upstream inheritance."""
import json,hashlib
from pathlib import Path
from read_pc_idle_files import R,tuple_decode,tree,walk
from pc_banm_declarations import parse,descendants

bent=R/'InstalledGameAssetCheck/Bent/fro_elsa/fro_elsa.bent'
root=tree(tuple_decode(bent.read_bytes())['records'])
filters=json.loads((R/'AuthoredFilters/biped-filters.json').read_text(encoding='utf-8'))['filters']
assignments=[]
def visit(node,path=()):
    here=path+({'name':node['name'],'value':node.get('value'),'offset':node.get('offset')},)
    if node['name']=='Filter':
        owner=next((p for p in reversed(path) if p['name']=='File'),None)
        assignments.append({'file_entry':owner['value'] if owner else None,
                            'filter':node['value'],'resolved_in_biped_bct':node['value'] in filters,
                            'path':list(here)})
    for child in node.get('children',[]):visit(child,here)
visit(root)
selected=[]
for file in walk(root):
    if file['name']=='File' and file.get('value') in ['STANCE','STANCE_PASSIVE','WALKRUN']:
        selected.append({'file_entry':file['value'],'offset':file['offset'],
                         'filename':next(c['value'] for c in file['children'] if c['name']=='Filename'),
                         'filter_declarations':[n['value'] for n in walk(file) if n['name']=='Filter'],
                         'layer_declarations':[n.get('value') for n in walk(file) if n['name']=='Layer']})
banm=next((R/'InstalledGameAssetCheck/RunMotions').rglob('grl_bm_walkrun.banm'))
ast=parse(banm.read_text(encoding='utf-8-sig'))
references=[]
for node in descendants(ast):
    if node['field']=='ReferencedTrack':
        fields={c['field']:c.get('value') for c in node['children']}
        references.append({'track':node['label'],'line':node['line'],**fields})
assert len(assignments)==88 and all(a['resolved_in_biped_bct'] for a in assignments)
assert len(selected)==3 and all(not s['filter_declarations'] for s in selected)
assert not any(n['field']=='Filter' for n in descendants(ast))
report={'bent_sha256':hashlib.sha256(bent.read_bytes()).hexdigest(),
        'banm_sha256':hashlib.sha256(banm.read_bytes()).hexdigest(),
        'assignments':assignments,'selected_entries':selected,'walkrun_references':references,
        'walkrun_banm_has_filter_declaration':False,
        'scope':'File-derived explicit declarations only. STANCE, STANCE_PASSIVE and WALKRUN have no Filter declarations in their BENT entries; walkrun BANM has none either. This does not prove the absence of concurrent controllers, inherited configuration assembled upstream, or active runtime layers. Never apply a filter merely because a filename contains upbody.'}
(R/'AuthoredFilters/layer-filter-assignment-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'resolved_assignments':len(assignments),'selected_entries':selected,
                  'walkrun_reference_count':len(references),'walkrun_filter_declarations':0}))
