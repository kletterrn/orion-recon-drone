from pathlib import Path
import bpy,json
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v005.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v004.blend'));s=bpy.context.scene;s.frame_set(1)
root=bpy.data.objects['ORION_ROOT'];body=bpy.data.objects['ORION_FUSELAGE'];bays=bpy.data.collections['ORION_GEAR_BAYS']
# The counter-rotated forks need the small internal centre gap between the two
# wells. Preserve the exterior centre strip and door silhouette; join only the
# hidden interior above the belly skin.
for name in ['ORION_MAIN_L_BAY_SIDE_1','ORION_MAIN_R_BAY_SIDE_-1']:
 bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-1.46,-.0575));c=bpy.context.object;c.name='ORION_RC8_SHARED_MAIN_WELL_INTERNAL_CUTTER';c.scale=(.07,1.88,.545)
for col in list(c.users_collection):col.objects.unlink(c)
bpy.data.collections['ORION_RETAINED_CAVITY_CUTTERS'].objects.link(c);c.hide_render=True;c.parent=root
mod=body.modifiers.new('RC8_hidden_shared_well_clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c
mat=bpy.data.objects['ORION_MAIN_R_BAY_ROOF'].data.materials[0]
for name,loc,size in [('CENTRE_ROOF',(0,-1.46,.208),(.032,1.892,.006)),('CENTRE_END_FRONT',(0,-.517,-.07),(.032,.006,.55)),('CENTRE_END_REAR',(0,-2.403,-.07),(.032,.006,.55))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='ORION_RC8_MAIN_WELL_'+name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(o.users_collection):col.objects.unlink(o)
 bays.objects.link(o);o.parent=root;o.data.materials.append(mat);o['evidence']='C restrained shared main-bay interior completion, hidden clearance correction'
# Linear sampled channels make runtime interpolation reproducible and prevent overshoot.
for action in bpy.data.actions:
 if action.library:continue
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
publish=bpy.data.collections.get('ORION_ASSET')
if publish:
 for o in bays.all_objects:
  if o.name not in publish.all_objects:publish.objects.link(o)
s['RC8_status']='v005 candidate: hidden shared main-well centre clearance; fully sampled gear curves; acceptance pending'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
print('RC8_MOTION_V005_SAVED',flush=True)
