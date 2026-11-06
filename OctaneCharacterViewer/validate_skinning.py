import sys,json
from pathlib import Path
sys.path.insert(0,r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation\YodaAnimationProbe\analysis_dependencies')
import numpy as np
root=Path(__file__).parent
model=json.loads((root/'Data/elsa-pc-mesh.json').read_text());poses=json.loads((root.parent/'ElsaSceneResearch/pc-run-braid-animation.json').read_text())['clips'][0]['samples'];refs=json.loads((root/'skinning-reference-points.json').read_text())
vertices=np.c_[np.array(model['vertices'],dtype=np.float32).astype(float),np.ones(len(model['vertices']))];binds=np.array(model['bindposes'],dtype=np.float32).astype(float).reshape(-1,4,4)
indices=np.array([w['indices']for w in model['weights']]);weights=np.array([w['weights']for w in model['weights']],dtype=np.float32).astype(float)
worst=0
for record in refs:
 sample=record['sample']if 'sample'in record else poses[record['sampleIndex']];lookup={p['bone']:np.array(p['matrix'],dtype=np.float32).astype(float).reshape(4,4)for p in sample['transforms']};matrices=np.array([lookup[n]for n in model['bones']])@binds
 expected=np.zeros((len(vertices),3))
 for slot in range(4):expected+=np.einsum('vij,vj->vi',matrices[indices[:,slot]],vertices)[:,:3]*weights[:,slot,None]
 expected[:,2]*=-1
 error=float(np.max(abs(expected-np.array(record['points']))));worst=max(worst,error)
 if error>1e-9:raise ValueError(('C# vs numpy skinning mismatch',error))
report={'pass':True,'frames_checked':len(refs),'vertices_per_frame':len(vertices),'max_absolute_coordinate_error':worst,'scope':'Independent C# vs numpy CPU skinning, not source animation parity'}
(root/'skinning-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
