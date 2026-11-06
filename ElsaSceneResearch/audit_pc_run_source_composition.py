"""File-derived PC walk/run composition audit, not runtime active-layer reconstruction."""
import json,hashlib
from pathlib import Path
from read_pc_idle_files import R,tuple_decode,tree,walk
from pc_banm_declarations import parse,descendants

def audit():
 bent=R/'InstalledGameAssetCheck/Bent/fro_elsa/fro_elsa.bent'
 banm=next((R/'InstalledGameAssetCheck/RunMotions').rglob('grl_bm_walkrun.banm'))
 root=tree(tuple_decode(bent.read_bytes())['records']);ast=parse(banm.read_text(encoding='utf-8-sig'))
 files=[n for n in walk(root)if n['name']=='File'];entry=next(n for n in files if n['value']=='WALKRUN');entryfields={c['name']:c['value']for c in entry['children']}
 if entryfields['Filename']!='characters/class_girl/motions/grl_bm_walkrun.banm':raise ValueError('source graph changed')
 groups=[]
 for n in descendants(ast):
  if n['field']!='GroupTrack':continue
  tracks=[]
  for child in descendants(n.get('children',[])):
   if child['field']=='ReferencedTrack':
    fields={c['field']:c.get('value')for c in child['children']}
    if any(c['field']not in ['Filename','Weight','BlendMethod']for c in child['children']):raise ValueError('unknown source reference field')
    tracks.append({'filename':fields['Filename'],'explicit_weight':fields.get('Weight'),'explicit_blend_method':fields.get('BlendMethod'),'line':child['line']})
  groups.append({'name':n['label'],'line':n['line'],'tracks':tracks})
 forwards=[g for g in groups if g['name']in ('Run Forward','Run Forward2')]
 if len(forwards)!=2:raise ValueError('unexpected forward groups')
 expected=['characters/class_girl/motions/grl_bm_runf.oct','characters/class_girl/motions/grl_bm_run_upbody_add.oct','characters/human/motions/human_bm_runf_lean_add.oct']
 for group in forwards:
  if [t['filename']for t in group['tracks']]!=expected:raise ValueError('unexpected forward sequence')
  if group['tracks'][2]['explicit_blend_method']!=1 or group['tracks'][2]['explicit_weight']not in (None,1):raise ValueError('lean declaration changed')
 filters=[]
 for file in files:
  for n in walk(file):
   if n['name']=='Filter':filters.append({'file':file['value'],'filter':n['value'],'offset':n['offset']})
 keytracks=[]
 for n in descendants(ast):
  if n['field']=='KeyBlendTrack':
   fields={c['field']:c.get('value')for c in n['children']if c['field']!='Tracks'}
   keytracks.append({'name':n['label'],'line':n['line'],'value_parameter':fields.get('Value'),'keys':fields.get('Keys')})
 report={'scope':'Verified PC serialized declarations only. No active-game selection, phase mapping, filter coefficients or default weight semantics inferred.','bent_path':str(bent),'bent_sha256':hashlib.sha256(bent.read_bytes()).hexdigest(),'banm_path':str(banm),'banm_sha256':hashlib.sha256(banm.read_bytes()).hexdigest(),'walkrun_entry':entry,'key_tracks':keytracks,'groups':groups,'run_forward_groups':forwards,'filter_references':filters,'unique_filter_names':sorted({x['filter']for x in filters}),'walkrun_has_explicit_filter':any(n['name']=='Filter'for n in walk(entry)),'fixture_assumptions':['Speed and Direction runtime values not captured for an identified Elsa actor.','Absent reference Weight remains unspecified here; viewer currently uses unit-weight source assignments.','Passive idle is explicitly applied as a control initializer by our bake; its coexistence with run in-game is unproved.','Clip phase/time mapping and motion-rate metadata use in-game remain unresolved.','Filter names are references; coefficients and native application are not reconstructed.']}
 return report
if __name__=='__main__':
 report=audit();(R/'pc-run-source-composition.json').write_text(json.dumps(report,indent=2));print(json.dumps({'groups':len(report['groups']),'forward_groups':len(report['run_forward_groups']),'filter_references':len(report['filter_references']),'unique_filters':len(report['unique_filter_names']),'walkrun_explicit_filter':report['walkrun_has_explicit_filter'],'forward_tracks':report['run_forward_groups'][0]['tracks']},indent=2))

