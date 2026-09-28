from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];REV=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v002';CHECK=P/f'Orion/checkpoints/Orion_E_exterior_rig_{REV}.blend'
if CHECK.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_D_wing_root_fix_v012.blend'))
bpy.context.preferences.filepaths.save_version=0
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1)
root=bpy.data.objects['ORION_ROOT'];source=bpy.data.collections['10_SOURCE'];helpers=bpy.data.collections['30_RIG_HELPERS']
def coll(n,p):c=bpy.data.collections.new(n);p.children.link(c);return c
detail=coll('ORION_EXTERIOR_DETAILS_R3',source);rig=coll('ORION_PRESENTATION_CONTROLS',helpers);cut=coll('ORION_E_RETAINED_CUTTERS',helpers);cut.hide_render=True;cut.hide_viewport=True
def mat(n,c,r=.5,m=0):
 a=bpy.data.materials.new(n);a.use_nodes=True;node=a.node_tree.nodes['Principled BSDF'];node.inputs['Base Color'].default_value=(*c,1);node.inputs['Roughness'].default_value=r;node.inputs['Metallic'].default_value=m;return a
grey=bpy.data.materials['ORION_GREY_REVIEW'];white=bpy.data.materials['ORION_WHITE_NOSE_REVIEW'];dark=bpy.data.materials['ORION_SEALS_DARK'];metal=bpy.data.materials['ORION_GEAR_SATIN_METAL']
red=mat('ORION_RED_LENS',(.28,.006,.004),.2);green=mat('ORION_GREEN_LENS',(.006,.18,.035),.2);yellow=mat('ORION_PROPELLER_TIP_PAINT',(.78,.60,.025),.55)
def mesh(n,v,f,c=detail,m=grey):
 d=bpy.data.meshes.new(n+'_MESH');d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(n,d);c.objects.link(o);o.parent=root
 if m:d.materials.append(m)
 o['stage']='E';o['evidence']='A R3/R7 visible placement; C local dimensions and hidden completion';return o
def parent_keep(o,p):
 bpy.context.view_layer.update();world=o.parent.matrix_world@o.matrix_parent_inverse@o.matrix_basis if o.parent else o.matrix_basis.copy();o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted();o.matrix_world=world
def bevel(o,w=.002):
 b=o.modifiers.new('Small_edge_radius','BEVEL');b.width=w;b.segments=3;return o
def ellipsoid(n,loc,scale,m=grey):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=loc);o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 detail.objects.link(o);o.name=n;o.parent=root;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 o['evidence']='A/B visible fairing; C dimensions';return o
def curve(n,points,r,m=dark):
 d=bpy.data.curves.new(n+'_CURVE','CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=3;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*v,1)
 o=bpy.data.objects.new(n,d);detail.objects.link(o);o.parent=root;d.materials.append(m);o['stage']='E';return o
def rod(n,a,b,r,m=metal):
 a,b=Vector(a),Vector(b);axis=b-a;q=axis.to_track_quat('Z','Y');v=[tuple(p+q@Vector((r*math.cos(j*2*math.pi/32),r*math.sin(j*2*math.pi/32),0))) for p in [a,b] for j in range(32)]
 f=[(j,(j+1)%32,32+(j+1)%32,32+j) for j in range(32)]+[tuple(reversed(range(32))),tuple(32+j for j in range(32))];o=mesh(n,v,f,m=m)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return bevel(o,.0007)
body=bpy.data.objects['ORION_FUSELAGE'];ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();bt=BVHTree.FromPolygons([ev.matrix_world@v.co for v in em.vertices],[tuple(p.vertices) for p in em.polygons]);ev.to_mesh_clear()
def sidepoint(y,z):
 hit=bt.ray_cast(Vector((-2,y,z)),Vector((1,0,0)))
 if hit[0] is None:raise RuntimeError('Panel projection failed')
 return hit[0],hit[1]
def crown(y):return bt.ray_cast(Vector((0,y,2)),Vector((0,0,-1)))[0].z
# Rounded dorsal dome with its lower half buried inside the approved shell.
ellipsoid('ORION_DORSAL_WHITE_DOME',(0,.52,crown(.52)+.045),(.178,.208,.193),white)
ellipsoid('ORION_DORSAL_DOME_BASE_SEAL',(0,.52,crown(.52)+.004),(.19,.22,.009),dark)
ellipsoid('ORION_DORSAL_DOME_BASE_FLANGE',(0,.52,crown(.52)+.009),(.198,.23,.009),white)
# Conformal mounting skirt prevents a flat circular flange floating over the curved skin.
sv=[];sf=[];N=64
for layer in [0,1]:
 for j in range(N):
  a=2*math.pi*j/N;x=.194*math.cos(a);y=.52+.224*math.sin(a)
  hit=bt.ray_cast(Vector((x,y,2)),Vector((0,0,-1)))[0]
  sv.append((x,y,crown(.52)+.011 if layer else hit.z-.003))
for j in range(N):sf.append((j,(j+1)%N,N+(j+1)%N,N+j))
sf += [tuple(reversed(range(N))),tuple(N+j for j in range(N))]
skirt=mesh('ORION_DORSAL_DOME_CONFORMAL_BASE',sv,sf,m=white)
for f in skirt.data.polygons:f.use_smooth=len(f.vertices)==4
ellipsoid('ORION_FORWARD_LOW_DORSAL_COVER',(0,1.71,crown(1.71)-.001),(.10,.225,.045),dark)
z=crown(2.67);verts=[(x,y,zz) for x in [-.009,.009] for y,zz in [(2.59,z-.006),(2.79,z-.006),(2.70,z+.125),(2.63,z+.125)]]
bevel(mesh('ORION_FORWARD_RED_DORSAL_BLADE',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m=red),.003)
rod('ORION_AFT_SHORT_DORSAL_AERIAL',(0,-2.45,crown(-2.45)-.004),(0,-2.45,crown(-2.45)+.082),.006,dark)
# Left forward service panel: contour projected onto the actual fuselage.
points=[]
for cy,cz,start in [(2.77,.195,0),(2.77,-.15,90),(.86,-.15,180),(.86,.195,270)]:
 for j in range(13):
  a=math.radians(start+j*90/12);y=cy+.09*math.sin(a);z=cz+.06*math.cos(a);p,n=sidepoint(y,z);points.append(tuple(p+n*.0008))
points.append(points[0]);dense=[]
for a,b in zip(points[:-1],points[1:]):
 a,b=Vector(a),Vector(b);count=max(1,math.ceil((b-a).length/.025))
 for k in range(count):
  q=a.lerp(b,k/count);p,n=sidepoint(q.y,q.z);dense.append(tuple(p+n*.001))
dense.append(dense[0]);points=dense;curve('ORION_LEFT_FORWARD_PANEL_SEAL',points,.0009)
for j,i in enumerate([round((len(points)-1)*t/8) for t in range(8)]):
 p=Vector(points[i]);_,normal=sidepoint(p.y,p.z);rod('ORION_LEFT_PANEL_VISIBLE_FASTENER_'+str(j),p-normal*.0006,p+normal*.0018,.003)
# Small triangular side opening with a shallow closed backing.
outer=[];inner=[]
for y,z in [(.80,.153),(.96,.18),(.91,.235)]:
 p,n=sidepoint(y,z);outer.append(tuple(p+n*.012));inner.append(tuple(p-n*.028))
vc=mesh('ORION_LEFT_TRIANGULAR_VENT_CUTTER',outer+inner,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],cut,None)
mod=body.modifiers.new('Visible_left_triangular_vent','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=vc
back=[tuple(Vector(p)+Vector((-.003,0,0))) for p in inner];mesh('ORION_LEFT_VENT_SHALLOW_BACKING',back+inner,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],m=dark)
curve('ORION_LEFT_VENT_RIM',[tuple(Vector(p)+Vector((.010,0,0))) for p in outer]+[tuple(Vector(outer[0])+Vector((.010,0,0)))],.0013,grey)
# Rear dorsal scoop: exterior shell with a shallow closed recess, no engine internals.
v=[];f=[];N=32
for y,w,zt,zb in [(-3.35,.042,crown(-3.35)+.006,crown(-3.35)-.025),(-3.22,.105,crown(-3.22)+.093,crown(-3.22)-.025),(-2.97,.12,crown(-2.97)+.115,crown(-2.97)-.018)]:
 for j in range(N):
  a=2*math.pi*j/N;v.append((w*math.cos(a),y,zb+(zt-zb)*(.5+.5*math.sin(a))))
for k in range(2):
 for j in range(N):f.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
f.extend([tuple(reversed(range(N))),tuple(2*N+j for j in range(N))]);scoop=mesh('ORION_REAR_DORSAL_INTAKE_SHELL',v,f)
for poly in scoop.data.polygons:poly.use_smooth=len(poly.vertices)==4
opening_z=crown(-2.97)+.045
# Cut from front and leave a visible closed dark lining in the scoop.
def cube(n,loc,size,c,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object
 for oc in list(o.users_collection):oc.objects.unlink(o)
 c.objects.link(o);o.name=n;o.parent=root;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if m:o.data.materials.append(m)
 return bevel(o,.007)
rc=cube('ORION_REAR_INTAKE_RECESS_CUTTER',(0,-2.967,opening_z),(.176,.105,.085),cut,None)
mod=scoop.modifiers.new('Shallow_visible_rear_intake','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=rc
cube('ORION_REAR_INTAKE_BACKING',(0,-3.021,opening_z),(.169,.008,.080),detail,dark)
# Two forward underside apertures distinct from the turret.
ff=ellipsoid('ORION_FORWARD_UNDERSIDE_APERTURE_FAIRING',(0,2.99,-.344),(.145,.20,.075))
for sign in [-1,1]:
 aperture_cut=rod('ORION_FORWARD_APERTURE_CUTTER_'+str(sign),(sign*.054,3.07,-.383),(sign*.054,3.18,-.383),.023,None)
 detail.objects.unlink(aperture_cut);cut.objects.link(aperture_cut)
 m=ff.modifiers.new('Real_forward_aperture_'+str(sign),'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=aperture_cut
 rod('ORION_FORWARD_UNDERSIDE_APERTURE_'+str(sign),(sign*.054,3.095,-.383),(sign*.054,3.099,-.383),.0215,dark)
for side,label,m in [(-1,'L',red),(1,'R',green)]:
 ellipsoid('ORION_WING_TIP_LIGHT_HOUSING_'+label,(side*7.94,-.685,.252),(.049,.080,.018),grey)
 ellipsoid('ORION_WING_TIP_LIGHT_LENS_'+label,(side*7.966,-.663,.260),(.022,.045,.012),m)
 rod('ORION_WING_TIP_SMALL_PROJECTION_'+label,(side*7.989,-.74,.25),(side*7.989,-.835,.25),.0028,dark)
for label in ['A','B']:
 blade=bpy.data.objects['ORION_PROPELLER_BLADE_'+label];blade.data.materials.append(yellow)
 for face in blade.data.polygons:
  if abs(face.center.z)>.84:face.material_index=len(blade.data.materials)-1

# User-facing presentation properties, driving correctly located rigid pivots.
mapping={}
def property(n,minv,maxv):
 root[n]=0.;root.id_properties_ui(n).update(min=minv,max=maxv,soft_min=minv,soft_max=maxv,description='Visual presentation degrees; no flight or real mechanism specification')
def control(n,loc,axis,prop,limit,parent=root):
 o=bpy.data.objects.new(n,None);rig.objects.link(o);o.parent=root;o.location=loc;o.empty_display_type='ARROWS';o.empty_display_size=.12;o.rotation_mode='AXIS_ANGLE';parent_keep(o,parent);o.rotation_axis_angle=(0,*Vector(axis).normalized())
 property(prop,-limit,limit);dr=o.driver_add('rotation_axis_angle',0).driver;dr.expression='radians(v)';var=dr.variables.new();var.name='v';var.targets[0].id=root;var.targets[0].data_path='["'+prop+'"]';mapping[n]={'property':prop,'axis':list(axis),'limit_degrees':limit};return o
prop=control('ORION_CTRL_PROPELLER',(0,-3.81,.045),(0,1,0),'propeller_degrees',3600)
for n in ['ORION_PROPELLER_BLADE_A','ORION_PROPELLER_BLADE_B','ORION_PROPELLER_HUB','ORION_PUSHER_SPINNER']:parent_keep(bpy.data.objects[n],prop)
def hinge(span,u,side):
 t=(span-.28)/7.72;c=1.33-.70*t;return Vector((side*span,-.52-.13*t-c*u,.235+.02*t+c*.018*math.sin(math.pi*u)))
for side,label in [(-1,'L'),(1,'R')]:
 for comp,a,b in [('FLAP',.65,4.20),('AILERON',4.23,7.86)]:
  h=hinge(a,.757,side);axis=hinge(b,.757,side)-h;ctrl=control('ORION_CTRL_'+comp+'_'+label,h,axis,comp.lower()+'_'+label.lower()+'_degrees',8);parent_keep(bpy.data.objects['ORION_'+comp+'_'+label],ctrl)
 h=Vector((side*.22,-2.69-.90*.743,.245));axis=Vector((side*1.38,-.56+.34*.743,1.36));ctrl=control('ORION_CTRL_RUDDERVATOR_'+label,h,axis,'ruddervator_'+label.lower()+'_degrees',8);parent_keep(bpy.data.objects['ORION_RUDDERVATOR_'+label],ctrl)
for label in ['NOSE','MAIN_L','MAIN_R']:
 axle=bpy.data.objects['ORION_'+label+'_WHEEL_AXLE'];children=list(axle.children);bpy.context.view_layer.update();spin=control('ORION_CTRL_'+label+'_WHEEL_SPIN',axle.matrix_world.translation,(1,0,0),'wheel_'+label.lower()+'_degrees',3600,axle)
 for child in children:parent_keep(child,spin)
for name,axis,propname,limit in [('ORION_SENSOR_YAW',(0,0,1),'sensor_yaw_degrees',35),('ORION_SENSOR_PITCH',(1,0,0),'sensor_pitch_degrees',15)]:
 o=bpy.data.objects[name];o.rotation_mode='AXIS_ANGLE';o.rotation_axis_angle=(0,*axis);property(propname,-limit,limit);dr=o.driver_add('rotation_axis_angle',0).driver;dr.expression='radians(v)';var=dr.variables.new();var.name='v';var.targets[0].id=root;var.targets[0].data_path='["'+propname+'"]';mapping[name]={'property':propname,'axis':axis,'limit_degrees':limit}
root['gear_pose_help']='Timeline: 1 down, 65 rear swing, 100 inside/open, 120 illustrative retracted, 160 inspection'
# A separate export skeleton follows presentation pivots. Source geometry stays editable;
# rigid weights and baked engine clips are deliberately deferred to the game-copy milestone.
armdata=bpy.data.armatures.new('ORION_EXPORT_ARMATURE_DATA');arm=bpy.data.objects.new('ORION_EXPORT_ARMATURE',armdata);rig.objects.link(arm);arm.parent=root;arm.show_in_front=True;arm.hide_render=True
bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
br=armdata.edit_bones.new('ORION_BONE_ROOT');br.head=(0,0,0);br.tail=(0,.3,0)
targets={o.name:o for o in rig.objects if o.type=='EMPTY'}
targets.update({o.name:o for o in bpy.data.collections['ORION_D_PRESENTATION_CONTROLS'].objects if o.animation_data or o.name in ['ORION_SENSOR_YAW','ORION_SENSOR_PITCH']})
for n,o in targets.items():
 b=armdata.edit_bones.new('BONE_'+n.removeprefix('ORION_'));b.head=o.matrix_world.translation;b.tail=b.head+Vector((0,.12,0));b.parent=br;b.use_connect=False
for n,o in targets.items():
 ancestor=o.parent
 while ancestor and ancestor.name not in targets:ancestor=ancestor.parent
 if ancestor:armdata.edit_bones['BONE_'+n.removeprefix('ORION_')].parent=armdata.edit_bones['BONE_'+ancestor.name.removeprefix('ORION_')]
bpy.ops.object.mode_set(mode='OBJECT')
for n,o in targets.items():
 b=arm.pose.bones['BONE_'+n.removeprefix('ORION_')];c=b.constraints.new('COPY_TRANSFORMS');c.target=o;c.owner_space='WORLD';c.target_space='WORLD'
arm['status']='Blender preview/export hierarchy source; rigid game weights, FBX basis and engine animation remain unvalidated'
for o in source.all_objects:
 anc=o.parent
 while anc and anc.name not in targets:anc=anc.parent
 o['planned_export_bone']='BONE_'+anc.name.removeprefix('ORION_') if anc else 'ORION_BONE_ROOT'
s['revision']='E_'+REV;s['stage']='E_EXTERIOR_AND_PRESENTATION_RIG_REVIEW';s.camera=bpy.data.objects['ORION_CAM_HERO'];s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(CHECK),copy=True)
(P/f'Documentation/E_controls_{REV}.json').write_text(json.dumps({'properties':mapping,'export_bones':len(armdata.bones),'game_weights':'Deferred to game copies; source hierarchy remains rigid object parented','gear_motion':'Illustrative prior D action retained'},indent=2))
print('E_SAVED',len(detail.objects),'exterior objects',len(armdata.bones),'bones')
