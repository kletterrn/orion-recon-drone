from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1];REV='v001';check=P/f'Banderol/checkpoints/S8000_Banderol_F_primary_{REV}.blend'
assert not check.exists()
for sub in ['Banderol/checkpoints','Banderol/textures','Banderol/exports']:(P/sub).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='BANDEROL_GEOMETRY_REVIEW';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
def coll(n,parent=s.collection):c=bpy.data.collections.new(n);parent.children.link(c);return c
refs=coll('00_REFERENCE');src=coll('10_SOURCE');pres=coll('20_PRESENTATION');rig=coll('30_RIG_HELPERS');exp=coll('40_EXPORT');studio=coll('50_CAMERAS_LIGHTS')
root=bpy.data.objects.new('BANDEROL_ROOT',None);rig.objects.link(root);root.empty_display_type='ARROWS';root.empty_display_size=.2
params={'nominal_length_m':5.0,'reported_body_diameter_m':.30,'provisional_wing_span_m':2.2,'estimated_tail_tip_radius_m':.46,'nose_join_y_m':1.7,'main_wing_leading_root_y_m':1.18,'tail_leading_root_y_m':-1.52,'tail_count_selected':3,'axes':'+Y forward +X right +Z up','geometry_status':'Evidence-limited exterior reconstruction; primary form for review','wing_span_status':'C candidate; official Size 2.2 m label does not establish span','source':'https://war-sanctions.gur.gov.ua/en/page-s8000-banderol'}
for k,v in params.items():root[k]=v
root['stage']='F_PRIMARY_FORM';root['evidence']='Nominal public dimensions; C illustrated exterior station dimensions';root['wing_pose']='Illustration deployed; no folding mechanism or stowed pose authored'
def material(n,col,rough=.5,metal=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
grey=material('BDL_LIGHT_GREY_REVIEW',(.49,.51,.52));rim=material('BDL_REAR_RIM_REVIEW',(.32,.34,.35),.38,.7);dark=material('BDL_REAR_RECESS_DARK',(.024,.027,.028),.8);clay=material('BDL_NEUTRAL_CLAY',(.43,.43,.43),.75)
def mesh(n,v,f,mat=grey,smooth=True):
 d=bpy.data.meshes.new(n+'_MESH');d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(n,d);src.objects.link(o);o.parent=root;d.materials.append(mat)
 for p in d.polygons:p.use_smooth=smooth and len(p.vertices)==4
 o['evidence']='C dimensions/hidden completion; illustrated silhouette basis';return o
N=96
def body(n,stations):
 v=[];f=[]
 for y,rx,top,bottom in stations:
  for j in range(N):
   a=2*math.pi*j/N;z=(top+bottom)/2+(top-bottom)/2*math.sin(a);v.append((rx*math.cos(a),y,z))
 for k in range(len(stations)-1):
  for j in range(N):f.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 f += [tuple(reversed(range(N))),tuple((len(stations)-1)*N+j for j in range(N))]
 return mesh(n,v,f)
body('BDL_BODY',[(-1.89,.149,.149,-.132),(-1.60,.15,.15,-.134),(-1.0,.15,.15,-.134),(0,.15,.15,-.134),(1.0,.15,.15,-.134),(1.70,.15,.15,-.132)])
nose=body('BDL_NOSE',[(1.70,.15,.15,-.132),(1.84,.145,.144,-.132),(2.00,.128,.115,-.130),(2.15,.097,.070,-.126),(2.29,.066,.012,-.120),(2.41,.032,-.051,-.113),(2.48,.009,-.096,-.109),(2.50,.002,-.105,-.109)])
nose['evidence']='C wedge nose/flattened underside from official visualization and R5; no measured nose sections'
# Rear cowling with an actual lined cavity; the visible depth stops at a closed backing.
v=[];f=[]
rear=[(-1.89,.149,.149,-.132),(-2.10,.14,.142,-.127),(-2.29,.117,.120,-.113),(-2.43,.103,.103,-.100)]
for y,rx,top,bottom in rear:
 for j in range(N):
  a=j*2*math.pi/N;v.append((rx*math.cos(a),y,(top+bottom)/2+(top-bottom)/2*math.sin(a)))
for k in range(3):
 for j in range(N):f.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
f.append(tuple(reversed(range(N))))
# inward ring and closed shallow lining
for y,r in [(-2.43,.088),(-2.26,.088)]:
 for j in range(N):a=j*2*math.pi/N;v.append((r*math.cos(a),y,r*math.sin(a)))
for k in [3,4]:
 for j in range(N):f.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
f.append(tuple(5*N+j for j in range(N)))
cowl=mesh('BDL_REAR_COWLING_LINED',v,f);cowl.data.materials.append(dark)
for p in cowl.data.polygons:
 if p.center.y< -2.25 and p.index>=3*N+1:p.material_index=1
# A separate protruding metal rim and lip follows the attributed rear photo.
v=[];f=[]
for y,r in [(-2.405,.097),(-2.50,.097),(-2.50,.087),(-2.405,.087)]:
 for j in range(N):a=j*2*math.pi/N;v.append((r*math.cos(a),y,r*math.sin(a)))
for k in range(4):
 for j in range(N):f.append((k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j))
lip=mesh('BDL_REAR_OPENING_RIM',v,f,rim);lip['evidence']='A visible rear metal lip in GUR-attributed photograph republished by TWZ; C metric diameter/depth'
def surface(n,side,radial,stations):
 # Closed thin visual wing profiles; no performance specification implied.
 M=40;outline=[]
 for i in range(M+1):u=(1-math.cos(math.pi*i/M))/2;outline.append((u,1))
 for i in range(M,-1,-1):u=(1-math.cos(math.pi*i/M))/2;outline.append((u,-1))
 v=[];f=[];K=len(outline)
 for r,y,chord,thick in stations:
  for u,sign in outline:
   hh=max(.0006,thick*(.2969*math.sqrt(u)-.126*u-.3516*u*u+.2843*u**3-.1015*u**4)/.10003)
   if radial=='X':v.append((side*r,y-u*chord,-.074+sign*hh))
   elif radial=='TAIL_X':v.append((side*r,y-u*chord,sign*hh))
   else:v.append((sign*hh,y-u*chord,r))
 for k in range(len(stations)-1):
  for j in range(K):f.append((k*K+j,k*K+(j+1)%K,(k+1)*K+(j+1)%K,(k+1)*K+j))
 f += [tuple(reversed(range(K))),tuple((len(stations)-1)*K+j for j in range(K))]
 return mesh(n,v,f)
for side,label in [(-1,'L'),(1,'R')]:
 surface('BDL_WING_'+label,side,'X',[(.095,1.18,.44,.020),(.18,1.16,.435,.019),(.55,1.07,.39,.014),(1.05,.92,.31,.010),(1.10,.90,.27,.006)])
 # Root fairing joins the wing visibly into the body's lower shoulder.
 fair=body('BDL_WING_ROOT_FAIRING_'+label,[(.64,.08,.025,-.127),(.76,.18,.01,-.128),(1.02,.19,.01,-.126),(1.19,.08,.01,-.125)])
 for vertex in fair.data.vertices:vertex.co.x=side*(abs(vertex.co.x)*.65+.04)
 # Keep fairings volumetric, not folded mirror surfaces.
 # Regenerate x range from original signed cross-section rather than abs.
 for ringindex in range(4):
  for j in range(N):
   a=j*2*math.pi/N;radii=[.08,.18,.19,.08];fair.data.vertices[ringindex*N+j].co.x=side*(radii[ringindex]*.65*math.cos(a)+.085)
 bm=bmesh.new();bm.from_mesh(fair.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(fair.data);bm.free()
 surface('BDL_TAIL_'+label,side,'TAIL_X',[(.10,-1.52,.45,.012),(.17,-1.54,.42,.011),(.43,-1.67,.31,.007),(.46,-1.70,.26,.004)])
surface('BDL_TAIL_TOP',1,'TAIL_Z',[(.10,-1.52,.45,.012),(.17,-1.54,.42,.011),(.43,-1.67,.31,.007),(.46,-1.70,.26,.004)])
for n in ['BDL_TAIL_L','BDL_TAIL_R','BDL_TAIL_TOP']:bpy.data.objects[n]['evidence']='A/B three visible tail directions in attributed rear photo and official illustration; C sections, metric span/sweep'
attach=bpy.data.objects.new('BANDEROL_ATTACH_ROOT',None);rig.objects.link(attach);attach.parent=root;attach.location=(0,0,.15);attach.empty_display_type='ARROWS';attach.empty_display_size=.18;attach['status']='Scene alignment helper only; Orion carriage datum unverified'
publish=coll('BDL_ASSET');publish.children.link(src);publish.children.link(rig)
s.world=bpy.data.worlds.new('BDL_NEUTRAL_WORLD');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,loc,energy,size in [('Key',(-3,3,5),950,5),('Fill',(3,2,2),650,4),('Rear',(0,-4,4),900,3)]:
 d=bpy.data.lights.new('BDL_LIGHT_'+name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.54));floor=bpy.context.object;floor.name='BDL_REVIEW_FLOOR'
for c in list(floor.users_collection):c.objects.unlink(floor)
pres.objects.link(floor);floor.data.materials.append(material('BDL_FLOOR',(.13,.14,.15),.8))
views=[('Hero',(4,6,3),(0,0,0),6),('Front',(0,7,0),(0,0,0),2.6),('Rear',(0,-7,.1),(0,-2.35,0),1.3),('Left',(-7,0,0),(0,0,0),5.7),('Right',(7,0,0),(0,0,0),5.7),('Top',(0,0,7),(0,0,0),5.7),('Underside',(0,0,-7),(0,0,0),5.7),('Nose',(-1,3.6,.65),(0,1.95,-.04),1.7),('Rear_Close',(-1.0,-3.5,.6),(0,-2.15,0),1.5),('Clay',(4,6,3),(0,0,0),6)]
for name,pos,target,scale in views:
 d=bpy.data.cameras.new('BDL_CAM_'+name);o=bpy.data.objects.new(d.name,d);studio.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale
s.camera=bpy.data.objects['BDL_CAM_Hero'];s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type!='CPU'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s['stage']='F_REFERENCE_LIMITED_PRIMARY_FORM';s['revision']='F_'+REV;s['status']='Review before detailing; scale and illustration uncertainty recorded'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(check),copy=True)
(P/f'Documentation/F_parameters_{REV}.json').write_text(json.dumps(params,indent=2));print('BANDEROL_F_SAVED',len(src.objects),'source objects')
