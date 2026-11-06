import json,struct,hashlib
from pathlib import Path
from native_pc_blend_replay import blend,sha
R=Path(__file__).parent
p=R.parent/'OctaneLiveInspector/Captures/ce_blendexec_20261017_204631_310307171.jsonl';data=p.read_bytes();rs=[json.loads(s)for s in data.decode().splitlines()];rows=[];skipped=[]
def f(h):
 b=bytes.fromhex(h);return list(struct.unpack('<'+'f'*(len(b)//4),b))
def value(c,key,default):return None if c.get(default)else f(c[key])[0]
for r in rs:
 if r.get('event')!='blend':continue
 if r['contribution_count']==0:skipped.append({'sequence':r['sequence'],'reason':'empty table; no original default/output prior state captured'});continue
 cs=[]
 for k,c in sorted(r['contributions'].items()):cs.append(dict(values=f(c['input_payload_hex64']),priority=f(c['priority_hex4'])[0],flag=c['flag39'],weight=value(c,'weight_hex4','weight_default_one'),factor2c=value(c,'factor_2c_hex4','factor_2c_default_one'),factor30=value(c,'factor_30_hex4','factor_30_default_one'),packed=int(c['packed_word'],16)))
 actual=blend(cs);wanted=f(r['output_payload_hex32']);error=max(abs(a-b)for a,b in zip(actual,wanted));rows.append({'sequence':r['sequence'],'count':len(cs),'error':error,'predicted':actual,'observed':wanted})
report={'capture':str(p),'capture_sha256':hashlib.sha256(data).hexdigest(),'exe_sha256':sha,'cases':len(rows),'max_error':max(x['error']for x in rows),'skipped':skipped,'rows':rows,'scope':'Original native blend execution with synthetic cached inputs, full replacement flag, no default network; identity output initializer. Numeric payloads/weights/priorities from capture, slots compacted. Does not reconstruct source loader or temporal fade.'}
(R/'pc-native-blend-capture-replay.json').write_text(json.dumps(report,indent=2));print('CASES',len(rows),'MAX',report['max_error']);print('FAILURES',[(x['sequence'],x['error'])for x in rows if x['error']>1e-6]);assert report['max_error']<1e-6
