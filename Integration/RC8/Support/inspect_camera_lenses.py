import bpy,json
from mathutils import Vector
from pathlib import Path
p=Path(r'C:/Users/david/Desktop/RECON DRONES/Integration/RC8')
bpy.ops.wm.open_mainfile(filepath=str(p/'Blender/Orion_RC8_Motion_v022.blend'))
bpy.context.scene.frame_set(1)
rows=[]
for o in bpy.data.objects:
 if any(x in o.name.upper() for x in ['LENS','OPTIC','SENSOR_PITCH','SENSOR_YAW']):
  rows.append({'name':o.name,'position':list(o.matrix_world.translation),'bounds_center':list(sum((o.matrix_world@Vector(c) for c in o.bound_box),Vector())/8),'dimensions':list(o.dimensions),'parent':o.parent.name if o.parent else None})
(p/'Reports/camera_lens_positions.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))

