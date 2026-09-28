from pathlib import Path
import bpy,json
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';O=W/'Assets/ORD/Models/RC8';O.mkdir(parents=True,exist_ok=True)
reports=[]
for label,file,col,rig,name in [('Orion','Orion_RC8_Skinned_v002.blend','ORION_RC8_SKINNED_SOURCE','ORD_RC8_ExportRig','ORD_Orion_RC8_Probe'),('Banderol','Banderol_RC8_Motion_v004.blend','BDL_RC8_SKINNED_SOURCE','BDL_RC8_EXPORT_RIG','ORD_Banderol_RC8_Probe')]:
 bpy.ops.wm.open_mainfile(filepath=str(I/'Blender'/file));s=bpy.context.scene;s.frame_set(1);arm=bpy.data.objects[rig];collection=bpy.data.collections[col]
 for p in arm.pose.bones:
  for c in list(p.constraints):p.constraints.remove(c)
  p.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');arm.hide_set(False);arm.hide_render=False;arm.select_set(True)
 meshes=[]
 for o in collection.objects:
  if o.type!='MESH':continue
  o.hide_set(False);o.hide_render=False;o.select_set(True);o.name=o.name.removesuffix('_RC8_SKIN')+'_LOD0';meshes.append(o)
 bpy.context.view_layer.objects.active=arm
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False,use_armature_deform_only=False,path_mode='RELATIVE')
 reports.append(dict(asset=label,file=str(O/(name+'.fbx')),bones=[b.name for b in arm.data.bones],meshes=len(meshes),triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),basis=[list(r) for r in axis_conversion(to_forward='Z',to_up='Y').to_4x4()],purpose='minimal bind/skin/helper import; not final optimized or textured asset'))
(I/'Reports/minimal_export.json').write_text(json.dumps(reports,indent=2));print('RC8_MINIMAL_EXPORT_COMPLETE',flush=True)
