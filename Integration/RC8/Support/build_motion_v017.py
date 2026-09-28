from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
I=Path('C:/Users/david/Desktop/RECON DRONES/Integration/RC8');bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v016.blend'));s=bpy.context.scene;s.frame_set(62,subframe=.5)
door=bpy.data.objects['ORION_NOSE_DOOR_SHELL_1'];mod=door.modifiers['RC8_inner_face_tire_clearance'];cut=mod.object;tire=bpy.data.objects['ORION_NOSE_TIRE'];e=tire.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh();v=[e.matrix_world@p.co for p in mesh.vertices];e.to_mesh_clear();centre=sum(v,Vector())/len(v);bm=bmesh.new()
for p in v:bm.verts.new(centre+(p-centre)*1.035)
bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free();cut.parent=None;cut.matrix_world=Matrix.Identity(4);cut.parent=door;cut.matrix_parent_inverse=door.matrix_world.inverted();cut.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();r=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return r
print('NOSE_CONTACT',len(tree(door).overlap(tree(tire))),flush=True)
s.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v017.blend'),relative_remap=True)
