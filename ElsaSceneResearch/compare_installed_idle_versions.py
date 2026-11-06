import zipfile,hashlib,json
from pathlib import Path
r=Path('.');rows=[]
with zipfile.ZipFile('G:/Downloads/fro_elsa.zip') as z:
 for p in (r/'InstalledGameAssetCheck/IdleMotions').rglob('*.oct'):
  matches=[n for n in z.namelist() if Path(n).name==p.name]
  a=hashlib.sha256(p.read_bytes()).hexdigest();old=[{'name':n,'bytes':len(z.read(n)),'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in matches]
  rows.append({'installed_file':str(p),'bytes':p.stat().st_size,'sha256':a,'downloaded_matches':old,'exact_match':any(x['sha256']==a for x in old)})
(r/'installed-elsa-idle-comparison.json').write_text(json.dumps(rows,indent=2));print(rows)
