import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Users/david/Desktop/RECON DRONES/Integration/RC8/Blender/Orion_RC8_Skinned_v003.blend')
for n in ['ORION_NOSE_UPPER_STRUT','ORION_NOSE_SLIDING_SECTION','ORION_NOSE_FORK_1','ORION_MAIN_L_UPPER_STRUT','ORION_MAIN_L_SLIDING_SECTION']:
 o=bpy.data.objects[n];p=[o.matrix_world@Vector(v) for v in o.bound_box];print(n,'LOC',list(o.matrix_world.translation),'BOUND',[[min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)]],flush=True)
