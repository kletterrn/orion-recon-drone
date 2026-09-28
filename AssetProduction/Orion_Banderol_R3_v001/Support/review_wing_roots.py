from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1);rev=s['revision'].replace('D_','')
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear();return t
body=tree(bpy.data.objects['ORION_FUSELAGE']);report={'revision':rev,'fresh_master_reopen':True,'roots':[]}
for label in ['L','R']:
 o=bpy.data.objects['ORION_WING_ROOT_BLEND_'+label];bm=bmesh.new();bm.from_mesh(o.data);non=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);volume=bm.calc_volume();bm.free()
 inner=min(abs(v.co.x) for v in o.data.vertices);cap=[o.matrix_world@v.co for v in o.data.vertices if abs(abs(v.co.x)-inner)<1e-6]
 distances=[]
 for p in cap:
  point,normal,idx,dist=body.find_nearest(p);distances.append((p-point).dot(normal))
 report['roots'].append({'name':o.name,'nonmanifold_edges':non,'degenerate_faces':deg,'positive_volume':volume>0,'inner_cap_points':len(cap),'cap_max_signed_distance':max(distances),'cap_entirely_inside_evaluated_body':max(distances)<-1e-5,'body_surface_intersection_pairs':len(tree(o).overlap(body))})
s.cycles.samples=32;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=True
views=[('Forward',None,None,None),('ThreeQuarter',(2.7,1.8,2.4),(0,-1.15,.29),3.5),('Top',(0,-1.1,6),(0,-1.1,.30),3.9)]
for name,pos,target,scale in views:
 if pos:
  d=bpy.data.cameras.new('ROOT_'+name);cam=bpy.data.objects.new('ROOT_'+name,d);s.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale
 else:cam=bpy.data.objects['ORION_CAM_WING_ROOT_FORWARD']
 s.camera=cam;s.render.filepath=str(P/f'Previews/D_{rev}_Wing_Root_{name}.png');bpy.ops.render.render(write_still=True)
(P/f'Documentation/D_wing_root_validation_{rev}.json').write_text(json.dumps(report,indent=2))
print('ROOT_VALIDATION',report)
