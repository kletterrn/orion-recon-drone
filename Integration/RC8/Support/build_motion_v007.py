from pathlib import Path
import bpy,math
from mathutils import Quaternion
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v007.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v006.blend'));s=bpy.context.scene
for o in bpy.data.objects:
 if o.type!='EMPTY' or 'DOOR_HINGE' not in o.name:continue
 o.animation_data_clear();side=1 if ('MAIN_R' in o.name or o.name.endswith('_1') and 'NOSE_' in o.name) else -1
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame
  angle=180+40*max(0,min(1,(f-1)/19)) if f<=20 else 220*(1-max(0,min(1,(f-100)/20)))
  o.rotation_quaternion=Quaternion((0,1,0),math.radians(-side*angle));o.keyframe_insert('rotation_quaternion',frame=frame)
s.frame_set(1);s['RC8_status']='v007 offset door travel candidate; validation pending'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v006.blend'))
for lib in bpy.data.libraries:
 if 'Orion_RC8_Motion_v006' in lib.filepath:lib.filepath=str(dest)
 lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath))
bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v007.blend'),relative_remap=True)
print('RC8_V007_SAVED',flush=True)
