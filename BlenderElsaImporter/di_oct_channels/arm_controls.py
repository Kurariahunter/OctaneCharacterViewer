"""Verified original Elsa arm/head Euler and native relationship scalar inputs."""
import bpy,pathlib,json,base64,hashlib
from mathutils import Matrix
from bpy_extras.io_utils import ExportHelper
from .codec import read,replace_component_samples
from . import curves
R=pathlib.Path(r'F:\DisneyInfinityPortalTest')
def manifest():return json.loads(pathlib.Path(__file__).with_name('elsa-controls.json').read_text())
def path_for(c):return f'pose.bones["{c["bone"]}"].rotation_euler' if c['axis'] is not None else f'pose.bones["{c["bone"]}"]["{c["property"]}"]'
def key_for(c):return path_for(c)+'#'+str(c['axis'] if c['axis'] is not None else 0)
def fc_key(fc):return fc.data_path+'#'+str(fc.array_index)
def fc_signature(fc):return [[float(k.co.x),float(k.co.y),list(k.handle_left),list(k.handle_right),k.interpolation] for k in fc.keyframe_points]

def import_controls(path):
 raw=pathlib.Path(path).read_bytes();m=manifest()
 if hashlib.sha256(raw).hexdigest()!=m['template_sha256']:raise ValueError('Original PC Elsa idle_specific03 template required')
 channels={(c['curve'],c['dimension']):c for c in read(raw)[4]};mesh=json.loads((R/'OctaneCharacterViewer/Data/elsa-pc-mesh.json').read_text())
 col=bpy.data.collections.new('Elsa native arm and finger controls');bpy.context.scene.collection.children.link(col);arm=bpy.data.armatures.new('Elsa native source controls');obj=bpy.data.objects.new('Elsa OCT arms and fingers',arm);col.objects.link(obj)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.mode_set(mode='EDIT');C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
 for name in sorted({c['bone'] for c in m['controls']}):
  n=name.replace('Cntrl_','');n=n.replace('Thumb1_','Thumb1_');bone=arm.edit_bones.new(name);bone.head=(0,0,0);bone.tail=(0,0,.08);bone.use_deform=False
  if n not in mesh['bones']:raise ValueError('Missing source control display anchor '+n)
  v=mesh['bindposes'][mesh['bones'].index(n)];bind=Matrix([v[i:i+4] for i in range(0,16,4)]).inverted();rest=C@Matrix.Diagonal((1,-1,-1,1));rest.translation=(C@bind).translation;bone.matrix=rest;bone.length=.08
 bpy.ops.object.mode_set(mode='OBJECT');obj.show_in_front=True;obj.display_type='WIRE';arm.display_type='STICK'
 for pb in obj.pose.bones:
  pb.rotation_mode='ZXY';pb.lock_location=(True,True,True);pb.lock_scale=(True,True,True);pb.lock_rotation=tuple(not any(c['bone']==pb.name and c['axis']==i for c in m['controls']) for i in range(3))
 for c in m['controls']:
  pb=obj.pose.bones[c['bone']];channel=channels[c['curve'],c['dimension']];axis=c['axis']
  if axis is None:
   pb[c['property']]=0.;pb.id_properties_ui(c['property']).update(min=-100.,max=100.,soft_min=-100.,soft_max=100.,description='Native relationship input; not a bone angle')
  for t,v in zip(channel['times'],[v[0] for v in channel['controls']]+[channel['controls'][-1][-1]]):
   if axis is None:pb[c['property']]=v;pb.keyframe_insert(data_path=f'["{c["property"]}"]',frame=1+t*30,group=c['bone'])
   else:pb.rotation_euler[axis]=v;pb.keyframe_insert(data_path='rotation_euler',index=axis,frame=1+t*30,group=c['bone'])
  fc=next(f for f in curves(obj) if fc_key(f)==key_for(c))
  for i,k in enumerate(fc.keyframe_points):
   k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='FREE'
   if i:k.handle_left=(k.co.x-(channel['times'][i]-channel['times'][i-1])*10,channel['controls'][i-1][2])
   if i<len(channel['controls']):k.handle_right=(k.co.x+(channel['times'][i+1]-channel['times'][i])*10,channel['controls'][i][1])
 obj['di_arm_template']=base64.b64encode(raw).decode();obj['di_arm_signatures']=json.dumps({fc_key(f):fc_signature(f) for f in curves(obj)});obj['scope']='13 source-control bones, 48 channels; no independent ring/little digits; mesh updates after native refresh'
 bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=152;bpy.context.scene.frame_set(1);return obj

def export_controls(obj,path):
 if obj is None or 'di_arm_template' not in obj:raise ValueError('Select Elsa OCT arms and fingers')
 if obj.constraints or obj.animation_data.nla_tracks:raise ValueError('Constraints/NLA not supported')
 for pb in obj.pose.bones:
  if pb.rotation_mode!='ZXY' or pb.constraints or max(abs(v) for v in pb.location)>1e-7 or max(abs(v-1) for v in pb.scale)>1e-7:raise ValueError('Only source ZXY rotation and scalar properties supported')
 raw=base64.b64decode(obj['di_arm_template']);m=manifest();allowed={key_for(c):c for c in m['controls']};original=json.loads(obj['di_arm_signatures']);fs={fc_key(f):f for f in curves(obj)}
 if set(original)-set(fs):raise ValueError('A required source curve was deleted')
 lo,hi=read(raw)[3]['time_range'];count=round((hi-lo)*30);times=[lo+(hi-lo)*i/count for i in range(count+1)];edits={};changed=[]
 for key,fc in fs.items():
  if fc.modifiers:raise ValueError('Curve modifiers not supported')
  if key not in allowed:
   if '.rotation_euler#' in key and max(abs(fc.evaluate(1+t*30)) for t in times)<1e-7:continue
   raise ValueError('Unsupported animation channel '+key)
  if fc_signature(fc)==original[key]:continue
  c=allowed[key];values=[float(fc.evaluate(1+t*30)) for t in times]
  if c['axis'] is None and max(abs(v) for v in values)>100:raise ValueError('Finger relationship inputs must stay within -100..100')
  component=(c['curve'],c['dimension'])
  if component in edits:raise ValueError('Aliased source component edited twice')
  edits[component]={'times':times,'values':values};changed.append(c)
 result,report=replace_component_samples(raw,edits,30);report['source_controls_changed']=changed;report['handshape_limit']='No separate ring/little finger bones; faithful ASL I-love-you handshape needs rig/mesh changes'
 p=pathlib.Path(path)
 if p.suffix.lower()!='.oct':raise ValueError('Output must end in .oct')
 with p.open('xb') as f:f.write(result)
 p.with_suffix('.oct.report.json').write_text(json.dumps(report,indent=2));obj['di_last_export']=str(p.resolve());return report

class DIArmsImport(bpy.types.Operator):
 bl_idname='di.import_elsa_arms';bl_label='Add Elsa arm and finger controls'
 def execute(self,context):
  try:import_controls(next((R/'ElsaSceneResearch/InstalledGameAssetCheck').rglob('elsa_bm_idle_specific03.oct')))
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
  return {'FINISHED'}
class DIArmsExport(bpy.types.Operator,ExportHelper):
 bl_idname='di.export_elsa_arms';bl_label='Export arm/finger edit to OCT';filename_ext='.oct';check_existing=False
 filter_glob:bpy.props.StringProperty(default='*.oct',options={'HIDDEN'})
 def execute(self,context):
  try:export_controls(context.active_object,self.filepath)
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
  self.report({'INFO'},'OCT written; refresh native mesh to inspect');return {'FINISHED'}
class DIArmsPanel(bpy.types.Panel):
 bl_label='DI native arms and fingers';bl_idname='VIEW3D_PT_di_arms';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='DI OCT'
 def draw(self,context):
  self.layout.operator(DIArmsImport.bl_idname);self.layout.operator(DIArmsExport.bl_idname);self.layout.operator('di.preview_elsa_head',text='Refresh native arm/finger preview')
  pb=context.active_pose_bone
  if pb:
   for c in manifest()['controls']:
    if c['bone']==pb.name and c['axis'] is None:self.layout.prop(pb,f'["{c["property"]}"]',text=c['property'])
  self.layout.label(text='Finger values are native scalars')
  self.layout.label(text='No independent ring/little fingers')
def register():
 for c in (DIArmsImport,DIArmsExport,DIArmsPanel):bpy.utils.register_class(c)
def unregister():
 for c in reversed((DIArmsImport,DIArmsExport,DIArmsPanel)):bpy.utils.unregister_class(c)
