"""Pinned Elsa head-control bridge. Source-control bone, not arbitrary skin-bone inversion."""
import bpy,json,base64,pathlib,hashlib,math
from mathutils import Matrix,Vector
from .codec import read,encode
from . import curves,signature
SHA='9fe1c9e60b679f212ee2bdb5bcf61eccba81e4e8c750fd4d7f33039e45f19d53'
AXES=['curve_049_dim_000','curve_050_dim_000','curve_051_dim_000']

def import_head(path):
 raw=pathlib.Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('Head bridge requires original PC elsa_bm_idle_specific03.oct')
 channels={c['id']:c for c in read(raw)[4]};collection=bpy.data.collections.new('Elsa native head control');bpy.context.scene.collection.children.link(collection)
 arm=bpy.data.armatures.new('Elsa source control');obj=bpy.data.objects.new('Elsa OCT editable head control',arm);collection.objects.link(obj)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.mode_set(mode='EDIT')
 bone=arm.edit_bones.new('Cntrl_Head');bone.head=(0,0,1.25);bone.tail=(0,0,1.4);bone.use_deform=False
 mesh=json.loads((pathlib.Path(r'F:\DisneyInfinityPortalTest')/'OctaneCharacterViewer/Data/elsa-pc-mesh.json').read_text());bind=Matrix([mesh['bindposes'][mesh['bones'].index('Head')][i:i+4] for i in range(0,16,4)]).inverted();C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)));rest=C@Matrix.Diagonal((1,-1,-1,1));rest.translation=(C@bind).translation;bone.matrix=rest;bone.length=.15
 bpy.ops.object.mode_set(mode='POSE');pb=obj.pose.bones['Cntrl_Head'];pb.rotation_mode='ZXY';bpy.ops.object.mode_set(mode='OBJECT')
 for axis,cid in enumerate(AXES):
  c=channels[cid]
  for i,(time,value) in enumerate(zip(c['times'],[v[0] for v in c['controls']]+[c['controls'][-1][-1]])):
   pb.rotation_euler[axis]=value;pb.keyframe_insert(data_path='rotation_euler',index=axis,frame=1+time*30,group='Cntrl_Head')
  fc=next(f for f in curves(obj) if f.array_index==axis)
  for i,k in enumerate(fc.keyframe_points):
   k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='FREE'
   if i>0:
    width=(c['times'][i]-c['times'][i-1])*10;k.handle_left=(k.co.x-width,c['controls'][i-1][2])
   if i<len(c['controls']):
    width=(c['times'][i+1]-c['times'][i])*10;k.handle_right=(k.co.x+width,c['controls'][i][1])
 obj['di_head_template']=base64.b64encode(raw).decode();obj['head_signatures']=json.dumps(signature(obj));obj['head_source']='Anchor|Cntrl_Head|Transform; node267; port545; registers68,69,70; Euler convention2'
 obj['scope']='Only this source-control bone is exportable. Mesh follows after native preview refresh.'
 bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=152;bpy.context.scene.render.fps=30;bpy.context.scene.frame_set(1)
 return obj

def export_head(obj,path):
 if 'di_head_template' not in obj:raise ValueError('Select Elsa OCT editable head control')
 pb=obj.pose.bones['Cntrl_Head']
 if pb.rotation_mode!='ZXY' or len(pb.constraints) or any(abs(v)>1e-7 for v in pb.location) or any(abs(v-1)>1e-7 for v in pb.scale):raise ValueError('Only keyed ZXY rotation edits are supported')
 if obj.constraints or obj.animation_data.nla_tracks:raise ValueError('Constraints/NLA are not supported for this control')
 raw=base64.b64decode(obj['di_head_template']);channels={c['id']:c for c in read(raw)[4]};fs=curves(obj)
 if len(fs)!=3 or any(f.data_path!='pose.bones["Cntrl_Head"].rotation_euler' or f.modifiers for f in fs):raise ValueError('Only three head Euler curves are supported')
 original=json.loads(obj['head_signatures']);current=signature(obj);edits={}
 for axis,cid in enumerate(AXES):
  fi=next(i for i,f in enumerate(fs) if f.array_index==axis)
  if current[fi]==original[fi]:continue
  c=channels[cid];fc=fs[fi]
  if not fc.keyframe_points:raise ValueError('Head axis has no animation keys')
  lo,hi=read(raw)[3]['time_range'];count=round((hi-lo)*60)
  times=[lo+(hi-lo)*i/count for i in range(count+1)]
  values=[float(fc.evaluate(1+t*30)) for t in times]
  edits[c['curve']]={'times':times,'values':values}
 from .codec import replace_scalar_curves
 result,report=replace_scalar_curves(raw,edits);p=pathlib.Path(path)
 if p.suffix.lower()!='.oct':raise ValueError('Choose a new .oct filename')
 with p.open('xb') as f:f.write(result)
 p.with_suffix('.oct.report.json').write_text(json.dumps(report,indent=2));obj['di_last_export']=str(p.resolve());return report

class DIHeadImport(bpy.types.Operator):
 bl_idname='di.import_elsa_head';bl_label='Add editable Elsa head control'
 def execute(self,context):
  try:
   root=pathlib.Path(r'F:\DisneyInfinityPortalTest');path=next((root/'ElsaSceneResearch/InstalledGameAssetCheck').rglob('elsa_bm_idle_specific03.oct'));import_head(path)
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
  return {'FINISHED'}
from bpy_extras.io_utils import ExportHelper
class DIHeadExport(bpy.types.Operator,ExportHelper):
 bl_idname='di.export_elsa_head';bl_label='Export head edit to new OCT';filename_ext='.oct';check_existing=False
 filter_glob:bpy.props.StringProperty(default='*.oct',options={'HIDDEN'})
 def execute(self,context):
  try:export_head(context.active_object,self.filepath)
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
  self.report({'INFO'},'OCT written; run native preview to evaluate edited mesh');return {'FINISHED'}
class DIHeadPanel(bpy.types.Panel):
 bl_label='DI native head edit';bl_idname='VIEW3D_PT_di_head';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='DI OCT'
 def draw(self,context):
  self.layout.operator(DIHeadImport.bl_idname);self.layout.operator(DIHeadExport.bl_idname);self.layout.operator('di.preview_elsa_head');self.layout.label(text='Elsa idle03 head rotation only')
def register():
 for cls in (DIHeadImport,DIHeadExport,DIHeadPanel,DIHeadPreview):bpy.utils.register_class(cls)
def unregister():
 for cls in reversed((DIHeadImport,DIHeadExport,DIHeadPanel,DIHeadPreview)):bpy.utils.unregister_class(cls)


class DIHeadPreview(bpy.types.Operator):
 bl_idname='di.preview_elsa_head';bl_label='Refresh mesh from exported OCT'
 def execute(self,context):
  import subprocess
  obj=context.active_object
  if obj is None or 'di_last_export' not in obj:self.report({'ERROR'},'Select the source-control rig and export a new OCT first');return {'CANCELLED'}
  root=pathlib.Path(r'F:\DisneyInfinityPortalTest');python=pathlib.Path(r'C:\Users\Kurar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe');source=pathlib.Path(obj['di_last_export'])
  self.output=source.with_name(source.stem+'_native_preview.json');self.logpath=source.with_name(source.stem+'_native_preview.log')
  try:
   self.log=self.logpath.open('w');self.process=subprocess.Popen([str(python),str(root/'BlenderElsaImporter/preview_head_edit.py'),str(source),'--output',str(self.output)],stdout=self.log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  except Exception as e:
   if hasattr(self,'log'):self.log.close()
   self.report({'ERROR'},str(e));return {'CANCELLED'}
  self.timer=context.window_manager.event_timer_add(.5,window=context.window);context.window_manager.modal_handler_add(self);context.workspace.status_text_set('DI native evaluator is rebuilding the mesh preview; Esc cancels.');return {'RUNNING_MODAL'}
 def modal(self,context,event):
  if event.type=='ESC':
   self.process.terminate();self.process.wait(timeout=5);self.finish(context);self.report({'INFO'},'Preview cancelled');return {'CANCELLED'}
  if event.type!='TIMER':return {'PASS_THROUGH'}
  code=self.process.poll()
  if code is None:return {'PASS_THROUGH'}
  self.finish(context)
  if code:self.report({'ERROR'},'Native preview failed; see '+str(self.logpath));return {'CANCELLED'}
  try:
   import importlib.util,sys
   path=pathlib.Path(r'F:\DisneyInfinityPortalTest\BlenderElsaImporter\io_scene_di_elsa.py');spec=importlib.util.spec_from_file_location('di_preview_mesh_loader',path);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
   rig,mesh,data,C=module.load_bundle(str(self.output.with_suffix('.di_elsa')));rig.location.x+=1;mesh.location.x+=1
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
  self.report({'INFO'},'Native-evaluated edited mesh loaded beside the original');return {'FINISHED'}
 def finish(self,context):
  context.window_manager.event_timer_remove(self.timer);context.workspace.status_text_set(None);self.log.close()

