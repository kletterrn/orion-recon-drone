from pathlib import Path
import bpy,bmesh,math,json,shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];check=P/'Orion/checkpoints/Orion_E_sensor_fix_v006.blend'
assert not check.exists()
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_E_exterior_rig_v005.blend'));s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1)
root=bpy.data.objects['ORION_ROOT'];root['sensor_yaw_degrees']=0.;root['sensor_pitch_degrees']=0.;root.update_tag();bpy.context.view_layer.update()
C=bpy.data.collections['ORION_SENSOR_R3'];cuts=bpy.data.collections['ORION_RETAINED_CAVITY_CUTTERS'];yaw=bpy.data.objects['ORION_SENSOR_YAW'];pitch=bpy.data.objects['ORION_SENSOR_PITCH']
for o in list(bpy.data.objects):
 if o.type in {'MESH','CURVE'} and (o.name.startswith('ORION_SENSOR_')):bpy.data.objects.remove(o,do_unlink=True)
yaw.location.z+=.12;bpy.context.view_layer.update()
grey=bpy.data.materials['ORION_GREY_REVIEW'];metal=bpy.data.materials['ORION_GEAR_SATIN_METAL'];dark=bpy.data.materials['ORION_SEALS_DARK']
glass=bpy.data.materials.get('ORION_OPTICAL_GLASS') or dark
blue=bpy.data.materials.new('ORION_SENSOR_BLUE_OPTIC_REVIEW');blue.use_nodes=True;bs=blue.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.012,.023,.075,1);bs.inputs['Roughness'].default_value=.16
red=bpy.data.materials.new('ORION_SENSOR_WARM_OPTIC_REVIEW');red.use_nodes=True;bs=red.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.05,.012,.008,1);bs.inputs['Roughness'].default_value=.19
def mesh(n,v,f,parent=pitch,mat=grey,collection=C):
 v=[(x,y,z+(.12 if n!='ORION_SENSOR_FIXED_CONFORMAL_SADDLE' or abs(z+.474)<1e-6 else 0)) for x,y,z in v]
 d=bpy.data.meshes.new(n+'_MESH');d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(n,d);collection.objects.link(o)
 if mat:d.materials.append(mat)
 o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
 for face in d.polygons:face.use_smooth=len(face.vertices)==4
 o['evidence']='A visible housing/connection/window arrangement R11 supplied photo; C exact depth, hidden completion';return o
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);ev.to_mesh_clear();return t
bt=tree(bpy.data.objects['ORION_FUSELAGE'])
N=96;v=[];f=[]
# Broad conformal attachment saddle: its upper edge penetrates the actual underside.
for layer in [0,1]:
 for j in range(N):
  a=2*math.pi*j/N;x=.205*math.cos(a);y=2.055+.255*math.sin(a);hit=bt.ray_cast(Vector((x,y,-2)),Vector((0,0,1)))[0];assert hit
  v.append((x,y,hit.z+.012 if layer else -.474))
for j in range(N):f.append((j,(j+1)%N,N+(j+1)%N,N+j))
f += [tuple(reversed(range(N))),tuple(N+j for j in range(N))]
mesh('ORION_SENSOR_FIXED_CONFORMAL_SADDLE',v,f,root)
def rod(n,a,b,r,parent=pitch,mat=grey,collection=C):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=axis.cross(Vector((1,0,0)))
 u.normalize();w=axis.cross(u);v=[tuple(p+r*(u*math.cos(j*2*math.pi/64)+w*math.sin(j*2*math.pi/64))) for p in [a,b] for j in range(64)]
 f=[(j,(j+1)%64,64+(j+1)%64,64+j) for j in range(64)]+[tuple(reversed(range(64))),tuple(64+j for j in range(64))];return mesh(n,v,f,parent,mat,collection)
rod('ORION_SENSOR_YAW_COLLAR',(0,2.055,-.468),(0,2.055,-.488),.18,yaw)
# Purpose-built vertical stations: broad cheeks, narrower crown, curved lower belly.
v=[];f=[];sections=[(-1.083,.035,.045),(-1.06,.105,.125),(-1.00,.183,.209),(-.90,.244,.270),(-.77,.268,.292),(-.64,.251,.266),(-.54,.201,.208),(-.513,.167,.174)]
for z,rx,ry in sections:
 for j in range(N):
  a=j*2*math.pi/N;x=rx*math.cos(a);dy=ry*math.sin(a)
  v.append((x,2.055+dy,z))
for k in range(len(sections)-1):
 for j in range(N):f.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
f += [tuple(reversed(range(N))),tuple((len(sections)-1)*N+j for j in range(N))]
h=mesh('ORION_SENSOR_PITCH_HOUSING',v,f);sub=h.modifiers.new('Controlled_curved_casing','SUBSURF');sub.levels=2;sub.render_levels=2;bpy.context.view_layer.update();ht=tree(h)
# Ports follow the real curved casing normals, not a flat circular face.
windows=[('MAIN',-.065,-.828,.083,dark),('UPPER_BLUE',.075,-.730,.040,blue),('RIGHT_MID',.138,-.834,.032,dark),('LOWER_L',-.128,-.951,.030,dark),('LOWER_MID',-.038,-1.012,.033,dark),('LOWER_R',.083,-.977,.035,red),('LEFT_SMALL',-.162,-.754,.023,dark)]
for name,x,z,r,mat in windows:
 z+=.12
 hit,n,_,_=ht.ray_cast(Vector((x,3,z)),Vector((0,-1,0)));assert hit is not None;n.normalize();u=n.cross(Vector((0,0,1)));u.normalize();w=n.cross(u)
 hit-=Vector((0,0,.12))
 cutter=rod('ORION_SENSOR_'+name+'_RECESS_CUTTER',hit-n*.10,hit+n*.10,r,pitch,None,cuts);bo=h.modifiers.new(name+'_WINDOW_RECESS','BOOLEAN');bo.operation='DIFFERENCE';bo.solver='EXACT';bo.object=cutter
 # Annulus slightly overlaps the casing; recessed glass is behind the casing surface.
 vv=[];ff=[]
 for d,rr in [(-.015,r+.004),(.003,r+.004),(.003,r-.001),(-.015,r-.001)]:
  vv += [tuple(hit+n*d+(u*math.cos(j*2*math.pi/64)+w*math.sin(j*2*math.pi/64))*rr) for j in range(64)]
 for k in range(4):
  for j in range(64):ff.append((k*64+j,k*64+(j+1)%64,((k+1)%4)*64+(j+1)%64,((k+1)%4)*64+j))
 mesh('ORION_SENSOR_'+name+'_WINDOW_RIM',vv,ff,mat=grey)
 rod('ORION_SENSOR_'+name+'_OPTICAL_SURFACE',hit-n*.030,hit-n*.022,r-.002,mat=mat)
 rod('ORION_SENSOR_'+name+'_DARK_BACKING',hit-n*.044,hit-n*.037,r-.002,mat=dark)
bridge_v=[(x,y,z) for x in [-.282,.282] for y in [1.89,2.22] for z in [-.488,-.471]]
mesh('ORION_SENSOR_YOKE_TOP_BRIDGE',bridge_v,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],yaw)
# Yoke cheeks are closed plates with a broad curved base; no floating rectangular bars.
for side in [-1,1]:
 outline=[(1.855,-.486),(2.255,-.486)]+[(2.055+.20*math.cos(j*math.pi/32),-.80-.23*math.sin(j*math.pi/32)) for j in range(33)]
 vv=[(side*x,y,z) for x in [.275,.294] for y,z in outline];m=len(outline);ff=[tuple(reversed(range(m))),tuple(m+j for j in range(m))]+[(j,(j+1)%m,m+(j+1)%m,m+j) for j in range(m)]
 o=mesh('ORION_SENSOR_YOKE_'+str(side),vv,ff,yaw);be=o.modifiers.new('Soft_cheek_edges','BEVEL');be.width=.002;be.segments=2;be.limit_method="ANGLE";be.angle_limit=.5
 rod('ORION_SENSOR_PITCH_PIVOT_CAP_'+str(side),(side*.267,2.055,-.80),(side*.303,2.055,-.80),.073,yaw)
 # Visible side seam follows casing, recessed behind stationary yoke.
 pts=[]
 for j in range(97):
  a=2*math.pi*j/96;y=2.055+.168*math.cos(a);z=-.795+.12+.208*math.sin(a);hit,n,_,_=ht.ray_cast(Vector((side*2,y,z)),Vector((-side,0,0)))
  if hit:pts.append(tuple(hit+n*.001))
 d=bpy.data.curves.new('ORION_SENSOR_SIDE_SEAM','CURVE');d.dimensions='3D';d.bevel_depth=.0009;d.bevel_resolution=3;sp=d.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new('ORION_SENSOR_SIDE_SEAM_'+str(side),d);C.objects.link(o);o.parent=pitch;o.matrix_parent_inverse=pitch.matrix_world.inverted();d.materials.append(dark)
for o in C.objects:
 o['planned_export_bone']='BONE_SENSOR_PITCH' if o.parent==pitch else 'BONE_SENSOR_YAW' if o.parent==yaw else 'ORION_BONE_ROOT'
arm=bpy.data.objects['ORION_EXPORT_ARMATURE'];bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n in ['BONE_SENSOR_YAW','BONE_SENSOR_PITCH']:
 arm.data.edit_bones[n].head.z+=.12;arm.data.edit_bones[n].tail.z+=.12
bpy.ops.object.mode_set(mode='OBJECT')
s['revision']='E_sensor_v006';s['stage']='SENSOR_CORRECTION_REVIEW';bpy.context.preferences.filepaths.save_version=0
ref=P/'Support/references_private/R11_sensor_mount.png';shutil.copy2('C:/Users/david/AppData/Local/Temp/codex-clipboard-31fef8df-c60e-44f8-b67f-5ce133c7785b.png',ref)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(check),copy=True)
print('SENSOR_CORRECTION_SAVED')
