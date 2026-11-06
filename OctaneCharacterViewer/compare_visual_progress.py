"""Compare saved native previews using the viewer's float32 CPU skinning inputs."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
model=json.loads((ROOT/'Data/elsa-pc-mesh.json').read_text())
v=np.c_[np.array(model['vertices'],dtype=np.float32).astype(float),np.ones(len(model['vertices']))]
bind=np.array(model['bindposes'],dtype=np.float32).astype(float).reshape(-1,4,4)
idx=np.array([w['indices']for w in model['weights']]);weights=np.array([w['weights']for w in model['weights']],dtype=np.float32).astype(float)
bones=model['bones'];handids=[i for i,n in enumerate(bones)if any(x in n.lower()for x in ['index','middle','thumb'])and ('left'in n.lower()or n.lower().startswith('l'))]
if not handids:handids=[i for i,n in enumerate(bones)if any(x in n.lower()for x in ['index','middle','thumb'])][:8]
mask=np.sum(weights*np.isin(idx,handids),axis=1)>.2
tris=np.concatenate([np.array(p['triangles']).reshape(-1,3)for p in model['parts']]);tris=tris[np.any(mask[tris],axis=1)]
def skin(s):
 lookup={p['bone']:np.array(p['matrix'],dtype=np.float32).astype(float).reshape(4,4)for p in s['transforms']}
 mats=np.array([lookup[n]for n in bones])@bind;out=np.zeros((len(v),3))
 for k in range(4):out+=np.einsum('vij,vj->vi',mats[idx[:,k]],v)[:,:3]*weights[:,k,None]
 out[:,2]*=-1
 return out
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
custom=len(sys.argv)>2
canvas=Image.new('RGB',(1200,510 if custom else 1020),'#10151b');draw=ImageDraw.Draw(canvas)
reports=[]
comparisons=[(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else 'Native channel-buffer composition: before versus current')] if custom else [
 ('grl_bm_runf-20261020-013558-741.json','native-default-visual-check.json','Latest precision change (same native-default timing)'),
 ('grl_bm_runf-20261019-015253-877.json','native-run-raw-finger-check.json','Earlier viewer versus current (same fixture timing)')]
for row,(old,new,title)in enumerate(comparisons):
 a=json.loads((ROOT/'NativePreviews'/old).read_text());b=json.loads((ROOT/'NativePreviews'/new).read_text())
 sa=a['clips'][0]['samples'];sb=b['clips'][0]['samples'];assert len(sa)==len(sb)
 assert all(abs(x['time']-y['time'])<1e-7 for x,y in zip(sa,sb))
 pairs=[(skin(x),skin(y))for x,y in zip(sa,sb)]
 diffs=[np.linalg.norm(x-y,axis=1)for x,y in pairs];frame=int(np.argmax([d[mask].max()for d in diffs]));x,y=pairs[frame]
 cloud=np.r_[x[mask],y[mask]];center=cloud.mean(axis=0);_,_,axes=np.linalg.svd(cloud-center,full_matrices=False)
 basis=axes.T;proj=(cloud-center)@basis;span=max(np.ptp(proj[:,:2],axis=0))*1.35;scale=410/span
 draw.text((24,row*510+12),title,font=font,fill='white')
 for col,(pts,label)in enumerate([(x,'Before'),(y,'Current')]):
  q=(pts-center)@basis;screen=q[:,:2]*scale;screen[:,1]*=-1;screen+=np.array([300+600*col,row*510+270])
  # Shared geometry projection and depth order for an honest pose comparison.
  for t in sorted(tris,key=lambda t:q[t,2].mean()):
   normal=np.cross(q[t[1]]-q[t[0]],q[t[2]]-q[t[0]]);norm=np.linalg.norm(normal)
   shade=.45+.5*abs(normal[2]/norm)if norm else .45
   color=tuple(int(c*shade)for c in (226,190,213))
   draw.polygon([tuple(z)for z in screen[t]],fill=color)
  draw.text((30+600*col,row*510+48),label,font=font,fill='white')
 d=diffs[frame];maxall=max(float(z.max())for z in diffs);maxhand=max(float(z[mask].max())for z in diffs)
 draw.text((24,row*510+465),f'Largest hand difference: {maxhand:.8g} model units | same time: {sa[frame]["time"]:.3f}s',font=small,fill='#b9c9d8')
 reports.append(dict(before=old,current=new,samples=len(sa),frame=frame,time=sa[frame]['time'],max_vertex_displacement=maxall,max_hand_displacement=maxhand,hand_vertices=int(mask.sum()),projected_max_hand_pixels=maxhand*scale))
prefix=sys.argv[4] if len(sys.argv)>4 else ('native-composition-comparison' if custom else 'visual-progress-comparison')
canvas.save(ROOT/(prefix+'.png'))
(ROOT/(prefix+'.json')).write_text(json.dumps(dict(comparisons=reports,scope='Orthographic skinned-geometry comparison using saved palettes and viewer float32 inputs; shared camera per pair, untextured. Across historical versions, not isolated causation except latest timing-matched checkpoint.'),indent=2),encoding='utf-8')
print(json.dumps(reports))
