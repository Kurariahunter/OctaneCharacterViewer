"""Wait briefly for a coherent running hand pose, without debugger hooks or game writes."""
import json,sys,time,struct
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'OctaneLiveInspector/ReadOnlyBridge'))
from client import submit
ROOT=Path(__file__).resolve().parent
links=json.loads((ROOT/'ControllerState/active-index-scene-rig-links.json').read_text())
old=json.loads((ROOT/'ControllerState/active-index-skin-snapshot.json').read_text())
preview=json.loads((ROOT.parent/'OctaneCharacterViewer/NativePreviews/current-native-run.json').read_text())
expected={p['processor']:p['outputs'][:2]for p in preview['finger_diagnostics']['samples'][0]['processors']if p['processor']in(165,171)}
reflect=np.diag([-1,1,1,1])
def affine(p):
 m=np.eye(4);m[:3,:3]=np.array(p[:9]).reshape(3,3).T;m[:3,3]=p[9:];return reflect@m@reflect
samples=preview['clips'][0]['samples'];history=[];deadline=time.monotonic()+90
while time.monotonic()<deadline:
 rows=[]
 for r in links:
  hand=int(next(x for x in old if x['side']==r['side'])['nodes'][0]['address'],16)
  addresses=dict(Hand=hand,Index1=int(r['scene_first_matrix'],16),Index2=int(r['scene_second_matrix'],16),Local1=int(r['first_local_node'],16),Local2=int(r['second_local_node'],16))
  lo=min(addresses.values());hi=max(a+(84 if k.startswith('Local')else 112)for k,a in addresses.items())
  answer=submit('READ',lo,hi-lo);assert answer['ok'];b=bytes.fromhex(answer['hex']);nodes={}
  for k,a in addresses.items():
   offset=a-lo;width=8 if k.startswith('Local')else 12
   nodes[k]=dict(stamp=struct.unpack_from('<H',b,offset+32)[0],values=list(struct.unpack_from('<'+'f'*width,b,offset+(52 if width==8 else 64))))
  err=0.
  for k,ex in zip(('Local1','Local2'),expected[r['relationship_file_pid']]):
   q=np.array(nodes[k]['values'][:4]);eq=np.array(ex['quaternion']);err=max(err,min(float(np.max(abs(q-eq))),float(np.max(abs(q+eq)))))
  coherent=len({n['stamp']for n in nodes.values()})==1
  row=dict(side=r['side'],coherent=coherent,run_local_quaternion_error=err,nodes=nodes,request_id=answer['id'])
  if coherent and err<1e-4:
   actual=[np.linalg.inv(affine(nodes['Hand']['values']))@affine(nodes[k]['values'])for k in ('Index1','Index2')]
   comparisons=[]
   for s in samples:
    p={t['bone']:np.array(t['matrix']).reshape(4,4)for t in s['transforms']};par=p['Hand_'+r['side']]
    errors=[float(np.max(abs(a-np.linalg.inv(par)@p[k+'_'+r['side']])))for a,k in zip(actual,('Index1','Index2'))]
    comparisons.append(dict(time=s['time'],first_error=errors[0],second_error=errors[1],max_error=max(errors)))
   row['viewer_comparisons']=comparisons;row['best_error']=min(c['max_error']for c in comparisons);row['worst_error']=max(c['max_error']for c in comparisons)
  rows.append(row)
 history.append(rows)
 if all('viewer_comparisons'in r for r in rows):break
 if len(history)%8==0:print('Waiting for running pose; latest local errors '+str([r['run_local_quaternion_error']for r in rows]),flush=True)
 time.sleep(1)
matched=all('viewer_comparisons'in r for r in history[-1]);report=dict(matched_running_pose=matched,attempts=len(history),last=history[-1],history=history,
 scope='Coherent per-hand active GeometryNode skin matrices with local run-quaternion signature. Compares hand-relative matrices to saved run samples; not global frame synchronization or GPU vertex output.')
(ROOT/'ControllerState/active-run-index-palette-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(matched=matched,attempts=len(history),rows=[{k:v for k,v in r.items()if k not in ('nodes','viewer_comparisons')}for r in history[-1]])),flush=True)
