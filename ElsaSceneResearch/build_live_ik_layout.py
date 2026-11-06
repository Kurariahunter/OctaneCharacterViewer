import struct,json
from pathlib import Path
from exe_reader import b,base,sections
from evaluate_elsa_head import N,DN,get,allnodes
p=next(p for p in allnodes(N,'ProcessorNode') if int(p['value'])==412)
pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))[:13];order=[12,2,1,10,3,8,9,7,6,5,4,0,11];rows=[]
for slot,j in enumerate(order):
 attr,node=pairs[j];typ=get(DN[node],'Type');rows.append({'slot':slot,'source_attribute':attr,'kind':typ,'float_count':4 if typ in ('Rotor','Scale') else 1 if typ=='Float' else 3})
vts=[];start=0
while True:
 o=b.find(struct.pack('<I',0x53b620),start)
 if o<0:break
 start=o+1;v=next(base+r+o-p for r,s,p in sections if p<=o<p+s)
 if 0x1b00000<v<0x1c00000:vts.append(v-64)
d={'execute_static':0x53b620,'vtables_static':vts,'inputs':rows,'outputs':['MidRotation','StartRotation','MidScale','StartScale'],'scope':'Runtime layout corroborated by prior native Elsa IK fixtures; live source ownership unproven.'}
Path('F:/DisneyInfinityPortalTest/OctaneLiveInspector/ik_layout.json').write_text(json.dumps(d,indent=2));print(d)

