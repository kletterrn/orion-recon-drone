"""Reference-led display asset. Run with Blender --background --python this_file.
Exterior artistic reconstruction; hidden mechanisms and profiles are approximate.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi, sqrt

OUT=Path(__file__).resolve().parents[1]/'Assets/ORD/Models/OrionE_Detailed'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
DRAFT='--draft' in sys.argv
TURRET_Y=2.52
NOSE_GEAR_Y=1.78
def coll(n):
 c=bpy.data.collections.new(n);scene.collection.children.link(c);return c
AIR=coll('01 | Airframe shells');WINGS=coll('02 | Wings and control surfaces');TAIL=coll('03 | Tail and propulsion');GEAR=coll('04 | Landing gear assemblies');EO=coll('05 | Optical turret');DETAIL=coll('06 | Seams and fasteners');MARK=coll('07 | Markings');STAGE=coll('08 | Studio');REF=coll('09 | Reference photographs (viewport only)')
def mat(n,col,rough=.4,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
paint=mat('Graphite blue | painted composite',(.095,.125,.165),.48,.06)
white=mat('Radome | warm ceramic white',(.76,.79,.80),.34)
dark=mat('Seals and recessed panel lines',(.017,.023,.032),.6)
rubber=mat('Tyre rubber',(.014,.018,.023),.82)
alloy=mat('Anodized aluminium',(.38,.44,.5),.27,.78)
chrome=mat('Polished oleo piston',(.7,.77,.81),.16,.95)
yellow=mat('Service stencil ochre',(.92,.64,.075),.44)
ink=mat('Stencil warm white',(.78,.81,.8),.48)
glass=mat('Optics | coated deep cyan',(.008,.029,.038),.12,.38)
blue=mat('Optics | violet interference coating',(.018,.024,.070),.15,.4)
red=mat('Port navigation ruby',(.65,.015,.025),.22,.25)
green=mat('Starboard navigation emerald',(.012,.45,.13),.2,.25)
for m in (paint,white,rubber):
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=190;noise.inputs['Detail'].default_value=2
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0007;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
def put(o,n,c,m):
 o.name=n
 for a in list(o.users_collection):a.objects.unlink(o)
 c.objects.link(o)
 if m:o.data.materials.append(m)
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o
def mesh(n,v,f,c,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);c.objects.link(o)
 if m:d.materials.append(m)
 for p in d.polygons:p.use_smooth=True
 return o
def bevel(o,w=.015,seg=3):
 mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=w;mod.segments=seg
 return o
def ball(n,p,s,c,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return put(o,n,c,m)
def rod(n,a,b,r,c,m,vertices=32):
 a=Vector(a);b=Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();put(o,n,c,m)
 for p in o.data.polygons:
  if len(p.vertices)>4:p.use_smooth=False
 return bevel(o,min(.003,r*.12),3)
def box(n,p,s,c,m,w=.012):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return bevel(put(o,n,c,m),w)
def line(n,pts,r=.002,m=dark,c=DETAIL,closed=False):
 d=bpy.data.curves.new(n,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=r;d.bevel_resolution=2;s=d.splines.new('POLY');s.points.add(len(pts)-1)
 for a,p in zip(s.points,pts):a.co=(*p,1)
 s.use_cyclic_u=closed;o=bpy.data.objects.new(n,d);c.objects.link(o);d.materials.append(m);return o
def torus(n,p,major,minor,c,m,axis=(0,0,1)):
 bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=64,minor_segments=12,location=p);o=bpy.context.object;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();return put(o,n,c,m)
# Linked fasteners keep thousands of individually editable details lightweight.
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1);fastmesh=bpy.context.object.data;fastmesh.name='Shared flush fastener mesh';bpy.data.objects.remove(bpy.context.object,do_unlink=True);fastmesh.materials.append(alloy)
def screw(p,r=.007):
 o=bpy.data.objects.new('Flush fastener',fastmesh);DETAIL.objects.link(o);o.location=p;o.scale=(r,r,r*.5);return o
stations=[(-3.8,.22,1.79,1.35),(-3.45,.28,1.84,1.27),(-2.8,.33,1.87,1.25),(-1.8,.38,1.91,1.23),(-.6,.415,1.96,1.21),(.7,.425,1.99,1.21),(1.65,.425,2.00,1.23),(2.40,.415,2.01,1.25),(2.80,.39,2.015,1.26),(3.12,.33,1.91,1.27),(3.50,.235,1.68,1.29),(3.80,.105,1.48,1.32),(3.98,.003,1.352,1.34)]
def profile(y):
 for i in range(len(stations)-1):
  if y<=stations[i+1][0]:break
 t=max(0,min(1,(y-stations[i][0])/(stations[i+1][0]-stations[i][0])));a=stations[max(0,i-1)];b=stations[i];c=stations[i+1];d=stations[min(len(stations)-1,i+2)]
 return [(.5*((2*b[j])+(-a[j]+c[j])*t+(2*a[j]-5*b[j]+4*c[j]-d[j])*t*t+(-a[j]+3*b[j]-3*c[j]+d[j])*t*t*t)) for j in (1,2,3)]
def skin(y,a,off=0):
 w,t,b=profile(y);v=sin(a);v=v if v>=0 else -abs(v)**.70
 return ((w+off)*cos(a),y,(t+b)/2+((t-b)/2+off)*v)
def shell(n,lo,hi,m):
 N=max(12,int((hi-lo)*28));v=[skin(lo+(hi-lo)*i/N,2*pi*j/96) for i in range(N+1) for j in range(96)];f=[]
 for i in range(N):
  for j in range(96):f.append((i*96+j,i*96+(j+1)%96,(i+1)*96+(j+1)%96,(i+1)*96+j))
 f.extend([tuple(reversed(range(96))),tuple(N*96+j for j in range(96))]);return mesh(n,v,f,AIR,m)
shell('Continuous graphite fuselage',-3.8,2.397,paint);shell('Sculpted white radome',2.402,3.98,white)
for y in [-3.43,-2.72,-1.65,.75,2.40]:
 line('Circumferential shell joint',[skin(y,2*pi*j/160,.002) for j in range(160)],.002,closed=True)
 for j in range(32):screw(skin(y+.022,2*pi*j/32,.004),.006)
for side in [-1,1]:
 # Long service hatches follow the curved surface instead of floating planes.
 for ya,yb,al,ah in [(.86,2.32,.03,1.12),(-2.58,-1.78,-.04,1.04),(-.8,.58,.12,1.21)]:
  def surf(y,a):return skin(y,a if side==1 else pi-a,.004)
  pts=[surf(ya+(yb-ya)*i/40,al) for i in range(41)]+[surf(yb,al+(ah-al)*i/20) for i in range(1,21)]+[surf(yb-(yb-ya)*i/40,ah) for i in range(1,41)]+[surf(ya,ah-(ah-al)*i/20) for i in range(1,21)]
  line('Service hatch perimeter',pts,.0015,closed=True)
  for y in [ya+.04+(yb-ya-.08)*i/10 for i in range(11)]:
   for a in [al+.045,ah-.045]:screw(surf(y,a),.0035)
  for y in [ya+.17,yb-.17]:
   p=surf(y,.28);ball('Recessed quarter-turn latch',p,(.004,.017,.013),DETAIL,alloy)
 # Engine cooling louvers and a recessed intake.
 for j in range(13):
  y=-3.30+j*.042;p=skin(y,.25 if side==1 else pi-.25,.005);o=box('Engine cooling louver',p,(.015,.014,.105),DETAIL,dark,.005)
 ball('Engine intake shadow',(side*.265,-3.52,1.57),(.018,.19,.09),AIR,dark)
 rod('Exhaust surround',(side*.29,-3.11,1.30),(side*.42,-3.28,1.28),.065,TAIL,alloy)
 rod('Exhaust dark interior',(side*.423,-3.283,1.279),(side*.43,-3.29,1.278),.051,TAIL,dark)
# Dense cosine-spaced airfoil sections, with separate actual trailing surfaces.
def foil(s,span,u):
 t=(span-.38)/7.62;front=.85-.64*t;chord=1.65-.97*t;z=1.46+.16*t
 thick=5*.115*chord*(.2969*sqrt(max(u,0))-.126*u-.3516*u*u+.2843*u**3-.1036*u**4)
 cam=.024*chord*4*u*(1-u)
 return front,chord,z,thick,cam
def wing(n,s,a,b,u0,u1):
 v=[];NR=32;NC=44
 for k in range(NR+1):
  span=a+(b-a)*k/NR
  for top in [1,-1]:
   for j in range(NC+1):
    u=u0+(u1-u0)*(1-cos(pi*j/NC))/2;front,c,z,h,cam=foil(s,span,u);v.append((s*span,front-c*u,z+cam+top*h))
 ring=2*(NC+1);f=[]
 for k in range(NR):
  for q in [0,NC+1]:
   for j in range(NC):
    i=k*ring+q+j;f.append((i,i+1,i+ring+1,i+ring))
  for j in [0,NC]:
   i=k*ring+j;f.append((i,i+ring,i+ring+NC+1,i+NC+1))
 for k in [0,NR]:
  for j in range(NC):
   i=k*ring+j;f.append((i,i+NC+1,i+NC+2,i+1))
 return mesh(n,v,f,WINGS,paint)
for s,label in [(-1,'PORT'),(1,'STARBOARD')]:
 wing(label+' main wing',s,.38,8,0,.745)
 for a,b,n in [(.42,2.6,'inboard flap'),(2.62,4.6,'outboard flap'),(4.62,7.86,'aileron'),(7.875,8,'tip trailing cap')]:wing(label+' '+n,s,a,b,.753,1)
 for span in [2.6,4.6,7.87]:
  line('Wing transverse panel joint',[(s*span,foil(s,span,u)[0]-foil(s,span,u)[1]*u,foil(s,span,u)[2]+foil(s,span,u)[3]+foil(s,span,u)[4]+.0015) for u in [i/80 for i in range(81)]],.0018)
 for span in [1.2,2.3,3.3,4.35,5.0,6.2,7.4]:
  front,c,z,h,cam=foil(s,span,.75);ball('Control surface hinge fairing',(s*span,front-c*.74,z-.04),(.047,.17,.045),WINGS,paint)
  for off in [-.028,.028]:screw((s*span+off,front-c*.73,z+h+cam+.004),.005)
 for j in range(80):
  span=.6+j*.09;front,c,z,h,cam=foil(s,span,.18);screw((s*span,front-c*.18,z+h+cam+.002),.004)
 ball(label+' navigation housing',(s*7.98,.02,1.625),(.045,.13,.028),WINGS,alloy)
 ball(label+' navigation lens',(s*8.005,.052,1.64),(.024,.065,.022),WINGS,red if s==-1 else green)
 for yy in [-.23,-.35]:rod('Wingtip static wick',(s*7.94,yy,1.62),(s*7.97,yy-.17,1.62),.003,DETAIL,dark,12)
 ball('Wing root fillet',(s*.405,.0,1.46),(.26,.86,.12),AIR,paint)
# Airfoil V tail surfaces, canted outwards, with distinct ruddervators.
for s,label in [(-1,'PORT'),(1,'STARBOARD')]:
 def tailpoint(t,u,side):
  x=s*(.22+.94*t);z=1.70+1.40*t;front=-2.60-.64*t;c=1.04-.34*t;h=.06*c*sin(pi*u)**.7
  return(x+s*side*h,front-c*u,z-side*h*.58)
 for u0,u1,n in [(0,.73,'fixed V stabilizer'),(.742,1,'ruddervator')]:
  v=[];f=[]
  for k in range(25):
   for sign in [1,-1]:
    for j in range(33):v.append(tailpoint(k/24,u0+(u1-u0)*j/32,sign))
  for k in range(24):
   for sign in [0,33]:
    for j in range(32):i=k*66+sign+j;f.append((i,i+1,i+67,i+66))
   for j in [0,32]:i=k*66+j;f.append((i,i+66,i+99,i+33))
  for k in [0,24]:
   for j in range(32):i=k*66+j;f.append((i,i+33,i+34,i+1))
  mesh(label+' '+n,v,f,TAIL,paint)
 line('Tail rudder hinge', [tailpoint(i/60,.736,1) for i in range(61)],.002)
 for t in [.12,.43,.73,.95]:
  p=tailpoint(t,.74,1);ball('Rudder hinge cover',p,(.016,.058,.031),TAIL,paint)
 for j in range(24):screw(tailpoint(j/24,.16,1),.004)
 rod('Tail static discharger',tailpoint(1,.96,0),Vector(tailpoint(1,.96,0))+Vector((0,-.2,0)),.003,DETAIL,dark)
rod('Engine rear collar',(0,-3.66,1.60),(0,-3.91,1.60),.245,TAIL,paint,64)
rod('Propeller shaft',(0,-3.86,1.60),(0,-4.02,1.60),.068,TAIL,chrome,48)
ball('Pusher spinner',(0,-4.08,1.60),(.16,.25,.16),TAIL,white)
for s in [-1,1]:
 v=[];f=[]
 for i in range(41):
  t=i/40;r=.11+.85*t;ch=.045+.135*sin(pi*t)**.7;twist=.52-.36*t
  for j in range(24):
   a=2*pi*j/24;u=ch*.5*cos(a);h=.013*sin(a)*sin(pi*(.06+.9*t))
   v.append((s*(.10*t*t+u*cos(twist)-h*sin(twist)),-3.96+u*sin(twist)+h*cos(twist),1.60+s*r))
 for i in range(40):
  for j in range(24):f.append((i*24+j,i*24+(j+1)%24,(i+1)*24+(j+1)%24,(i+1)*24+j))
 mesh('Twisted composite propeller blade',v,f,TAIL,dark)
# Forward EO assembly, ahead of the nose gear as shown in the supplied side view.
rod('Turret yaw bearing',(0,TURRET_Y,1.28),(0,TURRET_Y,1.17),.195,EO,paint,64)
torus('Turret yaw bearing seal',(0,TURRET_Y,1.182),.193,.006,EO,dark)
ball('Turret articulated shell',(0,TURRET_Y,.98),(.285,.29,.285),EO,white)
v=[];f=[]
for i in range(17):
 a=.18+1.13*i/16
 for j in range(96):
  b=2*pi*j/96;v.append((.301*sin(a)*cos(b),TURRET_Y+.304*sin(a)*sin(b),.98+.301*cos(a)))
for i in range(16):
 for j in range(96):f.append((i*96+j,i*96+(j+1)%96,(i+1)*96+(j+1)%96,(i+1)*96+j))
o=mesh('Turret upper protective shroud',v,f,EO,paint);mod=o.modifiers.new('Shroud wall','SOLIDIFY');mod.thickness=.006
for s in [-1,1]:
 rod('Gimbal trunnion',(s*.268,TURRET_Y,1.025),(s*.302,TURRET_Y,1.025),.075,EO,paint,48)
 rod('Trunnion bearing cap',(s*.302,TURRET_Y,1.025),(s*.305,TURRET_Y,1.025),.045,EO,alloy,48)
def optical_patch(n,x,z,r,m,offset):
 # Conformal optical windows avoid the earlier protruding stack of lens tubes.
 def pt(dx,dz):return(dx,TURRET_Y+.29*sqrt(max(.008,1-(dx/.285)**2-((dz-.98)/.285)**2))+offset,dz)
 v=[pt(x,z)]+[pt(x+r*k/8*cos(2*pi*i/64),z+r*k/8*sin(2*pi*i/64)) for k in range(1,9) for i in range(64)]
 f=[(0,i+1,(i+1)%64+1) for i in range(64)]
 for k in range(7):
  for i in range(64):a=1+k*64+i;b=1+k*64+(i+1)%64;f.append((a,b,b+64,a+64))
 mesh(n,v,f,EO,m)
 return [pt(x+r*cos(2*pi*i/96),z+r*sin(2*pi*i/96)) for i in range(96)]
for x,z,r,m in [(-.075,1.005,.094,glass),(.105,1.10,.042,blue),(.133,.985,.041,glass),(-.12,.845,.037,glass),(-.018,.811,.036,glass),(.086,.835,.033,blue)]:
 optical_patch('Optical aperture gasket',x,z,r+.008,dark,.002)
 rim=optical_patch('Flush multicoated optical window',x,z,r,m,.004)
 line('Optical retaining bezel',rim,.0025,alloy,EO,True)
# Gear: sculpted tyres, concentric rims, brakes, bolts, fork, oleo and hydraulic lines.
for label,x,y,r in [('NOSE',0,NOSE_GEAR_Y,.225),('PORT',-1.15,-.63,.265),('STARBOARD',1.15,-.63,.265)]:
 before_gear=set(GEAR.objects)
 z=r+.015;main=label!='NOSE';s=-1 if x<0 else 1;top=(s*.35 if main else 0,y-.20 if main else y,1.33);ax=(x,y,z)
 # Solid closed tyre section with a broad crown and shallow recessed tread grooves.
 section=[(-.056,.45),(-.076,.56),(-.084,.72),(-.076,.90),(-.057,.982)]
 for dx in [-.05,-.034,-.017,0,.017,.034,.05]:
  section.extend([(dx-.0018,.997),(dx-.001, .983),(dx+.001,.983),(dx+.0018,.997)])
 section.extend([(.057,.982),(.076,.90),(.084,.72),(.076,.56),(.056,.45)])
 v=[(x+dx,y+r*rr*cos(2*pi*j/128),z+r*rr*sin(2*pi*j/128)) for dx,rr in section for j in range(128)];f=[]
 for i in range(len(section)):
  for j in range(128):f.append((i*128+j,i*128+(j+1)%128,((i+1)%len(section))*128+(j+1)%128,((i+1)%len(section))*128+j))
 mesh(label+' rounded tyre',v,f,GEAR,rubber)
 for ss in [-1,1]:torus('Tyre sidewall mould seam',(x+ss*.082,y,z),r*.72,.0018,GEAR,rubber,(1,0,0))
 rod(label+' wheel core',(x-.063,y,z),(x+.063,y,z),r*.52,GEAR,alloy,64)
 for ss in [-1,1]:
  torus('Rim rolled lip',(x+ss*.068,y,z),r*.48,.009,GEAR,chrome,(1,0,0))
  rod('Brake disc',(x+ss*.069,y,z),(x+ss*.077,y,z),r*.36,GEAR,dark,48)
  rod('Axle bearing',(x+ss*.078,y,z),(x+ss*.085,y,z),r*.19,GEAR,alloy,32)
  for j in range(8):
   a=2*pi*j/8;rod('Hub bolt',(x+ss*.078,y+r*.29*cos(a),z+r*.29*sin(a)),(x+ss*.087,y+r*.29*cos(a),z+r*.29*sin(a)),.008,GEAR,chrome,6)
 fork=(x+s*.105,y,z+.22);knee=(x*.88,y-.075,z+.43)
 rod(label+' swept upper strut',top,knee,.047 if main else .045,GEAR,alloy)
 rod(label+' polished oleo',knee,fork,.027,GEAR,chrome)
 rod('Oleo lower sleeve',fork,(x+s*.105,y,z+.10),.043,GEAR,paint)
 rod('Wheel fork',(x+s*.105,y,z+.13),(x+s*.105,y,z),.032,GEAR,alloy)
 rod('Wheel axle',(x-s*.07,y,z),(x+s*.13,y,z),.031,GEAR,chrome)
 rod('Rear drag brace',(top[0],y-.42,1.21),knee,.022,GEAR,alloy)
 mid=(x+s*.11,y+.11,z+.40)
 rod('Torque link upper',(knee[0],knee[1],knee[2]+.07),mid,.018,GEAR,paint)
 rod('Torque link lower',mid,fork,.018,GEAR,paint)
 for p in [top,knee,fork,mid]:rod('Clevis pivot pin',Vector(p)+Vector((-.055,0,0)),Vector(p)+Vector((.055,0,0)),.021,GEAR,chrome,16)
 pts=[]
 for j in range(81):
  t=j/80;pt=Vector(top).lerp(Vector(fork),t);pt.x+=.048;pt.y+=.045*sin(t*pi);pts.append(pt)
 line('Flexible brake hydraulic hose',pts,.007,dark,GEAR)
 for t in [.2,.45,.70]:
  p=Vector(top).lerp(Vector(knee),t);torus('Strut retaining collar',p,.05,.008,GEAR,chrome,Vector(knee)-Vector(top))
 if not main:
  pts=[(.063+.038*cos(j*pi*18/150),y-.042+.038*sin(j*pi*18/150),.62+j*.0024) for j in range(151)];line('Nose suspension coil',pts,.008,chrome,GEAR)
 box(label+' gear bay recess',(top[0],y-.1,1.225),(.20,.51,.022),GEAR,dark)
 o=box(label+' open gear door',(top[0]+s*.14,y-.09,1.13),(.023,.49,.19),GEAR,paint);o.rotation_euler.y=s*.25
 for o in set(GEAR.objects)-before_gear:o['assembly']=label
# Aerials, dorsal radome and flush hardware.
ball('Dorsal communications radome',(0,-.5,1.965),(.15,.24,.17),AIR,white)
for yy,h in [(2.22,.08),(-1.15,.16),(-2.04,.09)]:
 top=profile(yy)[1]-.01
 mesh('Swept dorsal blade aerial',[(-.012,yy,top),(.012,yy,top),(-.009,yy-.08,top+h),(.009,yy-.08,top+h),(-.010,yy-.19,top),(.010,yy-.19,top)],[(0,2,4),(1,5,3),(0,1,3,2),(2,3,5,4),(4,5,1,0)],DETAIL,dark)
rod('Underbody pitot boom',(.65,.45,1.10),(.65,1.95,1.10),.009,DETAIL,alloy)
rod('Pitot tip',(.65,1.95,1.10),(.65,2.15,1.10),.0035,DETAIL,chrome)
rod('Pitot stand',(.65,.58,1.10),(.65,.58,1.45),.012,DETAIL,paint)
fontpath=Path('C:/Windows/Fonts/arial.ttf');font=bpy.data.fonts.load(str(fontpath)) if fontpath.exists() else None
def text(n,body,p,size,m,side=1):
 d=bpy.data.curves.new(n,'FONT');d.body=body;d.size=size;d.extrude=0;d.fill_mode='FRONT';d.space_character=1.1
 if font:d.font=font
 o=bpy.data.objects.new(n,d);MARK.objects.link(o);d.materials.append(m);o.location=p
 # Proper right-handed basis: text horizontal along fuselage, normal outward.
 o.rotation_euler=Matrix(((0,0,side),(side,0,0),(0,1,0))).to_euler();return o
for s in [-1,1]:
 text('Aircraft identity','ORION-E', (s*.445,1.03 if s==1 else 2.25,1.73),.22,ink,s)
 text('Airframe service stencil','E', (s*.453,.34 if s==1 else .44,1.61),.04,ink,s)
 for yy in [-2.25,-.9,.6,2.30]:
  w,t,b=profile(yy);text('Service point identification','+', (s*(w+.006),yy,1.55),.065,yellow,s)
 for yy in [2.12,-2.18]:
  w,t,b=profile(yy);text('Maintenance stencil','ACCESS PANEL', (s*(w+.008),yy,1.43),.022,ink,s)
# Conform lettering to the body skin; flat text would visibly float on the taper.
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
import bmesh
for old in list(MARK.objects):
 data=bpy.data.meshes.new_from_object(old.evaluated_get(deps));world=old.matrix_world.copy();side=1 if old.location.x>0 else -1
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=5,use_grid_fill=True);bm.to_mesh(data);bm.free()
 for vertex in data.vertices:
  p=world@vertex.co;w,t,b=profile(p.y);mid=(t+b)/2;h=(t-b)/2
  vv=(p.z-mid)/h;vv=vv if vv>=0 else -abs(vv)**(1/.70)
  p.x=side*(w*sqrt(max(.001,1-vv**2))+.0025);vertex.co=p
 obj=bpy.data.objects.new(old.name+' | fitted to skin',data);MARK.objects.link(obj);bpy.data.objects.remove(old,do_unlink=True)
# Studio and render cameras.
floor=mat('Studio | slate',(.052,.069,.093),.58)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.015));put(bpy.context.object,'Studio ground',STAGE,floor)
scene.world=bpy.data.worlds.new('Studio ambience');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.26,.32,.43,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for n,p,power,size in [('Large key',(2,5,10),2400,8),('Port softbox',(-7,0,6),1900,7),('Rear rim',(2,-7,7),2800,6),('Nose fill',(0,9,4),700,5)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=put(bpy.context.object,n,STAGE,None);o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(n,p,target,scale):
 bpy.ops.object.camera_add(location=p);o=put(bpy.context.object,n,STAGE,None);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;o.data.clip_end=1000;return o
cams=[camera('01 | HERO',(12,15,7.5),(0,0,1.25),18),camera('02 | NOSE DETAIL',(6,4,2.8),(0,2.1,1.14),4.0),camera('03 | REAR DETAIL',(5,-8,4),(0,-2.9,1.8),6.4),camera('04 | SIDE',(12,0,1.55),(0,0,1.55),9.6),camera('05 | TOP',(0,0,20),(0,0,1),18),camera('06 | FORWARD PROFILE',(12,2.28,1.19),(0,2.28,1.19),4.25)]
for path,label in [('C:/Users/david/AppData/Local/Temp/codex-clipboard-ebec4006-5cff-480b-b56d-51eff7bd9ccf.png','Flight reference'),('C:/Users/david/AppData/Local/Temp/codex-clipboard-ba0681c2-2268-4d7c-aa56-b5cc6ca74ad3.png','Ground reference'),('C:/Users/david/AppData/Local/Temp/codex-clipboard-7b45cbe0-91dc-414b-be21-95e404d19304.png','Revision 02 side reference - turret ahead of gear')]:
 if Path(path).exists():
  img=bpy.data.images.load(path);img.pack();o=bpy.data.objects.new(label,None);REF.objects.link(o);o.empty_display_type='IMAGE';o.data=img;o.empty_display_size=8;o.hide_render=True;o.hide_viewport=True
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1920;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.camera=cams[0]
scene['Asset description']='Reference-led Orion-E exterior display model. Approximate 8 m class fuselage / 16 m span. Artistic reconstruction, no engineering internals.'
scene['Configuration']='Gear down; white radome; multi-aperture EO turret; clean wings; graphite paint.'
scene['Revision']='02 | Forward turret, longer radome, low wing roots, refined landing gear'
scene['Turret center Y']=TURRET_Y
scene['Nose gear axle Y']=NOSE_GEAR_Y
scene['Scale reference']='https://kronshtadt.ru/assets/files/productfiles/Orion_eng.pdf'
scene['Limitations']='Mixed photographic configurations. Hidden details interpreted. No game LODs, collision, rig or authored texture atlas.'
# Consistent outward normals on the closed manufactured shells.
import bmesh
for data in list(bpy.data.meshes):
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
# Add automatic starting UVs in one batch. Linked fasteners use generated coordinates.
bpy.ops.object.select_all(action='DESELECT')
for o in list(AIR.objects)+list(WINGS.objects)+list(TAIL.objects)+list(EO.objects):
 if o.type=='MESH':o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_end=500
bpy.ops.file.pack_all()
if not DRAFT:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'OrionE_Detailed.blend'))
stats={'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'base_polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'file':str(OUT/'OrionE_Detailed.blend')}
if not DRAFT:(OUT/'asset_statistics.json').write_text(json.dumps(stats,indent=2))
print('ASSET_STATS',stats,flush=True)
for cam,name in zip(cams,['Hero','Nose_Detail','Rear_Detail','Side','Top','Forward_Profile']):
 if DRAFT and name not in ['Hero','Forward_Profile']:continue
 scene.render.resolution_percentage=65 if DRAFT else 100
 scene.cycles.samples=20 if DRAFT else 64
 scene.camera=cam;scene.render.filepath=str(OUT/(('Draft_' if DRAFT else '')+name+'.png'));bpy.ops.render.render(write_still=True)
scene.camera=cams[0]
if not DRAFT:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'OrionE_Detailed.blend'))
print('ORION_DETAILED_COMPLETE',flush=True)
