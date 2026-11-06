"""Build a standalone partial-palette mesh diagnostic from the source reader export."""
from pathlib import Path
import json,html as html_escape,numpy as np
P=Path(__file__).parent;D=P/'EyelidDiagnostic'
mesh=json.loads((D/'Extracted/mesh.json').read_text());binding=json.loads((P/'eyelid-skin-binding-check.json').read_text())
fixture=json.loads((P/'wiiu-head-eyelid-world-fixture.json').read_text())
tree=json.loads((P/'WiiUClips/fro_elsa.tree.json').read_text())
def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
def get(n,k):return next(c['value']for c in n['children']if c['name']==k)
head_influences=[n for n in walk(tree)if n['name']=='Influence'and get(n,'Name')=='Head']
assert len(head_influences)==1
head_bind=np.linalg.inv(np.array(get(head_influences[0],'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T)
base=np.array(mesh['positions']);points=np.c_[base,np.ones(len(base))];ids=np.array(mesh['indices']);weights=np.array(mesh['weights']);reflect=np.diag([-1,1,1,1]);frames=[];affected=np.zeros(len(base),bool)
assert np.max(abs(weights.sum(axis=1)-1))<1e-6
head_index=mesh['bones'].index('Head');head_descendants=[]
for index in range(len(mesh['bones'])):
 current=index;seen=set()
 while current>=0:
  assert current not in seen;seen.add(current)
  if current==head_index:head_descendants.append(index);break
  current=mesh['parents'][current]
lid_indices={mesh['bones'].index(r['bone'])for r in binding['results']}
# ParentRef omits some driven influences. Confirm eyeball attachment from producers.
all_bindings=json.loads((P/'wiiu-skin-associations.json').read_text())
def refs(n):return dict(zip(get(n,'DataNodeAttributes'),get(n,'DataNodeRefs')))
net=next(n for n in walk(tree)if n['name']=='SubNetwork')
producers={node:n for n in walk(net)if n['name']=='ProcessorNode'for attr,node in refs(n).items()if attr.startswith('Output')}
attachments=[]
for name in ('eyeLeft','eyeRight'):
 b=next(b for b in all_bindings if b['bone']==name);matrix=producers[b['matrix_node']]
 assert get(matrix,'Type')=='DilationToMatrix4x4VariantProcessor'
 world_id=refs(matrix)['Input'];world=producers[world_id]
 assert get(world,'Type')=='TransformDilationWithTransform'and refs(world)['Converter']==388
 index=mesh['bones'].index(name);head_descendants.append(index)
 attachments.append({'bone':name,'matrix_node':b['matrix_node'],'world_node':world_id,'head_converter':388,'local_input':refs(world)['Input']})
assert len(head_descendants)==len(set(head_descendants))
head_descendants=[i for i in head_descendants if i not in lid_indices]
head_weights=np.sum(np.where(np.isin(ids,head_descendants),weights,0),axis=1)
head_affected=head_weights>0
eye_indices=[mesh['bones'].index(a['bone'])for a in attachments]
eye_weights=np.sum(np.where(np.isin(ids,eye_indices),weights,0),axis=1)
pure_eyes=eye_weights>1-1e-6
assert pure_eyes.any()
face_fixture=json.loads((P/'wiiu-face-world-fixture.json').read_text())
neck_index=mesh['bones'].index('Neck');neck_weights=np.sum(np.where(ids==neck_index,weights,0),axis=1)
neck_affected=neck_weights>0
axial_fixture=json.loads((P/'wiiu-axial-world-fixture.json').read_text())
axial_names={r['bone']for r in axial_fixture['samples'][0]['outputs']};axial_carry={}
for index,name in enumerate(mesh['bones']):
 if index in head_descendants or index in lid_indices or index==neck_index:continue
 current=index;seen=set()
 while current>=0:
  assert current not in seen;seen.add(current)
  if mesh['bones'][current]in axial_names:
   axial_carry[index]=mesh['bones'][current];break
  current=mesh['parents'][current]
axial_weights={name:np.sum(np.where(np.isin(ids,[i for i,n in axial_carry.items()if n==name]),weights,0),axis=1)for name in axial_names}
axial_affected=sum(axial_weights.values())>0
for time in sorted(set(r['time']for r in binding['results'])):
 posed=base.copy();relative=base.copy();coherent=base.copy()
 head=np.array(next(f for f in fixture['samples']if f['time']==time)['head_world_matrix_column_convention'])
 remove_head=head_bind@np.linalg.inv(head)
 assert np.max(abs(remove_head@head-head_bind))<1e-10
 head_skin=reflect@head@np.linalg.inv(head_bind)@reflect
 coherent+=((head_skin@points.T).T[:,:3]-base)*head_weights[:,None]
 neck_sample=next(f for f in face_fixture['samples']if f['time']==time)
 neck_record=next(r for r in neck_sample['outputs']if r['bone']=='Neck')
 neck_skin=reflect@np.array(neck_record['skin_matrix_column_convention'])@reflect
 coherent+=((neck_skin@points.T).T[:,:3]-base)*neck_weights[:,None]
 for record in next(f for f in axial_fixture['samples']if f['time']==time)['outputs']:
  axial_skin=reflect@np.array(record['skin_matrix_column_convention'])@reflect
  coherent+=((axial_skin@points.T).T[:,:3]-base)*axial_weights[record['bone']][:,None]
 for record in [r for r in binding['results']if r['time']==time]:
  index=mesh['bones'].index(record['bone']);w=np.sum(np.where(ids==index,weights,0),axis=1)
  source_skin=np.array(record['skin_matrix_column_convention']);skin=reflect@source_skin@reflect
  relative_skin=reflect@remove_head@source_skin@reflect
  relative+=((relative_skin@points.T).T[:,:3]-base)*w[:,None]
  delta=((skin@points.T).T[:,:3]-base)*w[:,None]
  posed+=delta;coherent+=delta;affected|=w>0
 assert np.isfinite(posed).all()and np.isfinite(relative).all()and np.isfinite(coherent).all()
 frames.append({'time':time,'positions':posed.tolist(),'relative_positions':relative.tolist(),'coherent_positions':coherent.tolist(),'maximum_relative_displacement':float(np.max(np.linalg.norm(relative-base,axis=1))),'maximum_vertex_displacement':float(np.max(np.linalg.norm(posed-base,axis=1)))})
face_fixture=json.loads((P/'wiiu-face-world-fixture.json').read_text())
for frame in frames:
 full=np.array(frame['coherent_positions']);sample=next(f for f in fixture['samples']if f['time']==frame['time']);head=np.array(sample['head_world_matrix_column_convention']);carried=reflect@head@np.linalg.inv(head_bind)@reflect
 face=next(f for f in face_fixture['samples']if f['time']==frame['time'])
 for record in face['outputs']:
  if record['bone']=='Neck':continue # Already evaluated in coherent mode.
  index=mesh['bones'].index(record['bone']);assert index in head_descendants
  w=np.sum(np.where(ids==index,weights,0),axis=1)
  actual=reflect@np.array(record['skin_matrix_column_convention'])@reflect
  full+=((actual@points.T).T[:,:3]-(carried@points.T).T[:,:3])*w[:,None]
 assert np.isfinite(full).all()
 assert np.max(abs(full[~(affected|head_affected|neck_affected|axial_affected)]-base[~(affected|head_affected|neck_affected|axial_affected)]))==0
 expected_eye=(carried@points.T).T[:,:3]
 eye_error=float(np.max(abs(full[pure_eyes]-expected_eye[pure_eyes])))
 assert eye_error<1e-6,'Eyeballs must follow the carried Head transform'
 frame['pure_eye_vertices']=int(pure_eyes.sum());frame['eye_head_carry_error']=eye_error
 frame['face_positions']=full.tolist()
 frame['maximum_face_vs_carried_difference']=float(np.max(np.linalg.norm(full-np.array(frame['coherent_positions']),axis=1)))
coverage=json.loads((P/'wiiu-skin-output-coverage.json').read_text())
existing={r['bone']for r in binding['results']}|{r['bone']for f in face_fixture['samples']for r in f['outputs']}|axial_names|{'Head'}
extra=[o for o in coverage['outputs']if o['status']=='evaluated'and o['bone']not in existing]
for frame in frames:
 expanded=np.array(frame['face_positions']);head=np.array(next(f for f in fixture['samples']if f['time']==frame['time'])['head_world_matrix_column_convention']);head_skin=reflect@head@np.linalg.inv(head_bind)@reflect
 axial_sample=next(f for f in axial_fixture['samples']if f['time']==frame['time'])
 for output in extra:
  index=mesh['bones'].index(output['bone']);w=np.sum(np.where(ids==index,weights,0),axis=1)
  if index in head_descendants:old=head_skin
  else:
   assert index in axial_carry
   old=reflect@np.array(next(r for r in axial_sample['outputs']if r['bone']==axial_carry[index])['skin_matrix_column_convention'])@reflect
  actual=reflect@np.array(next(r for r in output['samples']if r['time']==frame['time'])['skin_matrix'])@reflect
  expanded+=((actual@points.T).T[:,:3]-(old@points.T).T[:,:3])*w[:,None]
 assert np.isfinite(expanded).all()
 frame['coverage_positions']=expanded.tolist()
 frame['maximum_extra_output_difference']=float(np.max(np.linalg.norm(expanded-np.array(frame['face_positions']),axis=1)))
assert affected.any()
for frame in frames:
 for key in ('positions','relative_positions'):assert np.max(abs(np.array(frame[key])[~affected]-base[~affected]))==0
for frame in frames:assert np.max(abs(np.array(frame['coherent_positions'])[~(affected|head_affected|neck_affected|axial_affected)]-base[~(affected|head_affected|neck_affected|axial_affected)]))==0
payload={'base':base.tolist(),'evaluated_count':coverage['evaluated'],'extra_outputs':[o['bone']for o in extra],'triangles':mesh['triangles'],'frames':frames,'affected':np.where(affected)[0].tolist()}
carried_indices=set(head_descendants)|set(axial_carry)|{neck_index}|lid_indices
coverage_rows=[]
for output in coverage['outputs']:
 index=mesh['bones'].index(output['bone']);status='evaluated'if output['status']=='evaluated'else 'carried'if index in carried_indices else 'bind pose'
 coverage_rows.append({'bone':output['bone'],'status':status,'blocking_reason':output['blocking_reason']})
coverage_html='<details><summary>Output coverage  -  evaluated-coverage mode</summary><table><tr><th>Influence</th><th>Status</th></tr>'+''.join('<tr><td>'+html_escape.escape(r['bone'])+'</td><td>'+r['status']+'</td></tr>'for r in coverage_rows)+'</table></details>'
html='''<!doctype html><meta charset="utf-8"><title>Wii U Elsa — partial eyelid diagnostic</title>
<style>body{margin:0;background:#151a20;color:#eee;font:15px system-ui}header{padding:14px}button,select{padding:6px;margin:4px}canvas{width:100%;height:78vh;touch-action:none}small{display:block;color:#bbc}</style>
<header><b>Wii U Elsa — partial eyelid diagnostic</b><small>Face mode evaluates four eyelids, three brows, jaw and four lip influences. Head/hair carrying remains partial; Body/spine/Hips are evaluated; authored limb descendants are carried at fixed bind-relative offsets. Head-group mode evaluates Neck and carries authored head descendants at fixed bind-relative offsets; only eyelids have evaluated local motion. Head-relative mode removes animated head motion algebraically. Absolute mode retains it and can produce seams against the fixed face. Neither is full actor playback. Three snapshots, no interpolated playback. Plain shading; no textures.</small>
<select id="sample"><option value="-1">Bind pose</option></select><select id="mode"><option value="coverage_positions">Evaluated coverage (24/64)</option><option value="face_positions">Evaluated face diagnostic</option><option value="coherent_positions">Head-group diagnostic</option><option value="relative_positions">Head-relative diagnostic</option><option value="positions">Absolute world fixture</option></select><button id="reset">Reset view</button><button id="face">Focus eyelids</button><label><input id="highlight" type="checkbox" checked>Highlight lid-weighted vertices</label><span id="status"></span><small>Drag to orbit · wheel to zoom. This is a mesh/binding diagnostic, not complete native animation playback.</small>COVERAGE_TABLE</header><canvas id="view"></canvas>
<script>const d=PAYLOAD;const c=document.querySelector('canvas'),ctx=c.getContext('2d'),sel=document.querySelector('#sample'),affected=new Set(d.affected);let yaw=0,pitch=0,zoom=1,drag=null;
d.frames.forEach((f,i)=>sel.add(new Option('Clip time '+f.time.toFixed(3)+' s',i)));let lo=[0,1,2].map(k=>Math.min(...d.base.map(v=>v[k]))),hi=[0,1,2].map(k=>Math.max(...d.base.map(v=>v[k])));let center=lo.map((v,k)=>(v+hi[k])/2);const size=Math.max(...hi.map((v,k)=>v-lo[k]));
function draw(){c.width=Math.round(c.clientWidth*devicePixelRatio);c.height=Math.round(c.clientHeight*devicePixelRatio);ctx.fillStyle='#151a20';ctx.fillRect(0,0,c.width,c.height);let f=Number(sel.value),p=f<0?d.base:d.frames[f][document.querySelector('#mode').value],scale=c.height*.8/size*zoom;let q=p.map(v=>{let x=v[0]-center[0],y=v[1]-center[1],z=v[2]-center[2],a=x*Math.cos(yaw)+z*Math.sin(yaw),b=-x*Math.sin(yaw)+z*Math.cos(yaw);return[c.width/2+a*scale,c.height/2-(y*Math.cos(pitch)-b*Math.sin(pitch))*scale,y*Math.sin(pitch)+b*Math.cos(pitch)]});let faces=[];d.triangles.forEach((ts,part)=>{for(let i=0;i<ts.length;i+=3){let a=ts.slice(i,i+3);faces.push({a,part,z:a.reduce((s,k)=>s+q[k][2],0)/3})}});faces.sort((a,b)=>a.z-b.z);for(let face of faces){let a=face.a.map(k=>q[k]);ctx.beginPath();ctx.moveTo(a[0][0],a[0][1]);ctx.lineTo(a[1][0],a[1][1]);ctx.lineTo(a[2][0],a[2][1]);ctx.closePath();let lit=document.querySelector('#highlight').checked&&face.a.some(k=>affected.has(k));ctx.fillStyle=lit?'#f8b84b':['#b8bbca','#739fae','#ccabba','#8f9bac'][face.part%4];ctx.fill();}document.querySelector('#status').textContent=d.base.length+' vertices; '+d.affected.length+' lid-weighted; '+d.evaluated_count+'/64 outputs evaluated; others carried or bind pose';}
c.onpointerdown=e=>{drag=[e.clientX,e.clientY];c.setPointerCapture(e.pointerId)};c.onpointerup=()=>drag=null;c.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.01;pitch=Math.max(-1.4,Math.min(1.4,pitch+(e.clientY-drag[1])*.01));drag=[e.clientX,e.clientY];draw()};c.onwheel=e=>{e.preventDefault();zoom=Math.max(.3,Math.min(12,zoom*Math.exp(-e.deltaY*.001)));draw()};sel.onchange=draw;document.querySelector('#mode').onchange=draw;document.querySelector('#face').onclick=()=>{center=[0,1,2].map(k=>d.affected.reduce((s,i)=>s+d.base[i][k],0)/d.affected.length);zoom=4;draw()};document.querySelector('#highlight').onchange=draw;document.querySelector('#reset').onclick=()=>{yaw=pitch=0;zoom=1;center=lo.map((v,k)=>(v+hi[k])/2);draw()};onresize=draw;draw();</script>'''.replace('PAYLOAD',json.dumps(payload,separators=(',',':'))).replace('COVERAGE_TABLE',coverage_html)
(D/'eyelid-preview.html').write_text(html,encoding='utf-8')
report={'vertices':len(base),'lid_weighted_vertices':int(affected.sum()),'unchanged_non_lid_vertices':int((~affected).sum()),'output_status':coverage_rows,'evaluated_outputs':coverage['evaluated'],'additional_evaluated_bones':[o['bone']for o in extra],'source_graph_attachments':attachments,'axial_carry':{mesh['bones'][i]:n for i,n in axial_carry.items()},'head_carried_bones':[mesh['bones'][i]for i in head_descendants],'head_group_weighted_vertices':int((affected|head_affected|neck_affected|axial_affected).sum()),'unchanged_outside_head_group':int((~(affected|head_affected|neck_affected|axial_affected)).sum()),'scope':'Twelve evaluated face influences; head/hair carrying is partial; Neck evaluated; remaining influences bind pose. Partial diagnostic, not actor playback.','samples':[{k:v for k,v in f.items()if k not in ('positions','relative_positions','coherent_positions','face_positions','coverage_positions')}for f in frames]}
(D/'mesh-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
