import json
from pathlib import Path
from evaluate_elsa_head import DN,get,stored
from decode_elsa_static_channels import decode
r=Path('.');a=json.loads((r/'dress-reference-dependency-audit.json').read_text());m=json.loads((r/'elsa-control-mapping.json').read_text())
for row in a['clips']:
 name=row['clip'].split('_Hips')[0];missing={x['port']:x for x in row['unselected_bindings']};b=(r/(name+'.clipdata.bin')).read_bytes();layout=json.loads((r/(name+'-decoded-curves.json')).read_text());found=[]
 for t in decode(b,layout)['tracks']:
  if t['port'] in missing:
   binding=missing[t['port']];record={'binding':binding,'track':t,'stored':stored(DN[binding['data_node']]).tolist()};found.append(record);print(name,binding['data_node'],record['stored'],t)
 row['unselected_constant_records']=found
 clip=next(c for c in m['idle_clips'] if Path(c['file']).stem==name)
 row['unselected_timed_records']=[c for c in clip['commands'] if c['model_control']['data_node'] in {x['data_node'] for x in missing.values()}]
 print('TIMED',row['unselected_timed_records'])
(r/'dress-reference-dependency-audit.json').write_text(json.dumps(a,indent=2))
