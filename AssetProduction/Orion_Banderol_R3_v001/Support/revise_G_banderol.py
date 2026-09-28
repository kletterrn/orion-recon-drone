from pathlib import Path
import bpy,bmesh,math,json,hashlib,shutil
from mathutils import Vector
P=Path(__file__).resolve().parents[1];cp=P/'Banderol/checkpoints/S8000_Banderol_G_shape_v001.blend'
assert not cp.exists()
bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'))
s=bpy.context.scene;src=bpy.data.collections['10_SOURCE'];root=bpy.data.objects['BANDEROL_ROOT'];grey=bpy.data.materials['BDL_LIGHT_GREY_REVIEW']
def material(n,col,metal=0,rough=.55):
 m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*col,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
grey.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.24,.255,.26,1)
seam=material('BDL_PANEL_SEAL',(.065,.07,.072));metal=material('BDL_SMALL_HARDWARE',(.29,.30,.31),.6);gold=material('BDL_TOP_LOOP_BRONZE',(.39,.24,.09),.55)
def mesh(n,v,f,mat=grey):
 if n in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 d=bpy.data.meshes.new(n+'_MESH');d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(n,d);src.objects.link(o);o.parent=root;d.materials.append(mat)
 for p in d.polygons:p.use_smooth=len(p.vertices)==4
 o['evidence']='User R12/R13 illustrations: visible feature; C metric dimensions and hidden completion';return o
N=128
def section(a,rx,top,bot,p=3.6):
 c=math.cos(a);q=math.sin(a);return (rx*math.copysign(abs(c)**(2/p),c),(top+bot)/2+(top-bot)/2*math.copysign(abs(q)**(2/p),q))
def loft(n,stations):
 v=[];f=[]
 for y,rx,t,b,p in stations:
  for j in range(N):x,z=section(j*math.tau/N,rx,t,b,p);v.append((x,y,z))
 for k in range(len(stations)-1):
  for j in range(N):f.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 f.extend([tuple(reversed(range(N))),tuple((len(stations)-1)*N+j for j in range(N))]);return mesh(n,v,f)
stations=[(-1.89,.149,.165,-.157,3.6),(-1.65,.15,.17,-.16,3.8),(-.8,.15,.17,-.16,3.8),(0,.15,.17,-.16,3.8),(.9,.15,.17,-.16,3.8),(1.48,.15,.17,-.16,3.6)]
loft('BDL_BODY',stations)
ns=[(1.48,.15,.17,-.16,3.6),(1.63,.149,.165,-.16,3.5),(1.78,.145,.147,-.159,3.4),(1.96,.132,.108,-.156,3.2),(2.13,.107,.045,-.15,3),(2.28,.074,-.023,-.141,2.9),(2.40,.04,-.081,-.13,2.7),(2.48,.011,-.111,-.121,2.4),(2.5,.001,-.118,-.12,2)]
loft('BDL_NOSE',ns)
# Retain lined rear cavity, reshape only outer cowling rings to join the revised casing.
cowl=bpy.data.objects['BDL_REAR_COWLING_LINED'];rear=[(-1.89,.149,.165,-.157,3.6),(-2.10,.14,.153,-.142,3.2),(-2.29,.117,.125,-.119,2.7),(-2.43,.103,.103,-.100,2)]
for k,(_,rx,t,b,p) in enumerate(rear):
 for j in range(96):x,z=section(j*math.tau/96,rx,t,b,p);cowl.data.vertices[k*96+j].co=(x,rear[k][0],z)
# Front-render span/body ratio ~3.1. This supersedes ambiguous 2.2 m candidate, not reported body diameter.
for label in ['L','R']:
 o=bpy.data.objects['BDL_WING_'+label]
 for v in o.data.vertices:
  v.co.x*=.43;v.co.z-=.089
 o=bpy.data.objects['BDL_WING_ROOT_FAIRING_'+label]
 for v in o.data.vertices:v.co.z-=.04
for label in ['L','R']:
 o=bpy.data.objects['BDL_TAIL_'+label]
 for v in o.data.vertices:v.co.x*=.91;v.co.z-=abs(v.co.x)*.09
def curve(n,points,r,mat,closed=False):
 d=bpy.data.curves.new(n+'_CURVE','CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=3;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(n,d);src.objects.link(o);o.parent=root;d.materials.append(mat);o['evidence']='R12/R13 visible exterior cue; C dimensional reconstruction';return o
for i,y in enumerate([-1.29,-.66,1.48]):
 pts=[]
 for j in range(N):x,z=section(j*math.tau/N,.1505,.1705,-.1605);pts.append((x,y,z))
 curve('BDL_CASE_SEAM_'+str(i),pts,.00055,seam,True)
# Nose inset boundary, following an actual nose station, not a painted flat circle.
pts=[]
for j in range(N):x,z=section(j*math.tau/N,.1325,.1085,-.1565,3.2);pts.append((x,1.96,z))
curve('BDL_NOSE_PANEL_BOUNDARY',pts,.00045,seam,True)
def uv(n,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 src.objects.link(o);o.parent=root;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 o['evidence']='R12 visible small hardware; C count/metric arrangement';return o
for side in [-1,1]:
 for k,y in enumerate([-1.25,-.62,.05,.80,1.43]):
  uv('BDL_SIDE_FASTENER_'+str(side)+'_'+str(k),(side*.1507,y,.052),(.0024,.0036,.0036),metal)
 for k,x in enumerate([.08,.12]):uv('BDL_CROWN_FASTENER_'+str(side)+'_'+str(k),(side*x,.32,.17),(.003,.003,.002),metal)
 uv('BDL_WING_ROOT_ROUNDED_COVER_'+str(side),(side*.114,.93,-.16),(.07,.18,.013),grey)
# Small top loop visible in both supplied renders; exterior visual only.
uv('BDL_TOP_LOOP_BASE',(0,.18,.176),(.024,.032,.009),gold)
pts=[(-.021,.18,.179),(-.019,.18,.199),(-.014,.18,.211),(0,.18,.214),(.014,.18,.211),(.019,.18,.199),(.021,.18,.179)]
curve('BDL_TOP_LOOP',pts,.005,gold,False)
uv('BDL_REAR_UNDERSIDE_EXTERNAL_COVER',(0,-1.57,-.169),(.025,.055,.013),metal)
# No needle antenna inferred: thin front projection can be the existing tail fin edge.
for n in ['BDL_CAM_Front','BDL_CAM_Rear']:bpy.data.objects[n].data.ortho_scale=1.30
root['provisional_wing_span_m']=.946;root['body_height_estimated_m']=.33;root['stage']='G_SHAPE_CORRECTION';root['evidence']='R12 front / R13 side user render-based correction, C metric geometry';root['wing_span_status']='C .946m image ratio candidate; supersedes F 2.2m ambiguous Size interpretation'
s['revision']='G_v001';s['stage']='G_REFERENCE_LIMITED_EXTERIOR';s['status']='Review body/nose/wing proportions and visible detail; no authenticated stowed pose'
attach=bpy.data.objects['BANDEROL_ATTACH_ROOT'];attach.location.z=.17
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(cp),copy=True)
for rid,path in [('R12_Banderol_front','C:/Users/david/AppData/Local/Temp/codex-clipboard-7cb4e50e-f2eb-4fb7-a47d-0aee45b4c628.png'),('R13_Banderol_side','C:/Users/david/AppData/Local/Temp/codex-clipboard-6d111b77-1321-4fd8-a564-09abd2e93577.png')]:shutil.copy2(path,P/f'Support/references_private/{rid}.png')
(P/'Documentation/G_parameters_v001.json').write_text(json.dumps(dict(root.items()),indent=2))
print('G_SAVED',len(src.objects))
