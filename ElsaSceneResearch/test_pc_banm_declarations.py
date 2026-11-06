from pc_banm_declarations import parse,descendants
from audit_pc_run_source_composition import audit
from pathlib import Path
import json
sample='Version="1.0g" Tracks={ReferencedTrack={Weight=0.5 BlendMethod=1 Filename="a/b.oct"}}'
ast=parse(sample)
assert [n['value']for n in descendants(ast)if n['field']=='Weight']==[.5]
bad=['Tracks={','Tracks={ Value= }','Keys=[1 2','Foo="unterminated','Value=NaN','Tracks=@','Foo="a\\b"','}' , 'Value=1e999']
for text in bad:
 try:parse(text)
 except ValueError:pass
 else:raise AssertionError('bad declaration accepted: '+text)
report=audit();assert len(report['groups'])==18
assert all(len(k['keys'])==9 for k in report['key_tracks']if k['name']in ('Walk','Run'))
assert len(report['filter_references'])==88 and len(report['unique_filter_names'])==31
out={'pass':True,'malformed_inputs_rejected':len(bad),'groups':18,'direction_keys_per_branch':9,'filter_references':88,'unique_filters':31,'scope':'Text syntax/declarations and original file structure; not active-game scheduling'}
Path(__file__).with_name('pc-banm-declaration-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
