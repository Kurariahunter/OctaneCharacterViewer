"""Bounded static PC lean ClipData reader; no guessed blend application."""
import json,struct,hashlib,math
from pathlib import Path
from read_pc_idle_files import R,Rig,Clip,tuple_decode
from pc_clip_decoder import constants

def read_static(b):
 if len(b)<28:raise ValueError('short static header')
 if struct.unpack_from('<IIHH',b,0)!=(0,0,1,0):raise ValueError('not tested static PC header')
 pool,start=struct.unpack_from('<II',b,12)
 if start!=20 or not start+8<=pool<=len(b) or pool%4:raise ValueError('static offsets')
 if struct.unpack_from('<4H',b,start)!=(0,0,8,0):raise ValueError('nonempty timed commands in static clip')
 return constants(b,{'static_commands_start':start+8,'static_commands_end':pool,'float_pool_start':pool})

def main():
 rig=Rig(R/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct');p=next((R/'InstalledGameAssetCheck/RunMotions').rglob('human_bm_runf_lean_add.oct'))
 source=p.read_bytes();v=next(x['value']for x in tuple_decode(source)['records']if x['name']=='ClipDataBlock');b=bytes.fromhex(v['hex'])if isinstance(v,dict)else bytes(v);data=read_static(b)
 assert [x['port']for x in data['tracks']]==[92,545,754,755]
 lower=Clip(next((R/'InstalledGameAssetCheck/RunMotions').rglob('grl_bm_runf.oct')),rig);upper=Clip(next((R/'InstalledGameAssetCheck/RunMotions').rglob('grl_bm_run_upbody_add.oct')),rig)
 sets=[{v['source_node']for v in c.sample(0).values()if v['source_node']is not None}for c in (lower,upper)]
 for x in data['tracks']:
  n=rig.lookup.get(x['port']);assert n is not None;x.update(source_node=n,path=rig.paths[n],overlap_lower=n in sets[0],overlap_upper=n in sets[1])
  for d in x['descriptors']:
   if d['opcode']==4:
    q=d['values'];assert abs(sum(v*v for v in q)-1)<1e-6;d['angle_degrees']=math.degrees(2*math.acos(min(1,abs(q[3]))))
 invalid=[b[:12],b[:-1]]
 bad=bytearray(b);struct.pack_into('<I',bad,12,len(b)+4);invalid.append(bytes(bad))
 bad=bytearray(b);struct.pack_into('<H',bad,10,1);invalid.append(bytes(bad))
 rejected=0
 for bad in invalid:
  try:read_static(bad)
  except (ValueError,struct.error):rejected+=1
  else:raise AssertionError('bad static input accepted')
 report={'source':str(p),'asset_sha256':hashlib.sha256(source).hexdigest(),'clipdata_sha256':hashlib.sha256(b).hexdigest(),'model_sha256':rig.sha,'timed_curves':0,'tracks':data['tracks'],'invalid_inputs_rejected':rejected,'scope':'Static channel decode and structural mapping only. No native blend replay; no claim BlendMethod=1 to runtime flag39 linkage or multiplication order is proven. Existing run preview unchanged.'}
 (R/'pc-run-lean-static-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
