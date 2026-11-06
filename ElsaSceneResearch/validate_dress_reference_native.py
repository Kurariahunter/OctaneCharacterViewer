"""Native reference operators against matrix evaluator and source clip fixtures."""
import json,random,inspect,struct
import validate_foot_basis_native as fixture
from pathlib import Path
import numpy as np
from evaluate_elsa_head import DN,PROD,get
from evaluate_elsa_feet import rotor
from evaluate_dress import DressEval
from evaluate_native_skin import dilation
from validate_foot_basis_native import native,SPECS,matrix
from native_leg_ik import sha
SPECS.update({'InvertDilation':(0x4d19c0,'unary',8),'ConcatenateChainDilation':(0x4d1cb0,'array',8),'ConcatenateChainInverseDilation':(0x4d2b00,'array',8)})
# Mixed normal/inverse chain stores the normal-input count at processor+0x1c.
code=inspect.getsource(fixture.native).replace('def native(', 'def reference_native(').replace('try:u.emu_start', "if name=='ConcatenateChainInverseDilation':u.mem_write(proc+0x1c,struct.pack('<I',1))\n try:u.emu_start")
namespace=dict(vars(fixture));exec(code,namespace);native=namespace['reference_native']
rng=random.Random(20261016);tests=[]
for case in range(100):
 vals=[]
 for j in range(2):
  q=np.array([rng.uniform(-1,1) for _ in range(4)]);q/=np.linalg.norm(q);vals.append(q.tolist()+[rng.uniform(-2,2) for _ in range(3)]+[rng.uniform(.7,1.3)])
 a,b=vals;A,B=map(matrix,vals)
 for typ,expected in [('InvertDilation',np.linalg.inv(A)),('ConcatenateChainDilation',B@A),('ConcatenateChainInverseDilation',np.linalg.inv(B)@A)]:
  out=matrix(native(typ,a,b if typ!='InvertDilation' else None));err=float(np.max(abs(out-expected)));tests.append({'operator':typ,'case':case,'error':err})
  assert err<1e-5,(typ,case,err)
source=json.loads(Path('elsa-knee-dress-control-samples.json').read_text());clips=[]
for clip in source['clips']:
 rows=[]
 for frame in range(len(clip['samples'])):
  e=DressEval();e.overrides={int(k):v for k,v in clip['samples'][frame]['controls'].items()}
  for i in [620,627,15,14,651,656]:
   p,_=PROD[i];typ=get(p,'Type');args=[e.run(v) for a,v in zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')) if PROD.get(v,(None,None))[0] is not p]
   out=matrix(native(typ,dilation(args[0]),dilation(args[1]) if len(args)==2 else None));err=float(np.max(abs(out-e.run(i))));assert err<1e-5,(i,err)
   rows.append({'frame':frame,'node':i,'operation':typ,'error':err})
 clips.append({'name':clip['name'],'rows':rows})
report={'exe_sha256':sha,'scope':'100 random mixed-axis positive uniform-scale cases per operator, plus all 313 source frames. No full graph scheduling, optional layer or original game pose validation.','operators':{k:{'execute':hex(SPECS[k][0]),'max_error':max(x['error'] for x in tests if x['operator']==k)} for k in ['InvertDilation','ConcatenateChainDilation','ConcatenateChainInverseDilation']},'clips':clips}
Path('dress-reference-native-validation.json').write_text(json.dumps(report,indent=2));print(report['operators']);print('SOURCE MAX',max(r['error'] for c in clips for r in c['rows']))

