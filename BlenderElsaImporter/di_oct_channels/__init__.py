bl_info={'name':'DI OCT Source Channels (experimental)','author':'DI research project; container reader/writer by DisneyInfinityCreator contributors','version':(0,1,0),'blender':(5,0,0),'category':'Import-Export'}
import bpy,json,base64,pathlib
from bpy_extras.io_utils import ImportHelper,ExportHelper
from .codec import read,encode

def curves(obj):
 ad=obj.animation_data
 if not ad or not ad.action:return []
 return [fc for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags if bag.slot_handle==ad.action_slot.handle for fc in bag.fcurves]

def signature(obj):
 return [[fc.data_path,[[float(k.co.x),float(k.co.y),float(k.handle_left.x),float(k.handle_left.y),float(k.handle_right.x),float(k.handle_right.y),k.interpolation] for k in fc.keyframe_points]] for fc in curves(obj)]

def import_oct(path):
 raw=pathlib.Path(path).read_bytes();scene,node,blob,layout,channels=read(raw)
 if not channels:raise ValueError('No editable ordinary CICD source channels found')
 collection=bpy.data.collections.new(pathlib.Path(path).stem+' source channels');bpy.context.scene.collection.children.link(collection)
 root=bpy.data.objects.new(pathlib.Path(path).stem+' OCT template',None);collection.objects.link(root)
 root['di_oct_template']=base64.b64encode(raw).decode();root['source_filename']=pathlib.Path(path).name
 root['editing_scope']='Source channels only; does not export edits to mesh pose bones.'
 for c in channels:
  obj=bpy.data.objects.new(c['id'],None);collection.objects.link(obj);obj.parent=root;obj.empty_display_size=.01
  obj['di_channel']=json.dumps(c)
  for i,(t0,t1,values) in enumerate(zip(c['times'],c['times'][1:],c['controls'])):
   prop=f'segment_{i:03}';obj[prop]=values[0];data_path=f'["{prop}"]';obj.keyframe_insert(data_path=data_path,frame=1+t0*30)
   obj[prop]=values[3];obj.keyframe_insert(data_path=data_path,frame=1+t1*30)
   fc=next(f for f in curves(obj) if f.data_path==data_path);a,b=fc.keyframe_points
   a.interpolation='BEZIER';b.interpolation='BEZIER'
   for k in (a,b):k.handle_left_type='FREE';k.handle_right_type='FREE'
   width=(t1-t0)*30/3
   a.handle_left=(a.co.x-width,values[0]);a.handle_right=(a.co.x+width,values[1]);b.handle_left=(b.co.x-width,values[2]);b.handle_right=(b.co.x+width,values[3])
  obj['di_original_signature']=json.dumps(signature(obj))
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
 bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1; bpy.context.scene.frame_end=round(1+layout['time_range'][1]*30);bpy.context.scene.frame_set(1)
 return root

def export_oct(root,path):
 if 'di_oct_template' not in root:raise ValueError('Select an imported OCT template root or one of its channel objects')
 raw=base64.b64decode(root['di_oct_template']);edited={}
 source_channels=read(raw)[4]
 children={json.loads(o['di_channel'])['id']:o for o in root.children if 'di_channel' in o}
 if len(children)!=len(source_channels):raise ValueError('Source channels were deleted or duplicated; export refused')
 for c in source_channels:
  obj=children[c['id']]
  if any(fc.modifiers for fc in curves(obj)):raise ValueError('Curve modifiers are not supported')
  if json.dumps(signature(obj))==obj['di_original_signature']:continue
  fs={fc.data_path:fc for fc in curves(obj)};controls=[]
  if len(fs)!=len(c['controls']):raise ValueError('Adding/deleting curves is not supported')
  for i,(t0,t1) in enumerate(zip(c['times'],c['times'][1:])):
   fc=fs[f'["segment_{i:03}"]'];keys=fc.keyframe_points
   if len(keys)!=2:raise ValueError('Keep the original two keys per source segment')
   a,b=keys;f0,f1=1+t0*30,1+t1*30;width=(f1-f0)/3
   if max(abs(a.co.x-f0),abs(b.co.x-f1),abs(a.handle_right.x-(f0+width)),abs(b.handle_left.x-(f1-width)))>1e-4:raise ValueError('Only value/vertical-handle edits supported; keep key and handle times fixed')
   if a.interpolation!='BEZIER' or fc.modifiers:raise ValueError('Bezier segments without modifiers required')
   controls.append([float(a.co.y),float(a.handle_right.y),float(b.handle_left.y),float(b.co.y)])
  edited[c['id']]=controls
 result,report=encode(raw,edited)
 path=pathlib.Path(path)
 if path.suffix.lower()!='.oct':raise ValueError('Output must have .oct extension')
 # Never overwrite an existing file, including the original.
 with path.open('xb') as f:f.write(result)
 path.with_suffix('.oct.report.json').write_text(json.dumps(report,indent=2))
 return report

class DIImport(bpy.types.Operator,ImportHelper):
 bl_idname='import_scene.di_oct_channels';bl_label='DI OCT source channels';filename_ext='.oct'
 filter_glob:bpy.props.StringProperty(default='*.oct',options={'HIDDEN'})
 def execute(self,context):
  try:import_oct(self.filepath)
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
  return {'FINISHED'}
class DIExport(bpy.types.Operator,ExportHelper):
 bl_idname='export_scene.di_oct_channels';bl_label='DI OCT source channels (new file)';filename_ext='.oct';check_existing=False
 filter_glob:bpy.props.StringProperty(default='*.oct',options={'HIDDEN'})
 def execute(self,context):
  try:
   root=context.active_object
   if root and 'di_oct_template' not in root:root=root.parent
   if root is None:raise ValueError('Select the imported template root')
   report=export_oct(root,self.filepath);self.report({'INFO'},f'Wrote OCT: {len(report["changed_channels"])} changed channels')
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
  return {'FINISHED'}
def menu_import(self,context):self.layout.operator(DIImport.bl_idname,text='DI OCT source channels (.oct)')
def menu_export(self,context):self.layout.operator(DIExport.bl_idname,text='DI OCT source channels (.oct)')
def register():
 from . import head_controls
 head_controls.register()
 from . import arm_controls
 arm_controls.register()
 bpy.utils.register_class(DIImport);bpy.utils.register_class(DIExport);bpy.types.TOPBAR_MT_file_import.append(menu_import);bpy.types.TOPBAR_MT_file_export.append(menu_export)
def unregister():
 from . import head_controls
 from . import arm_controls
 arm_controls.unregister()
 head_controls.unregister()
 bpy.types.TOPBAR_MT_file_import.remove(menu_import);bpy.types.TOPBAR_MT_file_export.remove(menu_export);bpy.utils.unregister_class(DIExport);bpy.utils.unregister_class(DIImport)


