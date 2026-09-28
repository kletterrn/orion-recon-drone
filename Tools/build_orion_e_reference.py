"""Build a reference-led, editable Orion-E exterior in Blender 5.2.

Coordinates: Blender X right, Y nose-forward, Z up; metres. This is an
independent art source, not a replacement for the current Enfusion prefab.
"""
import math
from pathlib import Path
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1] / 'Assets' / 'ORD' / 'Models' / 'OrionE_Reference'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

def collection(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); return c
air=collection('01 Airframe'); moving=collection('02 Movable parts'); gear=collection('03 Landing gear'); detail=collection('04 Details'); guides=collection('05 Export notes')

def mat(name, rgb, rough=.55, metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*rgb,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
grey=mat('Airframe - warm graphite grey',(.29,.32,.34),.57)
white=mat('Nose fairing - warm white',(.78,.79,.76),.48)
edge=mat('Panel seal - subtle dark grey',(.20,.23,.24),.67)
rubber=mat('Tyre - charcoal rubber',(.027,.031,.033),.83)
metal=mat('Gear - satin aluminium',(.43,.46,.48),.38,.65)
glass=mat('Optics - dark blue glass',(.014,.045,.063),.16,.2)
black=mat('Propeller - charcoal composite',(.045,.05,.053),.43)
light=mat('Navigation lamp',(.68,.12,.07),.27)

def place(obj,name,coll,material,pivot=None):
    obj.name=name
    if obj.type=='MESH': obj.data.name=name
    coll.objects.link(obj)
    for c in list(obj.users_collection):
        if c != coll: c.objects.unlink(obj)
    if material: obj.data.materials.append(material)
    if pivot is not None:
        # Mesh coordinates remain fixed in world space when the origin moves.
        delta=Vector(pivot)-obj.location
        obj.data.transform(__import__('mathutils').Matrix.Translation(-delta))
        obj.location=Vector(pivot)
    if obj.type=='MESH':
        for p in obj.data.polygons: p.use_smooth=True
    return obj

def mesh(name, verts, faces, coll, material, pivot=None):
    d=bpy.data.meshes.new(name); d.from_pydata(verts,[],faces); d.update()
    o=bpy.data.objects.new(name,d); coll.objects.link(o)
    if material:d.materials.append(material)
    if pivot is not None:
        d.transform(__import__('mathutils').Matrix.Translation(Vector(pivot)*-1));o.location=pivot
    for p in d.polygons:p.use_smooth=True
    return o

def loft(name,stations,coll,material,sides=32):
    # station: (y, halfwidth, top height, bottom height)
    vs=[]
    for y,w,t,b in stations:
        mid=(t+b)/2; h=(t-b)/2
        for j in range(sides):
            a=2*math.pi*j/sides
            x=w*math.cos(a); z=mid+h*math.sin(a)
            # A flatter underside than upper contour.
            if math.sin(a)<0:z=mid+h*(.72*math.sin(a)-.28)
            vs.append((x,y,z))
    fs=[]
    for i in range(len(stations)-1):
        for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    fs.extend([tuple(reversed(range(sides))),tuple((len(stations)-1)*sides+j for j in range(sides))])
    return mesh(name,vs,fs,coll,material)

def uvball(name,loc,scale,coll,material,segments=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=16,location=loc)
    o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return place(o,name,coll,material)

def cylinder(name,a,b,r,coll,material,vertices=16):
    a,b=Vector(a),Vector(b);v=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=v.length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
    return place(o,name,coll,material,pivot=a)

def box(name,loc,dims,coll,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return place(o,name,coll,material)

def wing_section(name,side,root,tip,material,coll,pivot=None):
    # 6-point airfoil rings, finite trailing edge; root/tip = (x, front, rear, z, thickness)
    vs=[]
    for x,front,rear,z,t in (root,tip):
        x*=side;c=front-rear
        vs += [(x,front,z-.11*t),(x,front-.28*c,z+.50*t),(x,front-.68*c,z+.28*t),
               (x,rear,z+.035*t),(x,rear,z-.035*t),(x,front-.48*c,z-.46*t)]
    fs=[(0,1,2,3,4,5),(6,11,10,9,8,7)]
    fs += [(j,(j+1)%6,(j+1)%6+6,j+6) for j in range(6)]
    return mesh(name,vs,fs,coll,material,pivot)

# Nose is +Y. Tail propeller is -Y. The visible fuselage is just under 8 m.
loft('Fuselage - continuous shaped shell',[
    (-3.82,.19,.47,.10),(-3.45,.28,.57,.05),(-2.9,.38,.65,.00),(-2.0,.45,.70,-.03),
    (-.7,.49,.72,-.10),(.7,.48,.71,-.11),(1.8,.44,.67,-.08),(2.65,.39,.61,-.03),
    (2.98,.37,.57,.00)],air,grey)
loft('White forward nose fairing',[(2.96,.372,.57,.00),(3.25,.39,.58,.00),(3.52,.36,.55,.03),
    (3.76,.27,.48,.09),(3.94,.12,.39,.18),(3.99,.012,.31,.27)],air,white)
# Thin crescent at the joint gives a controllable material boundary.
cylinder('Nose joint seal', (0,2.975,.29),(0,2.982,.29),.345,detail,edge,32)

for s,label in [(-1,'L'),(1,'R')]:
    wing_section('Wing inner '+label,s,(.38,1.28,-.81,.33,.25),(2.55,.99,-.73,.37,.18),grey,air)
    wing_section('Wing outer '+label,s,(2.55,.99,-.73,.37,.18),(7.88,.31,-.45,.43,.075),grey,air)
    uvball('Rounded wing tip '+label,(s*7.9,-.07,.43),(.12,.40,.045),air,grey,24)
    # Separate aileron, with its origin on its leading hinge line.
    wing_section('Aileron '+label,s,(4.8,-.44,-.73,.39,.065),(7.5,-.22,-.46,.43,.045),grey,moving,(s*4.8,-.44,.39))
    # Tail fin is a slab swept rearward, canted upward and outward.
    rootA=(s*.22,-2.78,.42);rootB=(s*.22,-3.55,.40)
    tipA=(s*1.13,-3.24,1.96);tipB=(s*1.16,-3.88,1.90)
    thickness=.045
    vs=[(x+s*thickness,y,z) for x,y,z in (rootA,rootB,tipB,tipA)]+[(x-s*thickness,y,z) for x,y,z in (rootA,rootB,tipB,tipA)]
    fs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    mesh('Upright V-tail fixed '+label,vs,fs,air,grey)
    va=(s*.23,-3.55,.40);vb=(s*1.16,-3.88,1.90);vc=(s*1.08,-4.01,1.88);vd=(s*.23,-3.68,.39)
    vs=[(x+s*.035,y,z) for x,y,z in (va,vb,vc,vd)]+[(x-s*.035,y,z) for x,y,z in (va,vb,vc,vd)]
    mesh('Ruddervator '+label,vs,fs,moving,grey,va)
    uvball('Wing navigation light '+label,(s*7.94,.18,.44),(.055,.09,.03),detail,light if s<0 else white,16)

# Rear pusher, two separate stationary blades per the side references.
cylinder('Engine aft cowl',(0,-3.62,.36),(0,-3.90,.36),.24,air,grey,32)
cylinder('Propeller hub',(0,-3.91,.36),(0,-4.02,.36),.13,moving,black,32)
uvball('Propeller spinner',(0,-4.04,.36),(.13,.14,.13),moving,grey,24)
for idx,sign in enumerate((-1,1)):
    # Elliptical, slightly swept blade with finite thickness and a narrow root.
    stations=[(.12,.11,.08),(.34,.16,.12),(.67,.20,.12),(.97,.17,.09),(1.19,.08,.05),(1.24,.02,.02)]
    vs=[]
    for radius,chord,thick in stations:
        z=.36+sign*radius;y=-4.00-.07*radius
        vs.extend([(-chord/2,y-thick/2,z),(chord/2,y-thick/2,z),(chord/2,y+thick/2,z),(-chord/2,y+thick/2,z)])
    fs=[]
    for k in range(len(stations)-1):
        for j in range(4):fs.append((4*k+j,4*k+(j+1)%4,4*(k+1)+(j+1)%4,4*(k+1)+j))
    fs.extend([(0,3,2,1),tuple(range(4*(len(stations)-1),4*len(stations)))])
    mesh('Propeller blade '+str(idx+1),vs,fs,moving,black,(0,-3.98,.36))

# EO/IR turret beneath central forward fuselage. Window geometry is editable.
cylinder('Sensor yaw mount',(0,1.92,-.12),(0,1.92,-.38),.15,moving,metal,24)
uvball('Sensor gimbal outer',(0,1.92,-.50),(.28,.29,.24),moving,grey,32)
uvball('Sensor gimbal rotating ball',(0,1.92,-.56),(.255,.27,.24),moving,white,32)
uvball('Sensor primary optical window',(0,1.675,-.58),(.125,.025,.115),moving,glass,24)
uvball('Sensor secondary optical window',(.135,1.70,-.49),(.067,.025,.058),moving,glass,20)

# Landing gear: three independent wheel units, hubs and connected struts.
for label,x,y,upper,bottom,r in [('Nose',0,2.32,-.08,-.84,.16),('Main L',-.77,-.73,-.10,-.88,.22),('Main R',.77,-.73,-.10,-.88,.22)]:
    wheel_center=(x,y,bottom)
    cylinder('Gear oleo '+label,(x,y,upper),(x,y,bottom+.13),.044,gear,metal)
    cylinder('Gear sliding rod '+label,(x,y,bottom+.34),(x,y,bottom+.08),.029,gear,metal)
    side=1 if x>=0 else -1
    if label!='Nose':
        cylinder('Gear drag brace '+label,(x*.64,y-.24,-.12),(x,y,bottom+.34),.023,gear,metal)
        cylinder('Gear fork '+label,(x,y,bottom+.19),(x+side*.075,y,bottom),.03,gear,metal)
    else:cylinder('Nose steering fork',(0,y,bottom+.16),(.065,y,bottom),.025,gear,metal)
    cylinder('Wheel tyre '+label,(x-.065,y,bottom),(x+.065,y,bottom),r,gear,rubber,32)
    for side2 in (-1,1):
        cylinder('Wheel hub '+label+' '+str(side2),(x+side2*.068,y,bottom),(x+side2*.074,y,bottom),r*.47,gear,metal,24)
        cylinder('Axle cap '+label+' '+str(side2),(x+side2*.077,y,bottom),(x+side2*.083,y,bottom),r*.16,gear,edge,20)

# Only clear reference-supported surface details; marks remain optional decals.
for s,label in [(-1,'L'),(1,'R')]:
    box('Wing root underside fairing '+label,(s*.64,-.25,-.04),(.32,1.0,.10),detail,grey)
    box('Gear bay lip '+label,(s*.65,-.73,-.10),(.27,.69,.015),detail,edge)
uvball('Dorsal fairing',(0,.85,.72),(.22,.62,.14),detail,grey,24)
box('Small dorsal antenna',(0,-.55,.77),(.022,.17,.14),detail,grey)
box('Vent left',(-.39,-2.72,.43),(.012,.27,.045),detail,edge)
box('Vent right',(.39,-2.72,.43),(.012,.27,.045),detail,edge)

# UVs are generated for each mesh; source materials remain editable PBR nodes.
for o in scene.objects:
    if o.type!='MESH':continue
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    for other in scene.objects:
        if other!=o:other.select_set(False)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=.015)
    bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)

# Blender-native axis notation and reference assumptions accompany the asset.
note=bpy.data.objects.new('READ ME - X right Y nose-forward Z up; 1 unit = 1 m',None);guides.objects.link(note)
note.empty_display_type='PLAIN_AXES';note.empty_display_size=.3
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.world=bpy.data.worlds.new('Neutral studio world')
scene.world.color=(.55,.55,.55)
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'

def target_camera(name,where,target=(0,0,.2),ortho=18):
    bpy.ops.object.camera_add(location=where);cam=bpy.context.object;cam.name='Inspection '+name
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=ortho;scene.camera=cam
    return cam

for loc,power,size in [((7,3,10),1800,7),((-6,-3,7),1150,6),((0,-6,3),600,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc);bpy.context.object.data.energy=power;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size

# Save a clean editable source, with lighting/cameras in their own render setup.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'OrionE_reference_source.blend'))
for name,pos,scale in [('front',(0,11,1),17),('side',(12,0,1),11),('rear',(0,-11,1),17),('top',(0,0,15),17),('three_quarter',(11,10,6),17)]:
    target_camera(name,pos,ortho=scale)
    scene.render.filepath=str(OUT/('inspect_'+name+'.png'))
    bpy.ops.render.render(write_still=True)

# Only mesh objects enter interchange exports. The current mod .xob remains intact.
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
    if o.type=='MESH' and any(c in (air,moving,gear,detail) for c in o.users_collection):o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'OrionE_reference_clean.fbx'),use_selection=True,apply_unit_scale=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
try:
    bpy.ops.export_scene.gltf(filepath=str(OUT/'OrionE_reference_clean.glb'),export_format='GLB',use_selection=True)
except Exception as e:print('GLB export warning:',e)
print('DONE',OUT)
