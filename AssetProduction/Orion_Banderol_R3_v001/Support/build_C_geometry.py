"""Build editable Orion primary geometry from the approved B checkpoint."""
from pathlib import Path
import bpy, bmesh, json, math, sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
REV=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
CHECKPOINT=ROOT/f'Orion/checkpoints/Orion_C_primary_geometry_{REV}.blend'
if CHECKPOINT.exists(): raise RuntimeError('Use a new numbered revision; checkpoint already exists')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Orion/checkpoints/Orion_B_reference_scale_v001.blend'))
bpy.context.preferences.filepaths.save_version=0
s=bpy.data.scenes['ORION_SCALE_REVIEW'];s.name='ORION_GEOMETRY_REVIEW';bpy.context.window.scene=s
s['stage']='C_PRIMARY_GEOMETRY_PENDING_REVIEW';s['model_status']='Primary source geometry; gear/sensor are presentation envelopes'
s['configuration']='Orion_R3';s['revision']=REV
for c in [bpy.data.collections['ORION_SETUP_GUIDES'],bpy.data.collections['00_REFERENCE']]:
    c.hide_render=True;c.hide_viewport=True
source=bpy.data.collections['10_SOURCE'];present=bpy.data.collections['20_PRESENTATION']
root=bpy.data.objects['ORION_ROOT']
def coll(name,parent):
    c=bpy.data.collections.new(name);parent.children.link(c);return c
air=coll('ORION_AIRFRAME',source);wing=coll('ORION_WINGS',source);tail=coll('ORION_TAIL_REAR',source)
proxy=coll('ORION_LAYOUT_ENVELOPES_NOT_FINAL',present);studio=coll('ORION_REVIEW_STUDIO',present)
def mat(name,color,roughness=.65,metallic=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=roughness;n.inputs['Metallic'].default_value=metallic
    return m
grey=mat('ORION_GREY_REVIEW',(.24,.27,.30));white=mat('ORION_WHITE_NOSE_REVIEW',(.79,.79,.76))
dark=mat('ORION_DARK_REVIEW',(.025,.03,.036));metal=mat('ORION_STRUT_REVIEW',(.45,.48,.50),.45,.5)
clay=mat('ORION_NEUTRAL_CLAY',(.48,.51,.54),.8)
clay.use_fake_user=True
floor_mat=mat('ORION_STUDIO_FLOOR',(.16,.18,.20),.85)
def mesh(name,vertices,faces,col,material,evidence,origin=(0,0,0)):
    d=bpy.data.meshes.new(name+'_MESH');d.from_pydata(vertices,[],faces);d.update()
    bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
    o=bpy.data.objects.new(name,d);col.objects.link(o);o.parent=root;d.materials.append(material)
    for p in d.polygons:p.use_smooth=True
    o['evidence']=evidence;o['stage']='C';o['status']='Primary geometry pending silhouette review'
    if origin!=(0,0,0):
        offset=Vector(origin)
        for v in d.vertices:v.co-=offset
        o.location=offset
    return o

# Stations describe width/crown/keel independently. No elongated-cylinder body.
# Hidden sections and absolute station locations remain C visual approximations.
body_stations=[(-3.70,.205,.25,-.18),(-3.45,.26,.34,-.25),(-3.05,.305,.365,-.31),
    (-2.30,.34,.38,-.355),(-1.4,.375,.40,-.38),(-.55,.40,.42,-.40),
    (.45,.405,.40,-.385),(1.25,.395,.39,-.37),(2.05,.37,.375,-.35),
    (2.75,.35,.355,-.34),(3.10,.345,.345,-.34)]
# Revised from user side/profile photos: forward body does not swell into the radome.
# White shell is shorter, with an arched upper outline and nearly level lower edge.
nose_stations=[(3.10,.345,.345,-.34),(3.23,.342,.32,-.34),
    (3.40,.325,.255,-.34),(3.58,.270,.13,-.339),(3.74,.195,-.01,-.335),
    (3.90,.087,-.18,-.335),(3.98,.023,-.285,-.328),(4.0,.001,-.318,-.321)]
def pchip(values,index,y):
    xs=[p[0] for p in values];ys=[p[index] for p in values]
    delta=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i]) for i in range(len(xs)-1)]
    tang=[delta[0]]
    for i in range(1,len(xs)-1):
        if delta[i-1]*delta[i]<=0:tang.append(0)
        else:
            h0=xs[i]-xs[i-1];h1=xs[i+1]-xs[i];w1=2*h1+h0;w2=h1+2*h0
            tang.append((w1+w2)/(w1/delta[i-1]+w2/delta[i]))
    tang.append(delta[-1]);i=next((i for i in range(len(xs)-1) if y<=xs[i+1]),len(xs)-2)
    h=xs[i+1]-xs[i];t=max(0,min(1,(y-xs[i])/h))
    return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*tang[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*tang[i+1]
def shell(name,stations,material):
    ys=[]
    for a,b in zip(stations[:-1],stations[1:]):
        n=max(3,round((b[0]-a[0])*10))
        ys.extend(a[0]+(b[0]-a[0])*j/n for j in range(n))
    ys.append(stations[-1][0]);nv=96;verts=[]
    for y in ys:
        w=pchip(stations,1,y);top=pchip(stations,2,y);bottom=pchip(stations,3,y)
        for j in range(nv):
            a=2*math.pi*j/nv;u=math.cos(a);v=math.sin(a)
            # R10 front-oblique view corroborates narrow rounded crown, broad
            # lower cheeks and a flattened base, rather than an elliptical bulb.
            # User correction: the same section family continues through the
            # entire fuselage; station widths/heights still control its taper.
            x1=w*math.copysign(abs(u)**(1.18 if v>=0 else .45),u)
            zn=.17+.83*v if v>=0 else .17*(1+v)
            z1=bottom+(top-bottom)*zn
            x=x1;z=z1
            # Slightly inclined mating boundary, shared by both closed shells.
            seam_weight=max(0,1-abs(y-3.10)/.65)**2
            yy=y+.045*(zn-.5)*seam_weight
            verts.append((x,yy,z))
    faces=[(i*nv+j,i*nv+(j+1)%nv,(i+1)*nv+(j+1)%nv,(i+1)*nv+j) for i in range(len(ys)-1) for j in range(nv)]
    faces.extend([tuple(reversed(range(nv))),tuple((len(ys)-1)*nv+j for j in range(nv))])
    o=mesh(name,verts,faces,air,material,'A visible contours / C station widths and hidden sections')
    # Preserve mating cross-sections instead of shrinking the ngon cap under subdivision.
    creases=o.data.attributes.new('crease_edge','FLOAT','EDGE')
    for edge in o.data.edges:
        a,b=(o.data.vertices[i].co for i in edge.vertices)
        if all(i<nv for i in edge.vertices) or all(i>=(len(ys)-1)*nv for i in edge.vertices):
            creases.data[edge.index].value=1.0
    for poly in o.data.polygons:
        if len(poly.vertices)>4:poly.use_smooth=False
    sub=o.modifiers.new('Editable_surface_subdivision','SUBSURF');sub.levels=1;sub.render_levels=2
    o['stations_json']=json.dumps(stations);return o
body=shell('ORION_FUSELAGE',body_stations,grey)
body['cross_section_status']='Same normalized cross-section as white nose throughout: narrow crown, fuller lower sides, flattened base; station taper retained'
nose=shell('ORION_NOSE_WHITE',nose_stations,white)
nose['cross_section_status']='R3/R7/R10 visible outline; C hidden sections: narrow crown, broad lower cheeks, flattened base'

def foil_thickness(u,t):
    return 5*t*(.2969*math.sqrt(max(0,u))-.126*u-.3516*u*u+.2843*u**3-.1036*u**4)
def foil_ring(chord,thick,n=40):
    us=[.5*(1-math.cos(math.pi*j/n)) for j in range(n+1)]
    return [(u,foil_thickness(u,thick)) for u in us]+[(u,-foil_thickness(u,thick)) for u in reversed(us[1:-1])]
def wing_section(span,u,side):
    t=(span-.28)/(8-.28);chord=1.33-.70*t;front=-.52-.13*t
    z=.235+.02*t;thickness=.105-.025*t;camber=.018*math.sin(math.pi*u)
    return (side*span,front-chord*u,z+chord*camber),chord,thickness
def surface(name,side,sp0,sp1,u0,u1,col=wing,is_tail=False):
    rings=[];verts=[];nspan=max(10,int((sp1-sp0)*6));nchord=32
    for k in range(nspan+1):
        span=sp0+(sp1-sp0)*k/nspan
        us=[u0+(u1-u0)*.5*(1-math.cos(math.pi*j/nchord)) for j in range(nchord+1)]
        samples=[(u,1) for u in us]+[(u,-1) for u in reversed(us)]
        for u,sign in samples:
            if not is_tail:
                p,c,t=wing_section(span,u,side);h=c*foil_thickness(u,t)
                verts.append((p[0],p[1],p[2]+sign*h))
            else:
                t=span;c=.90-.34*t;front=-2.69-.56*t
                h=c*foil_thickness(u,.105);x=side*(.22+1.38*t);z=.245+1.36*t
                verts.append((x+side*sign*h*.702,front-c*u,z-sign*h*.712))
    nr=2*(nchord+1);faces=[]
    for k in range(nspan):
        for j in range(nr):faces.append((k*nr+j,k*nr+(j+1)%nr,(k+1)*nr+(j+1)%nr,(k+1)*nr+j))
    faces.extend([tuple(reversed(range(nr))),tuple(nspan*nr+j for j in range(nr))])
    # Remove coincident leading/trailing vertices before recalculating normals.
    o=mesh(name,verts,faces,col,grey,'B compatible surface layout / C exact section and split stations')
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o['profile_status']='Visual airfoil thickness; no authentic aerodynamic section claimed'
    return o
for side,label in [(-1,'L'),(1,'R')]:
    surface('ORION_WING_'+label,side,.28,8,0,.754)
    for a,b,title in [(.28,.65,'ROOT_TRAILING'),(.65,4.20,'FLAP'),(4.20,4.23,'MID_TRAILING'),(4.23,7.86,'AILERON'),(7.86,8,'TIP_TRAILING')]:
        surface('ORION_'+title+'_'+label,side,a,b,.760,1)
    surface('ORION_TAIL_'+label,side,0,1,0,.74,tail,True)
    surface('ORION_RUDDERVATOR_'+label,side,0,1,.746,1,tail,True)
    # Minimal root transition shares the wing's shoulder and blends outboard.
    v=[];faces=[];nr=40
    for k in range(9):
        span=.26+.55*k/8;blend=(1-k/8)**2
        for u,sign in [(j/(nr-1),1) for j in range(nr)]+[(j/(nr-1),-1) for j in reversed(range(nr))]:
            p,c,t=wing_section(span,u,side);h=c*foil_thickness(u,t)+.08*blend*math.sin(math.pi*u)
            v.append((p[0],p[1],p[2]+sign*h))
    r=nr*2
    for k in range(8):
        for j in range(r):faces.append((k*r+j,k*r+(j+1)%r,(k+1)*r+(j+1)%r,(k+1)*r+j))
    faces.extend([tuple(reversed(range(r))),tuple(8*r+j for j in range(r))])
    mesh('ORION_WING_ROOT_BLEND_'+label,v,faces,air,grey,'C restrained root transition pending overhead evidence')

def revolve(name,stations,material,col=tail,center_z=.045):
    nv=64;v=[(r*math.cos(j*2*math.pi/nv),y,center_z+r*math.sin(j*2*math.pi/nv)) for y,r in stations for j in range(nv)]
    f=[(i*nv+j,i*nv+(j+1)%nv,(i+1)*nv+(j+1)%nv,(i+1)*nv+j) for i in range(len(stations)-1) for j in range(nv)]
    f.extend([tuple(reversed(range(nv))),tuple((len(stations)-1)*nv+j for j in range(nv))])
    return mesh(name,v,f,col,material,'B rear propeller layout / C local collar and spinner profile')
revolve('ORION_REAR_COLLAR',[(-3.66,.205),(-3.74,.207),(-3.78,.18)],grey)
revolve('ORION_PROPELLER_HUB',[(-3.76,.065),(-3.87,.065)],metal)
spinner=revolve('ORION_PUSHER_SPINNER',[(-3.825,.15),(-3.87,.145),(-3.94,.105),(-3.985,.045),(-4.0,.001)],grey)
for side,label in [(1,'A'),(-1,'B')]:
    v=[];f=[];nr=20
    for i in range(33):
        t=i/32;r=.10+.86*t;chord=.045+.135*math.sin(math.pi*(.08+.9*t))**.8
        twist=.58-.36*t;sweep=.07*t*t
        for j in range(nr):
            a=2*math.pi*j/nr;u=.5*chord*math.cos(a);h=.010*math.sin(a)*math.sin(math.pi*(.08+.9*t))
            v.append((side*(sweep+u*math.cos(twist)-h*math.sin(twist)),-3.81+u*math.sin(twist)+h*math.cos(twist),.045+side*r))
    for i in range(32):
        for j in range(nr):f.append((i*nr+j,i*nr+(j+1)%nr,(i+1)*nr+(j+1)%nr,(i+1)*nr+j))
    f.extend([tuple(reversed(range(nr))),tuple(32*nr+j for j in range(nr))])
    mesh('ORION_PROPELLER_BLADE_'+label,v,f,tail,dark,'B two-blade baseline / C exact blade profile',origin=(0,-3.81,.045))

def cylinder(name,a,b,r,material,col=proxy):
    axis=Vector(b)-Vector(a);rot=axis.to_track_quat('Z','Y');v=[];n=32
    for p in [Vector(a),Vector(b)]:
        v.extend(p+rot@Vector((r*math.cos(j*2*math.pi/n),r*math.sin(j*2*math.pi/n),0)) for j in range(n))
    f=[(j,(j+1)%n,n+(j+1)%n,n+j) for j in range(n)]+[tuple(reversed(range(n))),tuple(n+j for j in range(n))]
    return mesh(name,v,f,col,material,'C layout envelope only; stage D replaces this geometry')
def tyre(name,x,y,z,r,width):
    v=[];f=[];na=64;section=[(-width*.44,.51),(-width*.5,.74),(-width*.37,.97),(0,1),(width*.37,.97),(width*.5,.74),(width*.44,.51)]
    for dx,rr in section:
        for j in range(na):v.append((x+dx,y+r*rr*math.cos(j*2*math.pi/na),z+r*rr*math.sin(j*2*math.pi/na)))
    for i in range(len(section)):
        for j in range(na):f.append((i*na+j,i*na+(j+1)%na,((i+1)%len(section))*na+(j+1)%na,((i+1)%len(section))*na+j))
    return mesh(name,v,f,proxy,dark,'C tire envelope; profile/detail pending stage D')
for title,x,y,r in [('NOSE',0,1.45,.20),('MAIN_L',-1.02,-1.05,.245),('MAIN_R',1.02,-1.05,.245)]:
    z=-1.55+r
    tyre('ORION_GEAR_'+title+'_TIRE_ENVELOPE',x,y,z,r,.13 if title=='NOSE' else .16)
    cylinder('ORION_GEAR_'+title+'_HUB_ENVELOPE',(x-.05,y,z),(x+.05,y,z),r*.48,metal)
    top=(0,1.35,-.34) if title=='NOSE' else (math.copysign(.33,x),-.65,-.38)
    cylinder('ORION_GEAR_'+title+'_STRUT_ENVELOPE',top,(x,y,z+.10),.032 if title=='NOSE' else .026,metal)

# Sensor volume is deliberately a proxy, not a claimed detailed optical housing.
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(0,2.05,-.81))
o=bpy.context.object
for c in list(o.users_collection):c.objects.unlink(o)
proxy.objects.link(o);o.name='ORION_SENSOR_ENVELOPE_NOT_FINAL';o.scale=(.31,.285,.32);o.parent=root;o.data.materials.append(grey)
for p in o.data.polygons:p.use_smooth=True
o['evidence']='A visible location / C approximate volume';o['status']='No lens layout modeled; replace in stage D'
cylinder('ORION_SENSOR_MOUNT_ENVELOPE',(0,2.05,-.32),(0,2.05,-.61),.205,grey)

# Neutral presentation floor and three large lights; never export these.
floor=mesh('ORION_REVIEW_FLOOR',[(-100,-100,-1.551),(100,-100,-1.551),(100,100,-1.551),(-100,100,-1.551)],[(0,1,2,3)],studio,floor_mat,'Presentation only')
floor.parent=None;floor['status']='Presentation floor'
lighting=bpy.data.collections['50_CAMERAS_LIGHTS']
def light(name,loc,power,size,target=(0,0,0)):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);lighting.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('ORION_KEY',(2,6,10),2200,8)
light('ORION_FILL',(-8,0,5),1700,10)
light('ORION_REAR_LIGHT',(1,-8,7),1800,7)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.30,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
camlocs={'FRONT':((0,24,.05),(0,0,.05),19),'REAR':((0,-24,.05),(0,0,.05),19),
    'LEFT':((-24,0,.05),(0,0,.05),10),'RIGHT':((24,0,.05),(0,0,.05),10),
    'TOP':((0,0,30),(0,0,0),19),'UNDERSIDE':((0,0,-30),(0,0,0),19)}
for name,(loc,target,scale) in camlocs.items():
    cam=bpy.data.objects['ORION_CAM_'+name];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    if name=='TOP':cam.rotation_euler=(0,0,0)
persp=bpy.data.objects['ORION_CAM_R3_INITIAL'];persp.location=(5.2,7.6,-.04)
persp.rotation_euler=(Vector((0,2.15,-.48))-persp.location).to_track_quat('-Z','Y').to_euler();persp.data.lens=60
persp['match_status']='Provisional R3-like viewpoint; not a calibrated photographic camera'
d=bpy.data.cameras.new('ORION_CAM_HERO');hero=bpy.data.objects.new('ORION_CAM_HERO',d);lighting.objects.link(hero)
hero.location=(14,18,10);hero.rotation_euler=(-hero.location).to_track_quat('-Z','Y').to_euler();d.lens=45
s.camera=hero;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='OPTIX'
    s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.render.resolution_x=1800;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.render.filepath=str(ROOT/f'Previews/C_{REV}_Hero.png')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
station_report={'revision':REV,'body_stations_m':body_stations,'nose_stations_m':nose_stations,
    'station_status':'Visual approximations, not measured blueprint positions',
    'wing_span_m':16,'primary_extent_length_m':8,'nose_join_y_m':3.1,
    'gear_ground_z_m':-1.55,'sensor_center_m':[0,2.05,-.81],
    'gear_axles_m':[[0,1.45,-1.35],[-1.02,-1.05,-1.305],[1.02,-1.05,-1.305]],
    'control_splits_status':'Compatible structural interpretation; exact split positions C',
    'reference_camera_status':persp['match_status']}
(ROOT/f'Documentation/C_geometry_parameters_{REV}.json').write_text(json.dumps(station_report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Orion/Orion_Master.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(CHECKPOINT),copy=True)
print('STAGE_C_BUILT',CHECKPOINT)
