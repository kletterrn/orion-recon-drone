import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
c=bpy.data.objects['ORION_CTRL_PROPELLER']; print('PROP_CONTROL',list(c.matrix_world.translation))
for n in ['ORION_PROPELLER_BLADE_A','ORION_PROPELLER_BLADE_B']:
 o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();vs=[ev.matrix_world@v.co for v in m.vertices];p=c.matrix_world.translation
 print(n, 'bounds',[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)], 'radius',max(((v.x-p.x)**2+(v.z-p.z)**2)**.5 for v in vs));ev.to_mesh_clear()
for n in ['ORION_FUSELAGE','ORION_MAIN_L_UPPER_STRUT']:
 o=bpy.data.objects[n];print(n,list(o.matrix_world.translation))
o=bpy.data.objects['ORION_FUSELAGE'];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear()
for y in [-2.15,-2.,-1.75,-1.5,-1.3]:
 print('BELLY',y,t.ray_cast(Vector((0,y,-2)),Vector((0,0,1)))[0])
for n in ['ORION_MAIN_L_BAY_SIDE_1','ORION_MAIN_L_DOOR_SHELL_1','ORION_MAIN_L_DOOR_HINGE_BARREL_1_-1','ORION_MAIN_L_BAY_ROOF_SUPPORT_0']:
 o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();vs=[ev.matrix_world@v.co for v in m.vertices];print(n,[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)]);ev.to_mesh_clear()
