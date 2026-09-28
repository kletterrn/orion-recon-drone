from pathlib import Path
import bpy,bmesh
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v013.blend'));s=bpy.context.scene
# Small inner-face door relief at the isolated tire contact; tire size and movement remain unchanged.
s.frame_set(62,subframe=.5);door=bpy.data.objects['ORION_NOSE_DOOR_SHELL_1'];tire=bpy.data.objects['ORION_NOSE_TIRE'];e=tire.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(e);bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bm.to_mesh(mesh);bm.free();cut=bpy.data.objects.new('ORION_RC8_NOSE_DOOR_INNER_RELIEF',mesh);bpy.data.collections['ORION_GEAR_BAYS'].objects.link(cut)
cut.matrix_world=e.matrix_world;cut.scale*=1.03;bpy.context.view_layer.update();M=cut.matrix_world.copy();cut.parent=door;cut.matrix_parent_inverse=door.matrix_world.inverted();cut.matrix_world=M;cut.hide_render=True;cut.display_type='WIRE';cut.hide_set(True)
old=door.modifiers.get('RC8_inner_face_tire_clearance');door.modifiers.remove(old) if old else None
mod=door.modifiers.new('RC8_inner_face_tire_clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
door['RC8_change']='Local inner-face tire relief, evaluated at the prior isolated half-frame contact; exterior profile must be reviewed'

s.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v014.blend'),relative_remap=True)
print('RC8_V014_SAVED',flush=True)
