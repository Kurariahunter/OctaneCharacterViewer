"""Native multi-row scalar tests using actual runtime row layout."""
import json,struct
from pathlib import Path
from native_pc_raw_buffer_blend import replay

def row(value,mask=1):return struct.pack('<12fI',value,0,0,0,1,1,1,1,0,0,0,1,mask)
rows=[]
for mode in (0,1):
    for weight in (0,.5,.85,1):
        dst=row(2)+row(-3);src=row(4)+row(6)
        result=replay(dst,src,weight,mode)
        values=[struct.unpack_from('<f',result,i*52)[0]for i in range(2)]
        w=struct.unpack('<f',struct.pack('<f',weight))[0]
        expected=[a+b*w if mode==0 else a+(b-a)*w for a,b in ((2,4),(-3,6))]
        error=max(abs(a-b)for a,b in zip(values,expected));assert error<2e-6
        rows.append(dict(mode=mode,weight=weight,error=error))
rejected=0
for args in ((b'',row(1),1,0),(row(1),row(1),1,2),(row(1),row(1,0x8000),1,0)):
    try:replay(*args)
    except ValueError:rejected+=1
    else:raise AssertionError('Invalid input accepted')
r=dict(cases=rows,invalid_inputs_rejected=rejected,scope='Synthetic native multi-row scalar arithmetic only; no captured live blend yet.')
(Path(__file__).parent/'ControllerState/raw-buffer-blend-fixture-validation.json').write_text(json.dumps(r,indent=2)+'\n')
print(dict(cases=len(rows),invalid_inputs_rejected=rejected))
