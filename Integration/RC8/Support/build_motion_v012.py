from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v012.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v011.blend'));s=bpy.context.scene;s.frame_set(1)
body=bpy.data.objects['ORION_FUSELAGE'];e=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear()
for side in [-1,1]:
 lip=bpy.data.objects[f'ORION_NOSE_OPENING_LIP_{side}']
 for sp in lip.data.splines:
  for p in sp.points:
   hit=t.ray_cast(Vector((p.co.x,p.co.y,-2)),Vector((0,0,1)))[0]
   assert hit is not None
   p.co.z=hit.z+.0025
 lip['RC8_change']='Seal seated into actual widened-bay skin surface, leaving 0.5 mm exposed; no floating lip in door travel'
s['RC8_status']='v012 motion candidate; 120-frame v011 gear/body/payload sweep clear; final bidirectional and assembly validation pending'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
# Publish the new Banderol presentation controls and exterior hinge pieces.
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Banderol_RC8_Motion_v003.blend'));pub=bpy.data.collections['BDL_ASSET_FIT']
for o in bpy.data.collections['10_SOURCE'].all_objects:
 if o.name not in pub.all_objects:pub.objects.link(o)
for n in ['BDLF_CTRL_WING_L','BDLF_CTRL_WING_R']:
 o=bpy.data.objects[n]
 if o.name not in pub.all_objects:pub.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Banderol_RC8_Motion_v004.blend'),relative_remap=True)
print('RC8_V012_SAVED',flush=True)
