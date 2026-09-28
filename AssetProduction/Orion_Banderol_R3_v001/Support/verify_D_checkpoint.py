from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s
rev=s['revision'].replace('D_','')
source=bpy.data.collections['10_SOURCE'];body=bpy.data.objects['ORION_FUSELAGE'];nose=bpy.data.objects['ORION_NOSE_WHITE']
def digest(o):return hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'utf8') for v in o.data.vertices)).hexdigest()
before={o.name:digest(o) for o in [body,nose]}
bad=[]
for o in source.all_objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);boundary=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);vol=bm.calc_volume(signed=True);bm.free()
 if boundary or deg or vol<=0:bad.append({'object':o.name,'nonmanifold_edges':boundary,'degenerate_faces':deg,'volume':vol})
def tree(o,dg):
 ev=o.evaluated_get(dg);m=ev.to_mesh();verts=[ev.matrix_world@v.co for v in m.vertices];polys=[tuple(p.vertices) for p in m.polygons];t=BVHTree.FromPolygons(verts,polys,all_triangles=False,epsilon=0);ev.to_mesh_clear();return t
contacts=[];frames=list(range(1,161))
targets=[body]+[o for o in bpy.data.collections['ORION_GEAR_BAYS'].objects if o.type=='MESH' and any(k in o.name for k in ['BAY_SIDE','BAY_END','BAY_ROOF','DOOR_SHELL'])]+[bpy.data.objects['ORION_SENSOR_PITCH_HOUSING']]
moving=[o for o in bpy.data.collections['ORION_GEAR'].objects if o.type=='MESH']
for fr in frames:
 s.frame_set(fr);dg=bpy.context.evaluated_depsgraph_get();static={o.name:tree(o,dg) for o in targets};gear={o.name:tree(o,dg) for o in moving}
 for n,t in gear.items():
  for other,st in static.items():
   hits=t.overlap(st)
   if hits:contacts.append({'frame':fr,'moving':n,'obstacle':other,'surface_pairs':len(hits)})
 print('POSE_CHECK',fr,flush=True)
s.frame_set(1)
refs=[{'name':i.name,'filepath':i.filepath,'exists':Path(bpy.path.abspath(i.filepath)).exists()} for i in bpy.data.images if i.source=='FILE']
report={'fresh_master_reopen':True,'source_objects':len(source.all_objects),'base_mesh_defects':bad,'sampled_frames':frames,'gear_surface_contacts':contacts,'image_dependencies':refs,'body_nose_vertex_hashes':before,'scope':'Surface intersections against fuselage, bay liners, doors and sensor. Intentional gear-to-gear joints excluded. Containment and full swept-volume checks not established.'}
(P/f'Documentation/D_validation_{rev}.json').write_text(json.dumps(report,indent=2));print('D_VALIDATION',len(bad),'base defects',len(contacts),'surface-contact records')
