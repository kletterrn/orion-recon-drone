from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix,geometry
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8'
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v005.blend'));s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;oi=bpy.data.objects['ORION_LINKED_APPROVED']
def mesh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();M=oi.matrix_world@e.matrix_world;v=[M@p.co for p in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];e.to_mesh_clear();return v,f,BVHTree.FromPolygons(v,f,all_triangles=True)
def intersections(a,b):
 out=[]
 for src,dst in [(a,b),(b,a)]:
  for i in range(3):
   p=src[i];d=src[(i+1)%3]-p;l=d.length
   if l<1e-9:continue
   hit=geometry.intersect_ray_tri(*dst,d.normalized(),p,True)
   if hit is not None and -1e-6<=(hit-p).dot(d.normalized())<=l+1e-6:out.append(hit)
 return out
rows=[]
for frame in [1,60,105,115,120]:
 s.frame_set(frame);cache={};obstacles=[bpy.data.objects['ORION_FUSELAGE']]+[o for o in bpy.data.collections['ORION_GEAR_BAYS'].all_objects if o.type=='MESH' and 'BAY_SIDE' in o.name]
 for o in obstacles:cache[o.name]=mesh(o)
 for door in [o for o in bpy.data.collections['ORION_GEAR_BAYS'].all_objects if 'DOOR_SHELL' in o.name]:
  av,af,at=mesh(door);hinge=oi.matrix_world@door.parent.matrix_world.translation
  for name,(bv,bf,bt) in cache.items():
   overlaps=at.overlap(bt)
   if not overlaps:continue
   points=[]
   for a,b in overlaps:points.extend(intersections([av[j] for j in af[a]],[bv[j] for j in bf[b]]))
   rows.append({'frame':frame,'door':door.name,'obstacle':name,'triangle_pairs':len(overlaps),'intersection_points':len(points),'max_distance_from_hinge_axis_m':max((math.hypot(p.x-hinge.x,p.z-hinge.z) for p in points),default=None),'point_bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None})
(I/'Reports/door_interface_geometry_v005.json').write_text(json.dumps(rows,indent=2));print('DOOR_CONTACT_CLASSIFICATION_COMPLETE',flush=True)
