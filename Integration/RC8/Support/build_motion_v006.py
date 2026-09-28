from pathlib import Path
import bpy,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v006.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v005.blend'));s=bpy.context.scene;s.frame_set(120)
root=bpy.data.objects['ORION_ROOT'];bays=bpy.data.collections['ORION_GEAR_BAYS'];mat=bpy.data.objects['ORION_MAIN_R_UPPER_STRUT'].data.materials[0]
def rod(name,a,b,r,parent):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=(a-b).length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');o.data.materials.append(mat)
 for c in list(o.users_collection):c.objects.unlink(o)
 bays.objects.link(o);M=o.matrix_world.copy();o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();o.matrix_world=M
 o['evidence']='C illustrative offset hinge connector, exterior visual detail only';return o
for hinge in [o for o in bpy.data.objects if o.type=='EMPTY' and 'DOOR_HINGE' in o.name]:
 old=hinge.matrix_world.translation.copy();children=list(hinge.children);rest={o.name:o.matrix_world.copy() for o in children}
 hinge.location.z=-.415;bpy.context.view_layer.update()
 for o in children:
  M=rest[o.name]
  if 'BARREL' in o.name:M.translation.z=-.415
  o.matrix_parent_inverse=hinge.matrix_world.inverted();o.matrix_world=M
 for index,barrel in enumerate([o for o in children if 'BARREL' in o.name]):
  pin=barrel.matrix_world.translation.copy();attachment=Vector((old.x,pin.y,old.z-.008))
  side=1 if old.x>0 else -1
  rod(hinge.name+f'_RC8_FIXED_EAR_{index}',(old.x+side*.016,pin.y,old.z+.006),(pin.x+side*.016,pin.y,pin.z),.009,root)
  rod(hinge.name+f'_RC8_MOVING_EAR_{index}',pin,attachment,.008,hinge)
 hinge['RC8_change']='Offset hinge below the curved belly; closed door surface unchanged; connector ears keep the door attached'
s.frame_set(1);s['RC8_status']='v006 offset-door hinge candidate; motion validation pending'
pub=bpy.data.collections.get('ORION_ASSET')
for o in bays.all_objects:
 if pub and o.name not in pub.all_objects:pub.objects.link(o)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
print('RC8_MOTION_V006_SAVED',flush=True)
