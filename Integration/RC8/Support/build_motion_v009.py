from pathlib import Path
import bpy
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v009.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v008.blend'));s=bpy.context.scene;s.frame_set(120)
for hinge in [o for o in bpy.data.objects if o.type=='EMPTY' and 'DOOR_HINGE' in o.name]:
 barrels=sorted([o for o in hinge.children if 'BARREL' in o.name],key=lambda o:o.matrix_world.translation.y)
 ys=[.07,1.45] if 'NOSE_' in hinge.name else [-2.36,-.56]
 for index,(barrel,y) in enumerate(zip(barrels,ys)):
  dy=y-barrel.matrix_world.translation.y
  for o in [barrel,bpy.data.objects[hinge.name+f'_RC8_FIXED_EAR_{index}'],bpy.data.objects[hinge.name+f'_RC8_MOVING_EAR_{index}']]:
   M=o.matrix_world.copy();M.translation.y+=dy;o.matrix_world=M
 hinge['RC8_hinge_stations']='Bearing stations at bay ends, outside wheel/strut travel; illustrative visual reconstruction'
s.frame_set(1);s['RC8_status']='v009 door bearing station correction; coordinated timing pending'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v008.blend'))
for lib in bpy.data.libraries:
 if 'Orion_RC8_Motion_v008' in lib.filepath:lib.filepath=str(dest)
 lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath))
bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v009.blend'),relative_remap=True)
print('RC8_V009_SAVED',flush=True)
