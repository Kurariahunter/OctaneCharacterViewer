import sys,json,collections,hashlib
from pathlib import Path
sys.path.insert(0,'F:/DisneyInfinityPortalTest/TupleDecoderResearch')
from decode_tup_safe import decode
p=next(Path('InstalledGameAssetCheck').rglob('fro_elsa.oct'));b=p.read_bytes();doc=decode(b);print('FILE',p,len(b),hashlib.sha256(b).hexdigest());root={'name':'Root','value':None,'children':[]};stack=[root]
for x in doc['records']:
 n=dict(x,children=[]);stack=stack[:x['depth']];stack[-1]['children'].append(n);stack.append(n)
def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
def get(n,k):return next((x['value'] for x in n['children'] if x['name']==k),None)
procs=[x for x in walk(root) if x['name']=='ProcessorNode'];print('PROCESSOR TYPES',collections.Counter(get(x,'Type') for x in procs).most_common(15))
for x in procs:
 if any(k in str(get(x,'Type')) for k in ['IK','IkLean','Ik2Link']):print('IK',json.dumps(x))
Path('installed-elsa-model-graph.json').write_text(json.dumps(root));Path('installed-elsa-asset-comparison.json').write_text(json.dumps({'installed_oct_path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'old_oct_sha256':'126ec007bafe36a24799b30e56f57e4d58da15698607dcfc06097c580928f4d2','processor_types':dict(collections.Counter(get(x,'Type') for x in procs))},indent=2))
