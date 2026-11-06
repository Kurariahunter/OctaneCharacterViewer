"""Compare Wii U flags0 cubic boundary semantics with original PC native routine.
Only layout-preserving endian transcoding; not native Wii U code execution.
"""
from pathlib import Path
import sys,struct,json,math
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from native_pc_clip_math import curve,sha
P=Path(__file__).parent
b=(P/'WiiUClips/elsa_bm_idle_specific01.oct.clipdata').read_bytes();count=struct.unpack_from('>H',b,10)[0];pool=struct.unpack_from('>I',b,12)[0];offsets=struct.unpack_from('>'+str(count)+'I',b,20);rows=[]
def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]
for i,start in enumerate(offsets):
 end=offsets[i+1]if i+1<count else pool;src=b[start:end];word=struct.unpack_from('>I',src)[0];dims=(word>>10)&1023;segs=word>>20;assert word&1023==0
 lo,hi=struct.unpack_from('>ff',src,4);meta=[struct.unpack_from('>4f',src,12+16*d)for d in range(dims)];dst=bytearray(src);struct.pack_into('<I',dst,0,word)
 for at in range(4,12+16*dims,4):struct.pack_into('<I',dst,at,struct.unpack_from('>I',src,at)[0])
 data=12+16*dims
 for at in range(data,data+2*segs+8*segs*dims,2):struct.pack_into('<H',dst,at,struct.unpack_from('>H',src,at)[0])
 first=data+2*segs;before=[f(m[2]+f(struct.unpack_from('>h',src,first+8*d)[0]*m[3]))for d,m in enumerate(meta)];after=[m[1]for m in meta]
 native_before=curve(bytes(dst),lo-.125,dims);native_after=curve(bytes(dst),hi+.125,dims);at_end=curve(bytes(dst),hi,dims)
 be=max(abs(x-y)for x,y in zip(before,native_before));ae=max(abs(x-y)for x,y in zip(after,native_after))
 assert be<=max(1e-6,max(abs(x)for x in before)*1e-6),(i,be)
 assert ae==0,(i,ae)
 rows.append({'curve':i,'dimensions':dims,'range':[lo,hi],'before_expected':before,'after_metadata_expected':after,'native_before':native_before,'native_after':native_after,'native_at_end':at_end,'before_error':be,'after_error':ae})
report={'scope':'Original PC native scalar routine on endian-transcoded Wii U cubic data; static RPX branches independently confirm boundary choice. This does not execute Wii U code or prove all in-range math identical.','pc_exe_sha256':sha,'pass':True,'curves':rows,'checks':len(rows)*2,'max_before_error':max(x['before_error']for x in rows),'max_after_error':max(x['after_error']for x in rows)}
(P/'boundary-native-crosscheck.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='curves'},indent=2))
