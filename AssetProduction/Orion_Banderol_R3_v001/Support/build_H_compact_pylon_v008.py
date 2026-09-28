from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
sources=[P/'Orion/Orion_Master.blend',P/'Banderol/S8000_Banderol_Master.blend']
hashes={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
oldcol=bpy.data.collections['ASSEMBLY_VISUAL_SUPPORT_APPROXIMATION']
for o in list(oldcol.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(oldcol)
with bpy.data.libraries.load(str(P/'Banderol/S8000_Banderol_VisualFit_Master.blend'),link=True) as (src,dst):dst.collections=['BDL_ASSET_FIT']
bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL'];oi=bpy.data.objects['ORION_LINKED_APPROVED']
bi.instance_collection=dst.collections[0];bi.location=(0,-1.26,-.86)
bi['variant']='4.4 m artistic fit variant; original 5 m reference master preserved'
bi['evidence']='User-authorized visual size and alignment; not measured carrier configuration'
col=bpy.data.collections.new('ASSEMBLY_COMPACT_VISUAL_PYLON');s.collection.children.link(col)
root=bpy.data.objects.new('VISUAL_PYLON_ROOT',None);col.objects.link(root);root.parent=oi
root['evidence']='C: detailed exterior visual approximation, no functional release system'
for n,loc in [('ORION_PAYLOAD_SOCKET_PROVISIONAL',(0,-.20,-.40)),('BANDEROL_ATTACH_ROOT_PREVIEW',(0,-.20,-.61))]:bpy.data.objects[n].location=loc
def material(name,col,metal=0,rough=.5):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1)
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
paint=material('PYLON_SATIN_AIRFRAME_PAINT',(.27,.30,.33),.12,.44)
panel=material('PYLON_ACCESS_COVER_PAINT',(.24,.27,.29),.1,.48)
metal=material('PYLON_STAINLESS_FASTENER',(.30,.32,.34),.8,.3)
seal=material('PYLON_DARK_PANEL_SEAL',(.032,.037,.04),0,.7)
def geo(o,T=Matrix.Identity(4)):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();v=[T@ev.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];ev.to_mesh_clear()
    bb=[(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
    return v,f,bb
def tree(o,T=Matrix.Identity(4)):
    v,f,b=geo(o,T);return BVHTree.FromPolygons(v,f),b
def native(name,vs,fs,mat=paint,bevel=.002):
    m=bpy.data.meshes.new(name+'_MESH');m.from_pydata(vs,[],fs);m.update()
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    o=bpy.data.objects.new(name,m);col.objects.link(o);o.parent=root;m.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Controlled edge radius','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL')
    o['evidence']='C: exterior artistic approximation'
    return o
ft,_=tree(bpy.data.objects['ORION_FUSELAGE'],oi.matrix_world)
case=bpy.data.objects['BDLF_BODY'];ct,_=tree(case,bi.matrix_world)
def strip(name,ys,ws,target,start,direction,lo,hi,mat=paint):
    v=[]
    for y,w in zip(ys,ws):
        a=target.ray_cast(Vector((-w,y,start)),Vector((0,0,direction)))[0];b=target.ray_cast(Vector((w,y,start)),Vector((0,0,direction)))[0]
        assert a is not None and b is not None,(name,y,w)
        v.extend([(-w,y,a.z+lo),(w,y,b.z+lo),(w,y,b.z+hi),(-w,y,a.z+hi)])
    f=[(3,2,1,0)]+[(4*j+i,4*j+(i+1)%4,4*(j+1)+(i+1)%4,4*(j+1)+i) for j in range(len(ys)-1) for i in range(4)]
    f.append(tuple(4*(len(ys)-1)+i for i in range(4)))
    return native(name,v,f,mat)
upper=strip('PYLON_CONFORMING_UPPER_SADDLE',[-.465,-.435,-.30,-.16,-.12],[.028,.092,.092,.078,.025],ft,-2,1,-.024,.006)
lower=strip('PYLON_CURVED_LOWER_SHOE',[-.445,-.42,-.30,-.18,-.14],[.028,.08,.085,.075,.025],ct,0,-1,-.008,.027)
# Compact closed fairing with a swept leading end, rather than exposed long posts.
outline=[(-.43,-.677),(-.17,-.677),(-.10,-.437),(-.14,-.407),(-.40,-.407),(-.45,-.445)]
vs=[(x,y,z) for x in [-.052,.052] for y,z in outline];N=len(outline)
fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
housing=native('PYLON_STREAMLINED_OUTER_HOUSING',vs,fs,paint,.004)
def slab(name,x0,x1,shape,mat,bevel=.001):
    N=len(shape);v=[(x,y,z) for x in [x0,x1] for y,z in shape]
    f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return native(name,v,f,mat,bevel)
cover_shape=[(-.395,-.650),(-.20,-.650),(-.137,-.439),(-.395,-.439),(-.413,-.453)]
for sign in [-1,1]:
    slab(f'PYLON_COVER_SEAL_{sign}',sign*.0508,sign*.0532,cover_shape,seal,.001)
    inset=[(-.387,-.642),(-.206,-.642),(-.148,-.447),(-.387,-.447),(-.403,-.456)]
    slab(f'PYLON_REMOVABLE_SIDE_COVER_{sign}',sign*.0529,sign*.0557,inset,panel,.0018)
    for k,(y,z) in enumerate([(-.376,-.456),(-.376,-.633),(-.215,-.633),(-.160,-.456)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0045,depth=.0028,location=(sign*.0561,y,z),rotation=(0,math.pi/2,0))
        o=bpy.context.object;o.name=f'PYLON_RECESSED_COVER_FASTENER_{sign}_{k}'
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o);o.parent=root;o.data.materials.append(metal)
        b=o.modifiers.new('Head bevel','BEVEL');b.width=.0005;b.segments=2
        # Tiny visible socket mark; visual surface detail only.
        slot=[(y-.002,z-.0005),(y+.002,z-.0005),(y+.002,z+.0005),(y-.002,z+.0005)]
        slab(f'PYLON_FASTENER_SLOT_{sign}_{k}',sign*.0574,sign*.0578,slot,seal,.00015)
# Thin collars hide the interface seam while retaining distinct editable shells.
strip('PYLON_UPPER_INTERFACE_SEAL',[-.46,-.43,-.3,-.17,-.14],[.03,.08,.08,.065,.024],ft,-2,1,-.027,-.021,seal)
strip('PYLON_LOWER_CONTACT_SEAL',[-.44,-.41,-.3,-.19,-.15],[.025,.073,.075,.065,.025],ct,0,-1,.002,.008,seal)
bpy.context.view_layer.update()
payload={o.name:tree(o,bi.matrix_world) for o in bi.instance_collection.all_objects if o.type=='MESH' and not o.hide_render}
adapter={o.name:tree(o) for o in col.objects if o.type=='MESH'}
def overlaps(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
groups=['ORION_GEAR','ORION_GEAR_BAYS','ORION_SENSOR_R3','ORION_AIRFRAME','ORION_WINGS','ORION_TAIL_REAR','ORION_EXTERIOR_DETAILS_R3']
objects={o.name:o for n in groups for o in bpy.data.collections[n].all_objects if o.type=='MESH' and not o.hide_render}
moving={o.name for n in ['ORION_GEAR','ORION_GEAR_BAYS'] for o in bpy.data.collections[n].all_objects if o.type=='MESH' and not o.hide_render}
hits=[];interfaces=[]
for frame in range(1,161):
    s.frame_set(frame)
    for n,o in objects.items():
        if frame>1 and n not in moving:continue
        ot,ob=tree(o,oi.matrix_world)
        for pn,(pt,pb) in {**payload,**adapter}.items():
            if not overlaps(ob,pb):continue
            h=ot.overlap(pt)
            if h:
                record={'frame':frame,'orion':n,'assembly':pn,'pairs':len(h)}
                if n=='ORION_FUSELAGE' and pn in ['PYLON_CONFORMING_UPPER_SADDLE','PYLON_UPPER_INTERFACE_SEAL']:interfaces.append(record)
                else:hits.append(record)
    if frame%40==0:print('V008_CLEARANCE',frame,flush=True)
default=[h for h in hits if h['frame']==1]
(P/'Documentation/H_compact_diagnostic_v008.json').write_text(json.dumps({'default_contacts':default,'motion_contacts':hits},indent=2))
assert not default,default
s.frame_set(1)
contact=[]
for a,b,T in [('PYLON_CONFORMING_UPPER_SADDLE','ORION_FUSELAGE',oi.matrix_world),('PYLON_CURVED_LOWER_SHOE','BDLF_BODY',bi.matrix_world),('PYLON_STREAMLINED_OUTER_HOUSING','PYLON_CONFORMING_UPPER_SADDLE',Matrix.Identity(4)),('PYLON_STREAMLINED_OUTER_HOUSING','PYLON_CURVED_LOWER_SHOE',Matrix.Identity(4))]:
    at,_=tree(bpy.data.objects[a]);bt,_=tree(bpy.data.objects[b],T);ok=bool(at.overlap(bt));contact.append({'a':a,'b':b,'contact':ok});assert ok,(a,b)
ctrl=bpy.data.objects['ORION_CTRL_PROPELLER'];pivot=oi.matrix_world@ctrl.matrix_world.translation
rotor={o.name:geo(o,oi.matrix_world) for o in ctrl.children_recursive if o.type=='MESH' and not o.hide_render}
rotor_hits=[]
for deg in range(360):
    R=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'Y')@Matrix.Translation(-pivot)
    for n,(v,f,b) in rotor.items():
        vv=[R@p for p in v];bb=[(min(p[i] for p in vv),max(p[i] for p in vv)) for i in range(3)]
        candidates=[(pn,pt) for pn,(pt,pb) in {**payload,**adapter}.items() if overlaps(bb,pb)]
        if candidates:
            rt=BVHTree.FromPolygons(vv,f)
            for pn,pt in candidates:
                if rt.overlap(pt):rotor_hits.append({'degrees':deg,'rotor':n,'assembly':pn})
assert not rotor_hits
defects=[]
for o in col.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-13 for f in bm.faces) or bm.calc_volume()<=0:defects.append(o.name)
    bm.free()
assert not defects,defects
s['revision']='H_compact_pylon_v008';s['fit_status']='Default clear; complete rotor sweep clear; gear-motion report separate'
s['nominal_alignment_metres']='Visual-fit 4.4m Banderol (0,-1.26,-0.86); compact exterior pylon is C approximation'
for o in s.objects:
    if o.type=='FONT' and not o.library:o.data.body='COMPACT VISUAL-FIT REVIEW\n4.4 m artistic variant | detailed exterior pylon | full propeller sweep cleared'
def camera(name,loc,target,scale):
    if name in bpy.data.objects:o=bpy.data.objects[name]
    else:
        d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o)
    o.data.type='ORTHO';o.data.ortho_scale=scale;o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
camera('H_SUPPORT_CLOSEUP',(2.2,1,-1.35),(0,-.30,-.56),1.30)
camera('H_COMPACT_HERO',(9,12,4),(0,-.1,-.5),15)
camera('H_ROTOR_CLEARANCE',(3,-5.4,-1.4),(0,-3.45,-.52),2.6)
s.camera=bpy.data.objects['H_SIDE']
for o in s.objects:
    if o.type=='FONT' and not o.library:o.hide_render=o.parent!=s.camera
assert hashes=={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_H_compact_pylon_v008.blend'),copy=True,relative_remap=True)
report={'visual_fit_length_m':4.4,'translation':[0,-1.26,-.86],'source_master_hashes':hashes,'source_masters_unchanged':True,'default_unintended_contacts':default,'intentional_interface_checks':contact,'propeller_sweep_samples':360,'propeller_contacts':rotor_hits,'gear_motion_contacts':hits,'adapter_mesh_count':sum(o.type=='MESH' for o in col.objects),'adapter_base_defects':defects,'evidence':'C exterior artistic reconstruction; no functional release mechanism','visual_inspection':'pending'}
(P/'Documentation/H_compact_validation_v008.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
for label,cam in [('Side','H_SIDE'),('Hero','H_COMPACT_HERO'),('Pylon','H_SUPPORT_CLOSEUP'),('Underside','H_UNDERSIDE'),('RotorClearance','H_ROTOR_CLEARANCE')]:
    s.camera=bpy.data.objects[cam]
    for o in s.objects:
        if o.type=='FONT' and not o.library:o.hide_render=o.parent!=s.camera
    s.render.filepath=str(P/f'Previews/H_v008_{label}.png');bpy.ops.render.render(write_still=True)
print('V008_COMPLETE')

