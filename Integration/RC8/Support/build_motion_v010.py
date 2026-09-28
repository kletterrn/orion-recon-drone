from pathlib import Path
import bpy
from mathutils import Vector
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v010.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v009.blend'));s=bpy.context.scene;s.frame_set(1);root=bpy.data.objects['ORION_ROOT'];gear=bpy.data.collections['ORION_GEAR']
for label in ['L','R']:
 ctrl=bpy.data.objects[f'ORION_MAIN_{label}_GEAR_PIVOT'];old=ctrl.matrix_world.translation.copy();children=list(ctrl.children);rest={o.name:o.matrix_world.copy() for o in children};ctrl.location.z-=.06;bpy.context.view_layer.update()
 for o in children:o.matrix_parent_inverse=ctrl.matrix_world.inverted();o.matrix_world=rest[o.name]
 for o in bpy.data.objects:
  if o.name.startswith(f'ORION_MAIN_{label}_BAY_ATTACHMENT_'):o.location.z-=.06
 new=ctrl.matrix_world.translation.copy();bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.027,depth=.06,location=(new+old)/2);o=bpy.context.object;o.name=f'ORION_MAIN_{label}_RC8_INTERNAL_PIVOT_KNUCKLE';o.data.materials.append(bpy.data.objects[f'ORION_MAIN_{label}_UPPER_STRUT'].data.materials[0])
 for c in list(o.users_collection):c.objects.unlink(o)
 gear.objects.link(o);M=o.matrix_world.copy();o.parent=ctrl;o.matrix_parent_inverse=ctrl.matrix_world.inverted();o.matrix_world=M;o['evidence']='C local hidden pivot correction; rest stance and exterior leg geometry unchanged'
 bpy.data.collections['ORION_ASSET'].objects.link(o)
 ctrl['RC8_pivot_correction_m']=-.06
s['RC8_status']='v010 hidden pivot correction candidate; new motion path pending'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v009.blend'))
for lib in bpy.data.libraries:
 if 'Orion_RC8_Motion_v009' in lib.filepath:lib.filepath=str(dest)
 lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath))
bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v010.blend'),relative_remap=True)
print('RC8_V010_SAVED',flush=True)
