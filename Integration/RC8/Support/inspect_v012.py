from pathlib import Path
import bpy,json
from mathutils import Vector
I=Path('C:/Users/david/Desktop/RECON DRONES/Integration/RC8')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v012.blend'))
s=bpy.context.scene
rows=[]
for f in [1,62.5,100,100.5,120]:
 s.frame_set(int(f),subframe=f%1)
 for n in ['ORION_MAIN_L_FORK_1','ORION_MAIN_R_FORK_-1','ORION_MAIN_L_DOOR_HINGE_1','ORION_NOSE_DOOR_HINGE_1']:
  o=bpy.data.objects[n];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());v=[e.matrix_world@Vector(p) for p in e.bound_box];rows.append(dict(frame=f,name=n,loc=list(o.matrix_world.translation),bounds=[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)],rotation=list(o.rotation_quaternion),parent=o.parent.name if o.parent else None))
print(json.dumps(rows))
print('CONTROLLERS',[(o.name,o.parent.name if o.parent else None) for o in bpy.data.objects if o.type=='EMPTY' and o.name.startswith('ORION_')])
