from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
files=[P/'Orion/Orion_Master.blend',P/'Banderol/S8000_Banderol_Master.blend']
hashes={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL'];oi=bpy.data.objects['ORION_LINKED_APPROVED'];old=list(bi.location)
bi.location.z=-1.22
for n in ['ORION_PAYLOAD_SOCKET_PROVISIONAL','BANDEROL_ATTACH_ROOT_PREVIEW']:bpy.data.objects[n].location.z-=.15
bpy.data.objects['ALIGNMENT_GUIDE_NOT_RACK'].hide_render=True
bpy.data.objects['ALIGNMENT_GUIDE_NOT_RACK'].hide_viewport=True
bpy.context.view_layer.update()
col=bpy.data.collections.new('ASSEMBLY_VISUAL_SUPPORT_APPROXIMATION');s.collection.children.link(col)
root=bpy.data.objects.new('VISUAL_ADAPTER_ROOT',None);col.objects.link(root)
root['evidence']='C: user-requested exterior visual support; exact rack undetermined'
root['scope']='Nonfunctional presentation geometry; no release, load or engineering interface claim'
def material(name,color,metal,rough):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
paint=material('ADAPTER_GREY_PAINT',(.20,.24,.27),.15,.48)
edge=material('ADAPTER_EDGE_METAL',(.26,.29,.32),.65,.32)
def geometry(o,T=Matrix.Identity(4)):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();v=[T@ev.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];ev.to_mesh_clear()
    bb=[(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
    return v,f,bb
def tree(o,T=Matrix.Identity(4)):
    v,f,bb=geometry(o,T);return BVHTree.FromPolygons(v,f),bb
ft,_=tree(bpy.data.objects['ORION_FUSELAGE'],oi.matrix_world)
bt,_=tree(bpy.data.objects['BDL_BODY'],bi.matrix_world)
def native(name,vs,fs,mat=paint,bevel=.004):
    me=bpy.data.meshes.new(name+'_MESH');me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=root;me.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Restrained edge radius','BEVEL');mod.width=bevel;mod.segments=3
        mod=o.modifiers.new('Surface normals','WEIGHTED_NORMAL')
    o['evidence']='C: visual approximation, not a documented rack'
    return o
def strip(name,ys,widths,target,from_z,direction,low_offset,high_offset):
    vs=[]
    for y,w in zip(ys,widths):
        zl=target.ray_cast(Vector((-w,y,from_z)),Vector((0,0,direction)))[0]
        zr=target.ray_cast(Vector((w,y,from_z)),Vector((0,0,direction)))[0]
        assert zl is not None and zr is not None
        vs.extend([(-w,y,zl.z+low_offset),(w,y,zr.z+low_offset),(w,y,zr.z+high_offset),(-w,y,zl.z+high_offset)])
    fs=[(3,2,1,0)]
    for j in range(len(ys)-1):
        for i in range(4):fs.append((4*j+i,4*j+(i+1)%4,4*(j+1)+(i+1)%4,4*(j+1)+i))
    fs.append(tuple(4*(len(ys)-1)+i for i in range(4)))
    return native(name,vs,fs)
upper=strip('ADAPTER_UPPER_CONFORMING_SADDLE',[-3.25,-3.16,-2.85,-2.56,-2.48],[.04,.105,.105,.105,.04],ft,-2,1,-.033,.008)
lower=strip('ADAPTER_LOWER_CONTACT_SHOE',[-3.23,-3.14,-2.85,-2.57,-2.49],[.04,.10,.10,.10,.04],bt,0,-1,-.009,.032)
for name,y in [('AFT',-3.08),('FORWARD',-2.65)]:
    top=ft.ray_cast(Vector((0,y,-2)),Vector((0,0,1)))[0].z-.027
    bottom=bt.ray_cast(Vector((0,y,0)),Vector((0,0,-1)))[0].z+.024
    # Closed tapered exterior cheek; no concealed mechanical assembly.
    outline=[(y-.06,bottom-.009),(y+.06,bottom-.009),(y+.075,top+.008),(y-.075,top+.008)]
    vs=[(x,yy,z) for x in [-.062,.062] for yy,z in outline]
    fs=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
    native('ADAPTER_'+name+'_SUPPORT',vs,fs)
# Subtle visible cover screws, exterior detail only.
for y in [-3.08,-2.65]:
    for x in [-.063,.063]:
        z=-.62;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.012,depth=.006,location=(x,y,z),rotation=(0,math.pi/2,0))
        o=bpy.context.object;o.name=f'ADAPTER_COVER_FASTENER_{y}_{x}'
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o);o.parent=root;o.data.materials.append(edge);o['evidence']='C: restrained visual completion'

def overlaps(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
payload={o.name:tree(o,bi.matrix_world) for o in bi.instance_collection.all_objects if o.type=='MESH' and not o.hide_render}
adapter={o.name:tree(o) for o in col.objects if o.type=='MESH'}
# Prove conservative exclusion from the rotor's complete radial envelope where possible.
ctrl=bpy.data.objects['ORION_CTRL_PROPELLER'];pivot=oi.matrix_world@ctrl.matrix_world.translation
rotating=[o for o in ctrl.children_recursive if o.type=='MESH' and not o.hide_render]
assert {'ORION_PROPELLER_BLADE_A','ORION_PROPELLER_BLADE_B'}.issubset({o.name for o in rotating})
rotor={o.name:geometry(o,oi.matrix_world) for o in rotating}
rv=[v for vs,fs,bb in rotor.values() for v in vs];radius=max(math.hypot(v.x-pivot.x,v.z-pivot.z) for v in rv)
slab=(min(v.y for v in rv),max(v.y for v in rv));envelope=[]
for n,(t,bb) in {**payload,**adapter}.items():
    if bb[1][1]<slab[0] or bb[1][0]>slab[1]:continue
    dx=max(bb[0][0]-pivot.x,0,pivot.x-bb[0][1]);dz=max(bb[2][0]-pivot.z,0,pivot.z-bb[2][1]);gap=math.hypot(dx,dz)-radius
    envelope.append({'object':n,'conservative_radial_gap_m':gap})
rotor_hits=[]
for deg in range(360):
    R=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'Y')@Matrix.Translation(-pivot)
    for n,(vs,fs,bb) in rotor.items():
        v=[R@p for p in vs];rb=[(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
        candidates=[(pn,pt) for pn,(pt,pb) in {**payload,**adapter}.items() if overlaps(rb,pb)]
        if candidates:
            rt=BVHTree.FromPolygons(v,fs)
            for pn,pt in candidates:
                if rt.overlap(pt):rotor_hits.append({'degrees':deg,'rotor':n,'obstacle':pn})
assert not rotor_hits,rotor_hits
assert all(e['conservative_radial_gap_m']>0 for e in envelope),envelope
# Ground pose and all illustrative gear frames. Mount-contact overlaps are intentional.
groups=['ORION_GEAR','ORION_GEAR_BAYS','ORION_SENSOR_R3','ORION_AIRFRAME','ORION_WINGS','ORION_TAIL_REAR','ORION_EXTERIOR_DETAILS_R3']
obs={o.name:o for n in groups for o in bpy.data.collections[n].all_objects if o.type=='MESH' and not o.hide_render}
moving={o.name for n in ['ORION_GEAR','ORION_GEAR_BAYS'] for o in bpy.data.collections[n].all_objects if o.type=='MESH' and not o.hide_render}
hits=[];contacts=[]
for frame in range(1,161):
    s.frame_set(frame)
    for n,o in obs.items():
        if frame>1 and n not in moving:continue
        ot,ob=tree(o,oi.matrix_world)
        for pn,(pt,pb) in {**payload,**adapter}.items():
            if not overlaps(ob,pb):continue
            pairs=ot.overlap(pt)
            if not pairs:continue
            record={'frame':frame,'orion':n,'assembly':pn,'pairs':len(pairs)}
            if n=='ORION_FUSELAGE' and pn=='ADAPTER_UPPER_CONFORMING_SADDLE':contacts.append(record)
            else:hits.append(record)
    if frame%40==0:print('V006_GEAR_CHECK',frame,flush=True)
default=[h for h in hits if h['frame']==1];assert not default,default
contact_checks=[]
for a,b,T in [('ADAPTER_UPPER_CONFORMING_SADDLE','ORION_FUSELAGE',oi.matrix_world),('ADAPTER_LOWER_CONTACT_SHOE','BDL_BODY',bi.matrix_world)]:
    at,_=tree(bpy.data.objects[a]);bt2,_=tree(bpy.data.objects[b],T);ok=bool(at.overlap(bt2));contact_checks.append({'a':a,'b':b,'intentional_contact':ok});assert ok
for n in ['ADAPTER_AFT_SUPPORT','ADAPTER_FORWARD_SUPPORT']:
    for rail in [upper,lower]:
        nt,_=tree(bpy.data.objects[n]);rt,_=tree(rail);ok=bool(nt.overlap(rt));contact_checks.append({'a':n,'b':rail.name,'intentional_contact':ok});assert ok
defects=[]
for o in col.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-12 for f in bm.faces) or bm.calc_volume()<=0:defects.append(o.name)
    bm.free()
assert not defects
s.frame_set(1);s.camera=bpy.data.objects['H_SIDE']
s['revision']='H_support_v006';s['fit_status']='Default pose clear; full propeller envelope clear. Illustrative gear-motion conflicts remain.'
s['nominal_alignment_metres']='Banderol (0,-1.75,-1.22); visual adapter C; approved source dimensions unchanged'
for o in s.objects:
    if o.type=='FONT' and not o.library:
        o.data.body='VISUAL SUPPORT REVIEW - PROPELLER SWEEP CLEARED\nEditable approximate adapter | approved asset shapes and scale preserved';o.hide_render=o.parent!=s.camera
def camera(name,loc,target,scale):
    d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
camera('H_SUPPORT_CLOSEUP',(2.8,-4.,-1.65),(0,-2.85,-.76),2.3)
camera('H_ROTOR_CLEARANCE',(3,-5.4,-1.4),(0,-3.7,-.55),2.6)
report={'translation_before':old,'translation_after':list(bi.location),'rotor_pivot_m':list(pivot),'rotating_objects':[o.name for o in rotating],'full_sweep_samples_degrees':360,'rotor_surface_contacts':rotor_hits,'conservative_rotor_radius_m':radius,'conservative_swept_envelope_checks':envelope,'default_pose_unintended_contacts':default,'intentional_mount_contacts':contacts,'adapter_connected_surface_checks':contact_checks,'adapter_base_mesh_defects':defects,'gear_frames_sampled':160,'remaining_illustrative_gear_motion_contacts':hits,'adapter_evidence':'C, visual exterior approximation only','source_hashes':hashes,'engine_validation':'NOT ATTEMPTED','visual_inspection':'pending'}
(P/'Documentation/H_support_validation_v006.json').write_text(json.dumps(report,indent=2))
assert hashes=={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_H_support_v006.blend'),copy=True,relative_remap=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
for label,cam in [('Side','H_SIDE'),('Underside','H_UNDERSIDE'),('Support','H_SUPPORT_CLOSEUP'),('RotorClearance','H_ROTOR_CLEARANCE')]:
    s.camera=bpy.data.objects[cam]
    for o in s.objects:
        if o.type=='FONT' and not o.library:o.hide_render=o.parent!=s.camera
    s.render.filepath=str(P/f'Previews/H_v006_{label}.png');bpy.ops.render.render(write_still=True)
print('V006_COMPLETE; rotor contacts',len(rotor_hits),'default contacts',len(default),'source hashes unchanged',flush=True)
