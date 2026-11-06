"""Validate native packed matrix semantics against native point transforms."""
import random,math,json
from pathlib import Path
from native_pc_transform_scale import compose,point
from native_pc_skin_matrix import matrix
from native_pc_lean_ik import sha

rng=random.Random(184512);rows=[]
for i in range(48):
    q=[rng.uniform(-1,1)for _ in range(4)];norm=math.sqrt(sum(x*x for x in q));q=[x/norm for x in q]
    t=[rng.uniform(-8,8)for _ in range(3)]
    scale=[rng.uniform(.7,1.3)for _ in range(4)]
    raw=compose(q,t,scale,[1]*4);m=matrix(raw)
    errors=[];wrong=[]
    for v in ([0,0,0],[1,0,0],[0,1,0],[0,0,1],[.17,-.29,.43]):
        expected=point(raw,v)
        predicted=[sum(m[j*3+k]*v[j]for j in range(3))+m[9+k]for k in range(3)]
        transposed=[sum(m[k*3+j]*v[j]for j in range(3))+m[9+k]for k in range(3)]
        errors.append(max(abs(a-b)for a,b in zip(predicted,expected)))
        wrong.append(max(abs(a-b)for a,b in zip(transposed,expected)))
    rows.append(dict(case=i,max_point_error=max(errors),transposed_error=max(wrong)))
summary=dict(cases=len(rows),point_comparisons=5*len(rows),max_point_error=max(r['max_point_error']for r in rows),
             wrong_transpose_max_error=max(r['transposed_error']for r in rows))
report=dict(exe_sha256=sha,summary=summary,rows=rows,
    scope='Native55da50 typed converter, output12floats at node+40; packed9linear terms followed by translation3. Point action p[k]=sum(m[j*3+k]*v[j])+m[9+k]. 48mixed quaternion/translation/nonuniform positive scale cases against native4c4350. Static/offline validation, no live matrix capture yet.')
(Path(__file__).parent/'pc-native-matrix-converter-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(summary,indent=2))
assert summary['max_point_error']<4e-6 and summary['wrong_transpose_max_error']>.1
