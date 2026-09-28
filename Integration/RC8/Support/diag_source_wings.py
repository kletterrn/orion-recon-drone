import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Users/david/Desktop/RECON DRONES/Integration/RC8/Blender/Banderol_RC8_Motion_v004.blend');s=bpy.context.scene;s.frame_set(1)
for n in ['BDLF_WING_L','BDLF_WING_R','BDLF_CTRL_WING_L','BDLF_CTRL_WING_R']:
 o=bpy.data.objects.get(n)
 if not o:continue
 print('OBJECT',n,'parent',o.parent.name if o.parent else None,'location',list(o.matrix_world.translation),'matrix',[list(row) for row in o.matrix_world]);
 if o.type=='MESH':
  p=[o.matrix_world@v.co for v in o.data.vertices];print('BOUND',[[min(q[k] for q in p) for k in range(3)],[max(q[k] for q in p) for k in range(3)]])
