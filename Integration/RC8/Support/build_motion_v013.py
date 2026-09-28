from pathlib import Path
import bpy,json,math
from mathutils import Quaternion,Vector,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v013.blend'
assert not dest.exists()
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v012.blend'));s=bpy.context.scene
# Quaternion signs must remain continuous across 180 degrees. Component-wise interpolation of
# opposite-sign equivalent quaternions otherwise sends the door through the aircraft at subframes.
objects=[o for o in bpy.data.objects if o.animation_data and o.animation_data.action and o.rotation_mode=='QUATERNION']
samples={o.name:[] for o in objects}
for frame in range(1,241):
 s.frame_set(frame)
 for o in objects:
  q=o.rotation_quaternion.copy()
  if samples[o.name]:q.make_compatible(samples[o.name][-1])
  samples[o.name].append(q)
for o in objects:
 for frame,q in enumerate(samples[o.name],1):o.rotation_quaternion=q;o.keyframe_insert('rotation_quaternion',frame=frame)
# The two inner fork bars overlapped by 1.34 mm in the shared closed bay.
# A local 2 mm relief on the inner-facing edge preserves the extended axle/strut connections.
for name in ['ORION_MAIN_L_FORK_1','ORION_MAIN_R_FORK_-1']:
 o=bpy.data.objects[name];o.data=o.data.copy()
 for v in o.data.vertices:v.co.x*=.82;v.co.y*=.82
 o['RC8_change']='Local fork cross-section relief for shared-bay stowage; length and pivot unchanged'
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return BVHTree.FromPolygons(v,f)
# Small inner-face door relief at the isolated tire contact; tire size and movement remain unchanged.
s.frame_set(62,subframe=.5);door=bpy.data.objects['ORION_NOSE_DOOR_SHELL_1'];tire=bpy.data.objects['ORION_NOSE_TIRE'];e=tire.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(e);cut=bpy.data.objects.new('ORION_RC8_NOSE_DOOR_INNER_RELIEF',mesh);bpy.data.collections['ORION_GEAR_BAYS'].objects.link(cut)
cut.matrix_world=e.matrix_world;cut.scale*=1.012;bpy.context.view_layer.update();M=cut.matrix_world.copy();cut.parent=door;cut.matrix_parent_inverse=door.matrix_world.inverted();cut.matrix_world=M;cut.hide_render=True;cut.display_type='WIRE';cut.hide_set(True)
mod=door.modifiers.new('RC8_inner_face_tire_clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
door['RC8_change']='Local inner-face tire relief, evaluated at the prior isolated half-frame contact; exterior profile must be reviewed'
for action in bpy.data.actions:
 if action.library:continue
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);s['RC8_status']='v013 candidate: continuous quaternion signs, fork relief and local nose door timing; full subframe validation pending'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
(I/'Reports/motion_v013_changes.json').write_text(json.dumps({'nose_door_inner_relief_scale':1.012,'quaternion_objects':list(samples)},indent=2))
print('RC8_V013_SAVED',flush=True)


