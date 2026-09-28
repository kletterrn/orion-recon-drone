import bpy
from pathlib import Path
p=Path(r'C:\Users\david\Desktop\RECON DRONES\AssetProduction\Orion_Banderol_R3_v001');bpy.ops.wm.open_mainfile(filepath=str(p/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1)
for name in ['ORION_SENSOR_MAIN_RECESS_CUTTER','ORION_SENSOR_MAIN_OPTICAL_SURFACE','ORION_MAIN_R_UPPER_STRUT','ORION_SENSOR_PITCH','ORION_MAIN_R_GEAR_PIVOT']:
 o=bpy.data.objects[name];print(name,'QUAT',o.rotation_quaternion[:],'MODE',o.rotation_mode,'ANIM',o.animation_data, 'PARENT',o.parent.name,'BASIS',o.matrix_basis,'INV',o.matrix_parent_inverse,'WORLD',o.matrix_world)
