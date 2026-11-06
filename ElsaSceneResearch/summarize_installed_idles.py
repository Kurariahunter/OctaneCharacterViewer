import json
from pathlib import Path
r=json.loads(Path('installed-elsa-idle-comparison.json').read_text());print('Installed idle assets',len(r))
for x in r:
 if 'elsa_bm' in x['installed_file']:print(x['installed_file'],x['bytes'],'oldmatch',x['exact_match'])
