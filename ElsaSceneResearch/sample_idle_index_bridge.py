"""Bounded read-only idle hand observation; nearest-pose comparison is not clip identification."""
import sys,json,time,struct,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'OctaneLiveInspector/ReadOnlyBridge'))
sys.path.insert(0,r'C:/Users/Kurar/.codex/visualizations/2026/09/19/01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1/DI3ConverterValidation/YodaAnimationProbe/analysis_dependencies')
import numpy as np
from client import submit
def read(a,n):
 r=submit('READ',a,n);assert r['ok'];return bytes.fromhex(r['hex']),r['id']
links=json.loads((ROOT/'ElsaSceneResearch/ControllerState/active-index-scene-rig-links.json').read_text())
old=json.loads((ROOT/'ElsaSceneResearch/ControllerState/active-index-skin-snapshot.json').read_text())
for r in links:
 p=int(r['relationship'],16);rel=struct.unpack('<I',read(p+0x58,4)[0])[0];blob=struct.unpack('<I',read(rel+0x3c,4)[0])[0]
 assert hashlib.sha256(read(blob,836)[0]).hexdigest()==r['sha256'],'Relationship changed'
 # Check the active geometry table still binds the recorded nodes.
table=read(0x1ebbda00,16)[0];assert struct.unpack_from('<H',table)[0]==62
entries=struct.unpack('<62I',read(0x1ebbda00+struct.unpack_from('<H',table,2)[0],248)[0])
for r in links:
 for key in ('scene_first_matrix','scene_second_matrix'):assert int(r[key],16) in entries
reflect=np.diag([-1,1,1,1])
def affine(p):
 m=np.eye(4);m[:3,:3]=np.array(p[:9]).reshape(3,3).T;m[:3,3]=p[9:];return reflect@m@reflect
references=[]
for i in range(1,4):
 a=json.loads((ROOT/f'OctaneCharacterViewer/NativePreviews/native-elsa-specific{i:02}.json').read_text())
 for s in a['clips'][0]['samples']:
  d={t['bone']:np.array(t['matrix']).reshape(4,4) for t in s['transforms']}
  references.append((i,s['time'],{r['side']:[np.linalg.inv(d['Hand_'+r['side']])@d[k+'_'+r['side']] for k in ('Index1','Index2')] for r in links}))
history=[];start=time.monotonic()
while time.monotonic()-start<65:
 rows=[]
 for r in links:
  hand=int(next(x for x in old if x['side']==r['side'])['nodes'][0]['address'],16)
  addresses=dict(Hand=hand,Index1=int(r['scene_first_matrix'],16),Index2=int(r['scene_second_matrix'],16))
  lo=min(addresses.values());hi=max(addresses.values())+112;b,request=read(lo,hi-lo)
  nodes={k:dict(stamp=struct.unpack_from('<H',b,a-lo+32)[0],values=list(struct.unpack_from('<12f',b,a-lo+64))) for k,a in addresses.items()}
  coherent=len({n['stamp'] for n in nodes.values()})==1
  matches=[]
  if coherent:
   actual=[np.linalg.inv(affine(nodes['Hand']['values']))@affine(nodes[k]['values']) for k in ('Index1','Index2')]
   for i,t,reference in references:
    error=max(float(np.max(abs(x-y))) for x,y in zip(actual,reference[r['side']]))
    matches.append(dict(clip=i,time=t,error=error))
  rows.append(dict(side=r['side'],nodes=nodes,coherent=coherent,request_id=request,best=min(matches,key=lambda x:x['error']) if matches else None))
 history.append(dict(elapsed=time.monotonic()-start,hands=rows))
 if len(history)%20==0:print('Samples',len(history),flush=True)
 time.sleep(.15)
report=dict(observations=history,scope='Separate coherent per-hand snapshots; nearest index-relative pose only, not identified idle clip, synchronized clock or full mesh parity.')
p=ROOT/'ElsaSceneResearch/ControllerState/live-idle-index-observations.json';p.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Saved',len(history),'observations',flush=True)
try:
 import winsound
 winsound.MessageBeep()
except Exception:pass
