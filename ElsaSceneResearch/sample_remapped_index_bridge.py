"""Read coherent per-hand poses from validated current geometry-copy slots."""
import argparse,json,struct,sys,time
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'OctaneLiveInspector/ReadOnlyBridge'))
from client import submit
p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=20);a=p.parse_args();assert 0<a.seconds<=30
analysis=json.loads((R/'ElsaSceneResearch/ControllerState/skinremap-223856-analysis.json').read_text());links=json.loads((R/'ElsaSceneResearch/ControllerState/skinremap-223856-live-relationship-links.json').read_text())
model=json.loads((R/'OctaneCharacterViewer/Data/elsa-pc-mesh.json').read_text());preview=json.loads((R/'OctaneCharacterViewer/NativePreviews/native-run-full-palette.json').read_text());reflect=np.diag([-1.,1.,1.,1.])
def read(address,size):
 r=submit('READ',address,size,timeout=5);assert r['ok'],r
 return bytes.fromhex(r['hex']),r['id']
table_checks=[];live_groups=[]
for g in analysis['groups']:
 b,_=read(int(g['destination_slot_start'],16),248);matches=list(struct.unpack('<62I',b))==[int(x,16)for x in g['destination_nodes']]
 table_checks.append(dict(object=g['destination_object'],slots_match=matches))
 if matches:live_groups.append(g)
assert live_groups,'No captured geometry table still matches; reacquire current association'
palette=live_groups[0]['destination_nodes']
assert all(g['destination_nodes']==palette for g in live_groups),'Ambiguous current palettes'
def matrix(raw):
 m=np.eye(4);m[:3,:3]=np.array(raw[:9]).reshape(3,3).T;m[:3,3]=raw[9:];return reflect@m@reflect
references=[]
for s in preview['clips'][0]['samples']:
 m={t['bone']:np.array(t['matrix']).reshape(4,4)for t in s['transforms']};references.append((s['time'],{side:[np.linalg.inv(m['Hand_'+side])@m[k+'_'+side]for k in ('Index1','Index2')]for side in ('Left','Right')}))
configs=[]
for link in links:
 side=link['side'];addresses={k:int(palette[model['bones'].index(k+'_'+side)],16)for k in ('Hand','Index1','Index2')}
 addresses.update(Local1=int(link['local_candidate'],16),Local2=addresses['Index2']-0x5c)
 b,_=read(addresses['Local1']+24,4);assert struct.unpack('<I',b)[0]==int(link['producer'],16),'Relationship producer changed'
 configs.append((side,addresses))
history=[];start=time.monotonic()
while time.monotonic()-start<a.seconds:
 hands=[]
 for side,addresses in configs:
  lo=min(addresses.values());hi=max(addresses.values())+112;assert hi-lo<=4096;b,request=read(lo,hi-lo);nodes={}
  for key,address in addresses.items():
   off=address-lo;nodes[key]=dict(address=hex(address),stamp=struct.unpack_from('<H',b,off+32)[0],values=list(struct.unpack_from('<'+('8f'if key.startswith('Local')else'12f'),b,off+(52 if key.startswith('Local')else 64))))
  coherent=len({n['stamp']for n in nodes.values()})==1
  comparisons=[]
  if coherent:
   h=matrix(nodes['Hand']['values']);actual=[np.linalg.inv(h)@matrix(nodes[k]['values'])for k in ('Index1','Index2')]
   comparisons=[dict(time=t,error=max(float(np.max(abs(x-y)))for x,y in zip(actual,ref[side])))for t,ref in references]
  hands.append(dict(side=side,request_id=request,coherent=coherent,nodes=nodes,best_run_comparison=min(comparisons,key=lambda x:x['error'])if comparisons else None))
 history.append(dict(elapsed=time.monotonic()-start,hands=hands));time.sleep(.15)
report=dict(table_checks=table_checks,observations=history,scope='At least one current post-remap62-slot geometry table validated before sampling; changed/retired copies excluded. Separately coherent per-hand snapshots, not simultaneous whole-body sampling. Nearest constant run-finger pose is diagnostic, not clip identity or GPU draw proof.')
out=R/'ElsaSceneResearch/ControllerState/remapped-index-live-observations.json';out.write_text(json.dumps(report,indent=2));print(json.dumps(dict(saved=str(out),samples=len(history),coherent_hands=sum(h['coherent']for x in history for h in x['hands']))))
try:
 import winsound
 winsound.MessageBeep()
except Exception:pass
