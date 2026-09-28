from pathlib import Path
import bpy
I=Path('C:/Users/david/Desktop/RECON DRONES/Integration/RC8')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v014.blend'))
for o in bpy.data.objects:
 if o.name.startswith('ORION_RC8_NOSE_DOOR_INNER_RELIEF') and o.name not in bpy.data.collections['ORION_ASSET'].all_objects:bpy.data.collections['ORION_ASSET'].objects.link(o)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v015.blend'),relative_remap=True)
