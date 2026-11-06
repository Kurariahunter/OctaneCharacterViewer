"""Full vs staged original-PC eyelid relationship; bounded source fixture."""
import hashlib,json,math,random
from pathlib import Path
from evaluate_pc_arms import N,DN,allnodes,get
from native_pc_relationship import run
from native_pc_lean_ik import sha
R=Path(__file__).parent
p=next(p for p in allnodes(N,'ProcessorNode') if int(p['value'])==177)
pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')));refs=dict(pairs)
blob=bytes.fromhex(get(DN[refs['RelationshipData']],'RelationshipDataBlock')['hex'])
assert hashlib.sha256(blob).hexdigest()=='7ad4d7ac5ad56a235376973be6fd8849ac5e68d27d1ece72d96d04a1f25216b3'
assert [v for a,v in pairs if a.startswith('Output[')]==[274,278,282,286]
assert all(get(DN[v],'Type')=='Dilation' for a,v in pairs if a.startswith('Output['))
fixtures=[[0.]*4]
for axis in range(4):
 for value in (-100,-50,0,50,100):
  row=[0.]*4;row[axis]=value;fixtures.append(row)
rng=random.Random(20261022)
fixtures += [[rng.uniform(-100,100) for _ in range(4)] for _ in range(40)]
maximum=0.;rows=[]
for values in fixtures:
 full=run(blob,values,4);split=run(blob,values,4,staged=True)
 error=max(abs(a-b) for x,y in zip(full,split) for a,b in zip(x,y));maximum=max(maximum,error)
 assert error<1e-7
 for row in full:
  assert all(math.isfinite(v) for v in row)
  assert abs(sum(v*v for v in row[:4])-1)<1e-4
  assert max(abs(v) for v in row[4:7])<1e-7 and row[7]==1.
 rows.append(dict(inputs=values,outputs=full))
report=dict(passed=True,exe_sha256=sha,blob_sha256=hashlib.sha256(blob).hexdigest(),processor=177,blob_node=34,input_nodes=[341,342,343,340],output_nodes=[274,278,282,286],cases=len(fixtures),max_full_vs_staged_error=maximum,rows=rows,scope='Original PC full RelationshipProcessor versus original staged input/output routines, explicit zero caches and identity Dilation outputs, scalar inputs within [-100,100]. Confirms bounded source blob execution, not live-game eyelid parity, persistent cache behavior, or arbitrary relationship support.')
(R/'ControllerState/eyelid-relationship-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
