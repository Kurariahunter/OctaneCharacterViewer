"""Compare endian-adapted Wii U scalar curves with matching PC source curves."""
from pathlib import Path
import sys,json,struct,collections,numpy as np
from wiiu_pc_graph_adapter import P
from wiiu_clip_sampler import WiiUClip
from read_pc_idle_files import tuple_decode
from native_pc_clip_math import curve
rows=[]
for name in ['grl_bm_runf','grl_bm_run_upbody_add','grl_bm_walkf','grl_bm_walk_upbody_add']:
 w=WiiUClip(P/'ClipExpansion/Locomotion'/f'{name}.oct.clipdata');pcfile=next((P.parents[1]/'ElsaSceneResearch/InstalledGameAssetCheck').rglob(name+'.oct'));raw=next(r['value']for r in tuple_decode(pcfile.read_bytes())['records']if r['name']=='ClipDataBlock');b=bytes(raw)if isinstance(raw,list)else bytes.fromhex(raw['hex']);n=struct.unpack_from('<H',b,10)[0];pool=struct.unpack_from('<I',b,12)[0];starts=struct.unpack_from('<'+'I'*n,b,20);assert n==len(w.curves)
 maximum=0;equal=0;flags=collections.Counter()
 for i,(wb,dims)in enumerate(w.curves):
  pb=b[starts[i]:starts[i+1]if i+1<n else pool];flags[struct.unpack_from('<I',wb)[0]&1023]+=1;equal+=wb==pb
  for t in np.linspace(w.lo,w.hi,33):maximum=max(maximum,max(abs(x-y)for x,y in zip(curve(wb,float(t),dims),curve(pb,float(t),dims))))
 rows.append({'file':name,'curves':n,'byte_identical_transcoded_curves':equal,'flags':dict(flags),'maximum_native_sample_difference_vs_pc':maximum})
(P/'ClipExpansion/locomotion-native-curve-crosscheck.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
