"""Executed Stage D construction. Preserve the approved C v007 exterior."""
from pathlib import Path
import bpy, bmesh, math, json, sys
from mathutils import Vector, Quaternion
P=Path(__file__).resolve().parents[1]
REV=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v002'
CHECK=P/f'Orion/checkpoints/Orion_D_gear_bays_sensor_{REV}.blend'
if CHECK.exists(): raise RuntimeError('Checkpoint exists: use a new revision')
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_C_primary_geometry_v007.blend'))
bpy.context.preferences.filepaths.save_version=0
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW']; bpy.context.window.scene=s
source=bpy.data.collections['10_SOURCE']; helpers=bpy.data.collections['30_RIG_HELPERS']; root=bpy.data.objects['ORION_ROOT']
for o in list(bpy.data.collections['ORION_LAYOUT_ENVELOPES_NOT_FINAL'].objects): bpy.data.objects.remove(o,do_unlink=True)
def collection(n,parent):
 c=bpy.data.collections.new(n);parent.children.link(c);return c
gear=collection('ORION_GEAR',source); bays=collection('ORION_GEAR_BAYS',source); sensor=collection('ORION_SENSOR_R3',source)
cutters=collection('ORION_RETAINED_CAVITY_CUTTERS',helpers); cutters.hide_render=True;cutters.hide_viewport=True
controls=collection('ORION_D_PRESENTATION_CONTROLS',helpers)
def material(n,color,rough=.5,metal=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;node=m.node_tree.nodes['Principled BSDF']
 node.inputs['Base Color'].default_value=(*color,1);node.inputs['Roughness'].default_value=rough;node.inputs['Metallic'].default_value=metal;return m
grey=bpy.data.materials['ORION_GREY_REVIEW']; metal=material('ORION_GEAR_SATIN_METAL',(.49,.52,.55),.32,.75)
chrome=material('ORION_EXPOSED_SLIDING_METAL',(.65,.69,.72),.2,.85);rubber=material('ORION_TIRE_RUBBER',(.015,.019,.022),.79)
black=material('ORION_SEALS_DARK',(.027,.035,.04),.66);inside=material('ORION_BAY_INTERIOR_APPROXIMATION',(.21,.235,.245),.74)
lens=material('ORION_OPTICAL_SURFACE',(.016,.031,.042),.13,.25);blue=material('ORION_OPTICAL_BLUE_SURFACE',(.022,.058,.12),.15,.3)
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
def finish(o,n,c,mat,parent=root):
 o.name=n;move(o,c);o.parent=parent
 if mat:o.data.materials.clear();o.data.materials.append(mat)
 o['stage']='D';o['evidence']='C hidden detail / A-B visible component silhouette';return o
def bevel(o,w=.002):
 m=o.modifiers.new('Controlled_edge_radius','BEVEL');m.width=w;m.segments=3
 m=o.modifiers.new('Weighted_corner_normals','WEIGHTED_NORMAL');m.keep_sharp=True
 return o
def box(n,center,size,c,mat,bev=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=finish(bpy.context.object,n,c,mat)
 o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:bevel(o,bev)
 return o
def rod(n,a,b,r,c=gear,mat=metal,vertices=32):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(b-a).length,location=(a+b)/2)
 o=finish(bpy.context.object,n,c,mat);o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 bevel(o,min(.0015,r/6));return o
def tube(n,points,r,c=gear,mat=black):
 d=bpy.data.curves.new(n+'_CURVE','CURVE');d.dimensions='3D';d.resolution_u=12;d.bevel_depth=r;d.bevel_resolution=3
 sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for v,p in zip(sp.points,points):v.co=(*p,1)
 o=bpy.data.objects.new(n,d);c.objects.link(o);o.parent=root;d.materials.append(mat);o['stage']='D';return o
def empty(n,loc):
 o=bpy.data.objects.new(n,None);controls.objects.link(o);o.parent=root;o.location=loc;o.empty_display_size=.12;o.empty_display_type='ARROWS';o.rotation_mode='QUATERNION';return o
def parent_keep(o,p):
 bpy.context.view_layer.update()
 # Hidden cutter collections are absent from the view dependency graph: compute
 # the rest matrix from editable transforms rather than reading a stale world matrix.
 world=o.parent.matrix_world@o.matrix_parent_inverse@o.matrix_basis if o.parent else o.matrix_basis.copy()
 o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted();o.matrix_world=world
def mesh(n,verts,faces,c,mat):
 d=bpy.data.meshes.new(n+'_MESH');d.from_pydata(verts,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(n,d);c.objects.link(o);o.parent=root;d.materials.append(mat);o['stage']='D';return o
body=bpy.data.objects['ORION_FUSELAGE']
stations=json.loads(body['stations_json'])
def interp(y,idx):
 # Same monotonic Hermite rule used by the approved shell.
 xs=[p[0] for p in stations];ys=[p[idx] for p in stations];ds=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i]) for i in range(len(xs)-1)];ts=[ds[0]]
 for i in range(1,len(xs)-1):
  h0=xs[i]-xs[i-1];h1=xs[i+1]-xs[i];a=2*h1+h0;b=h1+2*h0;ts.append(0 if ds[i-1]*ds[i]<=0 else (a+b)/(a/ds[i-1]+b/ds[i]))
 ts.append(ds[-1]);i=next((i for i in range(len(xs)-1) if y<=xs[i+1]),len(xs)-2);h=xs[i+1]-xs[i];t=(y-xs[i])/h
 return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*ts[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*ts[i+1]
def skin_z(x,y):
 w=interp(y,1);bt=interp(y,3);top=interp(y,2);u=min(.999,abs(x)/w)**(1/.45);v=-math.sqrt(1-u*u);return bt+(top-bt)*.17*(1+v)
bay_specs=[('NOSE',0,.76,.32,1.50,.205),('MAIN_L',-.115,-1.46,.21,1.88,.205),('MAIN_R',.115,-1.46,.21,1.88,.205)]
door_controls=[]
for label,x,y,w,l,roof in bay_specs:
 cavity=box('ORION_'+label+'_BAY_CUTTER',(x,y,(roof-1)/2),(w,l,roof+1),cutters,None,.009)
 # Boolean after subdivision leaves the accepted exterior unchanged outside the openings.
 bo=body.modifiers.new(label+'_ACTUAL_BAY_OPENING','BOOLEAN');bo.operation='DIFFERENCE';bo.solver='EXACT';bo.object=cavity
 for sign in [-1,1]:
  box('ORION_'+label+'_BAY_SIDE_'+str(sign),(x+sign*(w/2+.003),y,(roof-.35)/2),(.006,l+.012,roof+.35),bays,inside)
  box('ORION_'+label+'_BAY_END_'+str(sign),(x,y+sign*(l/2+.003),(roof-.35)/2),(w,.006,roof+.35),bays,inside)
 box('ORION_'+label+'_BAY_ROOF',(x,y,roof+.003),(w+.012,l+.012,.006),bays,inside)
 for j in [0,1]:
  yy=y+(j-.5)*l*.58
  box('ORION_'+label+'_BAY_ROOF_SUPPORT_'+str(j),(x,yy,roof-.003),(w-.014,.022,.006),bays,metal,.001)
 # Continuous narrow skin lip follows the real lower cross-section.
 for side in [-1,1]:
  xx=x+side*w/2;points=[(xx,y-l/2+l*k/30,skin_z(xx,y-l/2+l*k/30)-.002) for k in range(31)]
  tube('ORION_'+label+'_OPENING_LIP_'+str(side),points,.003,bays,grey)
 if label=='NOSE': halves=[(-1,x-w/2,x),(1,x+w/2,x)]
 else:
  side=-1 if label.endswith('L') else 1;sign=-side;halves=[(sign,x-side*w/2,x+side*w/2)]
 for sign,outer,inner in halves:
  pivot=empty('ORION_'+label+'_DOOR_HINGE_'+str(sign),(outer,y,skin_z(outer,y)));verts=[];ny=22;nx=4
  for layer in [0,1]:
   for j in range(ny+1):
    yy=y-l/2+.006+(l-.012)*j/ny
    for k in range(nx+1):
     xx=outer+(inner-outer)*k/nx;xx+=.003*sign*(2*k/nx-1)
     verts.append((xx,yy,skin_z(xx,yy)-.004+layer*.005))
  nr=(ny+1)*(nx+1);faces=[]
  for layer in [0,1]:
   for j in range(ny):
    for k in range(nx):
     a=layer*nr+j*(nx+1)+k;faces.append((a,a+1,a+nx+2,a+nx+1))
  boundary=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+k for k in reversed(range(nx))]+[j*(nx+1) for j in reversed(range(1,ny))]
  for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+nr,a+nr))
  d=mesh('ORION_'+label+'_DOOR_SHELL_'+str(sign),verts,faces,bays,grey);bevel(d,.001);parent_keep(d,pivot)
  for j in [-1,1]:
   yy=y+j*l*.32;h=rod('ORION_'+label+'_DOOR_HINGE_BARREL_'+str(sign)+'_'+str(j),(outer,yy-.034,skin_z(outer,yy)),(outer,yy+.034,skin_z(outer,yy)),.012,bays,metal)
   parent_keep(h,pivot)
  pivot['evidence']='C illustrative hinge and door layout';door_controls.append((pivot,sign))
gear_controls=[]
def wheel(label,center,r,width,parent):
 c=Vector(center);joint=empty('ORION_'+label+'_WHEEL_AXLE',center);parent_keep(joint,parent)
 # Revolved tire section around X, with molded shoulder and seven shallow grooves.
 section=[(-width*.5,r*.80),(-width*.47,r*.94),(-width*.34,r*.993)]
 for j in range(23):
  x=-width*.32+width*.64*j/22;rr=r*(.997 if j%3 else .984);section.append((x,rr))
 section.extend([(width*.34,r*.993),(width*.47,r*.94),(width*.5,r*.80),(width*.42,r*.60),(-width*.42,r*.60)])
 n=80;vs=[tuple(c+Vector((x,rr*math.cos(2*math.pi*j/n),rr*math.sin(2*math.pi*j/n)))) for x,rr in section for j in range(n)]
 fs=[(k*n+j,k*n+(j+1)%n,((k+1)%len(section))*n+(j+1)%n,((k+1)%len(section))*n+j) for k in range(len(section)) for j in range(n)]
 tire=mesh('ORION_'+label+'_TIRE',vs,fs,gear,rubber)
 for p in tire.data.polygons:p.use_smooth=True
 parent_keep(tire,joint)
 hub=rod('ORION_'+label+'_RIM',c-Vector((width*.46,0,0)),c+Vector((width*.46,0,0)),r*.60,gear,metal,64);parent_keep(hub,joint)
 for side in [-1,1]:
  face=c+Vector((side*(width*.46+.001),0,0))
  disc=rod('ORION_'+label+'_HUB_RECESS_'+str(side),face,face+Vector((side*.003,0,0)),r*.42,gear,black,64);parent_keep(disc,joint)
  cap=rod('ORION_'+label+'_AXLE_CAP_'+str(side),face,face+Vector((side*.012,0,0)),r*.17,gear,metal);parent_keep(cap,joint)
  for j in range(6):
   a=2*math.pi*j/6;pt=face+Vector((side*.002,r*.30*math.cos(a),r*.30*math.sin(a)))
   bolt=rod('ORION_'+label+'_HUB_BOLT_'+str(side)+'_'+str(j),pt,pt+Vector((side*.003,0,0)),.0045,gear,metal,6);parent_keep(bolt,joint)
 return joint
for label,pivot,center,r,w in [('NOSE',(0,1.35,-.27),(0,1.45,-1.35),.20,.13),('MAIN_L',(-.08,-.65,-.28),(-1.02,-1.05,-1.305),.245,.16),('MAIN_R',(.08,-.65,-.28),(1.02,-1.05,-1.305),.245,.16)]:
 p=Vector(pivot);c=Vector(center);ctrl=empty('ORION_'+label+'_GEAR_PIVOT',p);ctrl['pose_motion']='C illustrative reconstructed motion; not authentic retraction engineering'
 direction=(c-p).normalized();end=c-direction*.14
 items=[]
 items.append(rod('ORION_'+label+'_UPPER_STRUT',p,p+(end-p)*.71,.026 if label=='NOSE' else .024))
 items.append(rod('ORION_'+label+'_SLIDING_SECTION',p+(end-p)*.58,end,.018 if label=='NOSE' else .019,gear,chrome))
 for t in [.18,.58,.70]:
  mid=p+(end-p)*t;items.append(rod('ORION_'+label+'_STRUT_COLLAR_'+str(t),mid-direction*.018,mid+direction*.018,.031))
 axle=rod('ORION_'+label+'_AXLE',c-Vector((w*.68,0,0)),c+Vector((w*.68,0,0)),.016);items.append(axle)
 for sign in [-1,1]:
  xx=sign*(w/2+.02)
  items.append(rod('ORION_'+label+'_FORK_'+str(sign),end+Vector((xx,0,0)),c+Vector((xx,0,0)),.012))
  items.append(rod('ORION_'+label+'_FORK_BRIDGE_'+str(sign),end,end+Vector((xx,0,0)),.013))
  bp=p+(end-p)*.16;mid=p+(end-p)*.58+Vector((0,-.067 if label=='NOSE' else -.037,0));low=p+(end-p)*.86
  items.append(rod('ORION_'+label+'_VISIBLE_LINK_UP_'+str(sign),bp+Vector((sign*.037,0,0)),mid+Vector((sign*.037,0,0)),.007))
  items.append(rod('ORION_'+label+'_VISIBLE_LINK_LOW_'+str(sign),mid+Vector((sign*.037,0,0)),low+Vector((sign*.037,0,0)),.007))
  for point,j in [(bp,0),(mid,1),(low,2)]:
   items.append(rod('ORION_'+label+'_LINK_PIN_'+str(sign)+'_'+str(j),point+Vector((sign*.031,0,0)),point+Vector((sign*.045,0,0)),.012,gear,metal,24))
 if label=='NOSE':
  # External coil visible in P4. Exact section dimensions remain approximate.
  a=p+(end-p)*.49;b=p+(end-p)*.79;axis=(b-a).normalized();u=Vector((1,0,0));v=axis.cross(u).normalized()
  pts=[tuple(a+(b-a)*k/240+.035*(u*math.cos(2*math.pi*9*k/240)+v*math.sin(2*math.pi*9*k/240))) for k in range(241)]
  items.append(tube('ORION_NOSE_VISIBLE_COIL',pts,.0045,gear,metal))
  pts=[tuple(p+(end-p)*t+Vector((-.047,-.022-.016*math.sin(t*math.pi),0))) for t in [0,.15,.4,.7,.85]]
  items.append(tube('ORION_NOSE_VISIBLE_FLEX_LINE',pts,.0035))
 for item in items:parent_keep(item,ctrl)
 # Local upper attachment cross-pin stays in the bay rather than traveling with the leg.
 rod('ORION_'+label+'_BAY_ATTACHMENT_PIN',p-Vector((.055,0,0)),p+Vector((.055,0,0)),.023,bays,metal)
 for sign in [-1,1]:box('ORION_'+label+'_BAY_ATTACHMENT_BRACKET_'+str(sign),p+Vector((sign*.052,0,.035)),(.014,.075,.10),bays,metal)
 joint=wheel(label,c,r,w,ctrl);gear_controls.append((label,ctrl,joint,p,c))

# Optical housing: flattened aperture face, asymmetric mounting cheek and rounded lower casing.
mount=rod('ORION_SENSOR_FIXED_MOUNT',(0,2.05,-.345),(0,2.05,-.48),.18,sensor,grey,64)
yaw=empty('ORION_SENSOR_YAW',(0,2.05,-.47));pitch=empty('ORION_SENSOR_PITCH',(0,2.05,-.80));parent_keep(pitch,yaw)
for side in [-1,1]:
 arm=box('ORION_SENSOR_YOKE_'+str(side),(side*.315,2.035,-.65),(.05,.19,.34),sensor,grey,.022);parent_keep(arm,yaw)
 cap=rod('ORION_SENSOR_PITCH_PIVOT_CAP_'+str(side),(side*.254,2.05,-.80),(side*.347,2.05,-.80),.09,sensor,grey,64);parent_keep(cap,yaw)
vc=[];fc=[];sections=[(-.245,.055,.09),(-.22,.175,.23),(-.12,.267,.32),(.09,.279,.345),(.235,.235,.294),(.25,.226,.287)];N=96
for dy,rx,rz in sections:
 for j in range(N):
  a=2*math.pi*j/N;u=math.cos(a);v=math.sin(a);vc.append((rx*u,2.05+dy,-.80+rz*v))
for k in range(len(sections)-1):
 for j in range(N):fc.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
fc += [tuple(reversed(range(N))),tuple((len(sections)-1)*N+j for j in range(N))]
housing=mesh('ORION_SENSOR_PITCH_HOUSING',vc,fc,sensor,grey)
for p in housing.data.polygons:p.use_smooth=len(p.vertices)==4
bevel(housing,.008);parent_keep(housing,pitch)
housing.modifiers.remove(housing.modifiers['Weighted_corner_normals'])
# Window centres are arranged to match R3, not borrowed from a different sensor specification.
windows=[('MAIN',-.033,-.026,.083,lens),('UPPER_BLUE',.095,.115,.037,blue),('RIGHT_MID',.132,.025,.034,lens),('LOWER_L',-.131,-.171,.030,lens),('LOWER_MID',-.038,-.210,.035,lens),('LOWER_R',.074,-.185,.032,lens),('LEFT_SMALL',-.155,.064,.024,lens)]
for name,x,z,r,m in windows:
 opening=rod('ORION_SENSOR_'+name+'_RECESS_CUTTER',(x,2.24,-.80+z),(x,2.34,-.80+z),r,cutters,None,64)
 parent_keep(opening,pitch)
 bo=housing.modifiers.new(name+'_WINDOW_RECESS','BOOLEAN');bo.operation='DIFFERENCE';bo.solver='EXACT';bo.object=opening
 # Annular rim gives actual thickness; separate optical disk is recessed by 11 mm.
 verts=[];faces=[]
 for yy,rr in [(2.299,r+.006),(2.303,r+.006),(2.303,r-.001),(2.287,r-.001)]:
  verts += [(x+rr*math.cos(j*2*math.pi/64),yy,-.80+z+rr*math.sin(j*2*math.pi/64)) for j in range(64)]
 for k in range(4):
  for j in range(64):faces.append((k*64+j,k*64+(j+1)%64,((k+1)%4)*64+(j+1)%64,((k+1)%4)*64+j))
 rim=mesh('ORION_SENSOR_'+name+'_WINDOW_RIM',verts,faces,sensor,metal);parent_keep(rim,pitch)
 glass=rod('ORION_SENSOR_'+name+'_OPTICAL_SURFACE',(x,2.280,-.80+z),(x,2.291,-.80+z),r-.003,sensor,m,64);parent_keep(glass,pitch)
 backing=rod('ORION_SENSOR_'+name+'_DARK_BACKING',(x,2.258,-.80+z),(x,2.271,-.80+z),r-.003,sensor,black,64);parent_keep(backing,pitch)
for side in [-1,1]:
 cover=rod('ORION_SENSOR_SIDE_ACCESS_COVER_'+str(side),(side*.268,2.01,-.80),(side*.278,2.01,-.80),.194,sensor,grey,64);parent_keep(cover,pitch)
 for j in range(8):
  a=2*math.pi*j/8;pt=Vector((side*.280,2.01+.168*math.cos(a),-.80+.168*math.sin(a)))
  screw=rod('ORION_SENSOR_SIDE_FASTENER_'+str(side)+'_'+str(j),pt,pt+Vector((side*.003,0,0)),.005,sensor,metal,6);parent_keep(screw,pitch)
housing['evidence']='A R3 aperture pattern and housing silhouette; B published housing comparison; C exact depth/back/hidden side'
yaw['visual_range_degrees']='-35 to +35; visual presentation only';pitch['visual_range_degrees']='-15 to +15; visual presentation only'

# Keyframes preserve geometry and wheel scale. Two-phase main fold is explicitly illustrative.
def key_rot(o,q,frame):
 o.rotation_quaternion=q;o.keyframe_insert(data_path='rotation_quaternion',frame=frame,group='Illustrative gear pose')
for frame,t in [(1,0),(20,0),(65,0),(100,1),(120,1),(130,1),(145,0),(160,0)]:
 for label,ctrl,joint,p,c in gear_controls:
  d=c-p
  if label=='NOSE':q=Quaternion((1,0,0),math.radians(-107)*t)
  else:
   side=1 if label.endswith('R') else -1
   horiz=math.hypot(d.x,d.y);targetx=side*.035;targety=-math.sqrt(horiz*horiz-targetx*targetx)
   az=math.atan2(targety,targetx)-math.atan2(d.y,d.x);az=(az+math.pi)%(2*math.pi)-math.pi
   yaw_t=0 if frame<=20 or frame==160 else 1
   qz=Quaternion((0,0,1),az*yaw_t)
   folded=qz@d;updy=-math.sqrt(d.length_squared-targetx*targetx-.22**2)
   ax=math.atan2(.22,updy)-math.atan2(folded.z,folded.y);ax=(ax+math.pi)%(2*math.pi)-math.pi
   q=Quaternion((1,0,0),ax*t)@qz
   if frame==160:q=Quaternion()
  key_rot(ctrl,q,frame)
  # Compensated axle joint keeps the tire aligned with the X axle during review motion.
  key_rot(joint,q.inverted(),frame)
for pivot,sign in door_controls:
 opening=97 if 'MAIN' in pivot.name else 85
 inspection=97 if 'MAIN' in pivot.name else 115
 for frame,angle in [(1,85),(20,opening),(65,opening),(100,opening),(120,0),(130,opening),(145,opening),(160,inspection)]:key_rot(pivot,Quaternion((0,1,0),math.radians(-sign*angle)),frame)
for o in controls.objects:
 if o.animation_data and o.animation_data.action:
  o.animation_data.action.name=o.name+'_Gear_Retract_Illustrative'
  # Blender 5 action channelbags.
  for layer in o.animation_data.action.layers:
   for strip in layer.strips:
    for slot in o.animation_data.action.slots:
     bag=strip.channelbag(slot)
     if bag:
      for fc in bag.fcurves:
       for kp in fc.keyframe_points:kp.interpolation='LINEAR'
s.frame_start=1;s.frame_end=160
for fr,name in [(1,'GEAR_DOWN_DEFAULT'),(65,'ILLUSTRATIVE_MAIN_REAR_SWING'),(100,'GEAR_IN_BAYS_DOORS_OPEN'),(120,'GEAR_RETRACTED_ILLUSTRATIVE'),(160,'BAY_INSPECTION_DOWN_DOORS_OPEN')]:s.timeline_markers.new(name,frame=fr)
s.frame_set(1)
s['stage']='D_GEAR_BAYS_SENSOR_REVIEW';s['revision']='D_'+REV;s['model_status']='Approved C v007 exterior; D components and illustrative poses pending review'
body['bay_interior_evidence']='C conservative cavity layout, liners and sparse roof supports; hidden interiors are not authenticated'
for o in source.all_objects:
 if o.get('stage')=='C':o['status']='C v007 primary shape approved by user'
# Standard viewport opens near the front components, with the entire asset selectable.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(CHECK),copy=True)
(P/f'Documentation/D_construction_{REV}.json').write_text(json.dumps({'checkpoint':str(CHECK),'source_objects':len(source.all_objects),'bay_specs':bay_specs,'poses':{'down':1,'rear_swing':65,'inside_open':100,'retracted':120,'inspection':160},'retraction':'Illustrative reconstruction, not documented real motion','approved_geometry_source':'Orion_C_primary_geometry_v007.blend'},indent=2),encoding='utf-8')
print('STAGE_D_SAVED',CHECK)
