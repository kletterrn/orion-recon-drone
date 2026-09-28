from pathlib import Path
import bpy,bmesh
I=Path('C:/Users/david/Desktop/RECON DRONES/Integration/RC8')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v015.blend'));s=bpy.context.scene;s.frame_set(62,subframe=.5)
door=bpy.data.objects['ORION_NOSE_DOOR_SHELL_1'];mod=door.modifiers.get('RC8_inner_face_tire_clearance');cut=mod.object;bm=bmesh.new()
for v in cut.data.vertices:bm.verts.new(v.co)
bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free()
from mathutils.bvhtree import BVHTree
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();r=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return r
bpy.context.view_layer.update();print('NOSE_CONTACT',len(tree(door).overlap(tree(bpy.data.objects['ORION_NOSE_TIRE']))),flush=True)
s.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v016.blend'),relative_remap=True)
