"""Local correction of the two exposed wing-root end faces. Actual Blender execution."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
REV=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v012'
checkpoint=P/f'Orion/checkpoints/Orion_D_wing_root_fix_{REV}.blend'
if checkpoint.exists():raise RuntimeError('Do not overwrite an existing numbered checkpoint')
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_D_gear_bays_sensor_v010.blend'))
bpy.context.preferences.filepaths.save_version=0
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1)
source=bpy.data.collections['10_SOURCE'];air=bpy.data.collections['ORION_AIRFRAME'];root=bpy.data.objects['ORION_ROOT']
names=['ORION_WING_ROOT_BLEND_L','ORION_WING_ROOT_BLEND_R']
def digest(o):return hashlib.sha256(b''.join(str(tuple(v.co)).encode() for v in o.data.vertices)).hexdigest()
prior={o.name:digest(o) for o in source.all_objects if o.type=='MESH'}
def review_cam(n,pos,target,scale):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);bpy.data.collections['50_CAMERAS_LIGHTS'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;return o
cam=review_cam('ORION_CAM_WING_ROOT_FORWARD',(0,2.8,1.35),(0,-1.1,.29),3.1)
s.camera=cam;bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=True;s.cycles.samples=32;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.render.filepath=str(P/f'Previews/D_{REV}_Wing_Root_Before.png');bpy.ops.render.render(write_still=True)
ev=bpy.data.objects['ORION_FUSELAGE'].evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh()
body_tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in em.vertices],[tuple(f.vertices) for f in em.polygons]);ev.to_mesh_clear()
def shape(span,u,side):
 t=(span-.28)/(8-.28);c=1.33-.70*t;front=-.52-.13*t;z=.235+.02*t+c*.018*math.sin(math.pi*u)
 thickness=5*(.105-.025*t)*(.2969*math.sqrt(max(0,u))-.126*u-.3516*u*u+.2843*u**3-.1036*u**4)
 return (side*span,front-c*u,z),c*max(0,thickness)
for side,label in [(-1,'L'),(1,'R')]:
 old=bpy.data.objects['ORION_WING_ROOT_BLEND_'+label];old_data=old.data
 vertices=[];faces=[];ns=48;nc=64;nr=nc*2+1
 # Closed airfoil rings have shared leading/trailing vertices rather than degenerate faces.
 params=[(.5*(1-math.cos(math.pi*j/nc)),1) for j in range(nc+1)]+[(.5*(1-math.cos(math.pi*j/nc)),-1) for j in reversed(range(1,nc+1))]
 for k in range(ns+1):
  t=k/ns;span=.06+.96*t;blend=(1-t)**2
  ct=max(0,min(1,(span-.28)/.37));umax=1-.246*ct*ct*(3-2*ct)
  # Keep the buried lower shoulder above the bay roofs. Release smoothly outside them.
  lt=max(0,min(1,(span-.226)/.048));lower_weight=1-(lt*lt*(3-2*lt))
  for un,sign in params:
   u=un*umax;point,h=shape(span,u,side);weight=max(0,math.sin(math.pi*un))
   if sign>0:
    innerp,innerh=shape(.06,un,side);hit=body_tree.ray_cast(Vector((innerp[0],innerp[1],1)),Vector((0,0,-1)))[0]
    if hit is None:raise RuntimeError('Missing body crown intersection')
    cap_raise=innerp[2]+innerh+.085*weight**.7-.0004*weight
    cap_correction=max(0,cap_raise-(hit.z-.012))
    z=point[2]+h+(.085*weight**.7-cap_correction)*blend-.0004*weight
   else:
    wb=point[2]-h;z=wb+max(0,.230-wb)*lower_weight+.0004*weight
   vertices.append((point[0],point[1],z))
 for k in range(ns):
  for j in range(nr):faces.append((k*nr+j,k*nr+(j+1)%nr,(k+1)*nr+(j+1)%nr,(k+1)*nr+j))
 faces += [tuple(reversed(range(nr))),tuple(ns*nr+j for j in range(nr))]
 d=bpy.data.meshes.new(old.name+'_CONTINUOUS_ROOT_MESH');d.from_pydata(vertices,[],faces);d.update()
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 old.data=d;d.materials.append(bpy.data.materials['ORION_GREY_REVIEW'])
 for poly in d.polygons:poly.use_smooth=len(poly.vertices)==4
 old['revision']='D_'+REV;old['evidence']='C restrained visual root blend; R3/R7 compatible shoulder layout'
 old['connection']='Closed inner cap buried at +/-0.06m; continuous saddle extends to 1.02m; chord retreats before moving flap'
 old['status']='Wing-root correction pending visual review'
 if old_data.users==0:bpy.data.meshes.remove(old_data)
s['revision']='D_'+REV;s['model_status']='D v010 with local wing-root correction; pending review'
s.camera=bpy.data.objects['ORION_CAM_HERO'];bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint),copy=True)
after={o.name:digest(o) for o in source.all_objects if o.type=='MESH'}
changed=[n for n in prior if prior[n]!=after[n]]
assert sorted(changed)==sorted(names),changed
(P/f'Documentation/D_wing_root_change_{REV}.json').write_text(json.dumps({'previous_revision':'D_v010','checkpoint':str(checkpoint),'changed_meshes':changed,'all_other_source_mesh_vertices_unchanged':True,'inner_halfspan_m':.06,'outer_halfspan_m':1.02,'hidden_lower_root_min_z_m':.230,'scope':'Two fairing meshes only. Body/nose, span, gear, bays, sensor and animations unchanged.'},indent=2))
print('WING_ROOT_FIX_SAVED',changed)
