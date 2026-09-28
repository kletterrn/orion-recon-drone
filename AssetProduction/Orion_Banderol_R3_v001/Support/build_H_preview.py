from pathlib import Path
import bpy, math, json, hashlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
sources=[P/'Orion/Orion_Master.blend',P/'Banderol/S8000_Banderol_Master.blend']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(P)):sha(p) for p in sources}
bpy.ops.wm.read_factory_settings(use_empty=True)

def link(path,name):
    with bpy.data.libraries.load(str(path),link=True) as (src,dst):
        assert name in src.collections
        dst.collections=[name]
    return dst.collections[0]
orion=link(sources[0],'ORION_ASSET'); bdl=link(sources[1],'BDL_ASSET')

def mat(name,col):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7
    return m
amber=mat('DIAGNOSTIC_AMBER_NOT_A_RACK',(1,.36,.035))
white=mat('REVIEW_LABEL_WHITE',(.82,.87,.92))
def instance(scene,coll,name,loc):
    o=bpy.data.objects.new(name,None);o.instance_type='COLLECTION';o.instance_collection=coll;o.location=loc
    scene.collection.objects.link(o);return o
def setup(s):
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
    s.cycles.device='GPU';s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
    s.world=bpy.data.worlds.new(s.name+'_WORLD');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.17,.21,1)
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
    s.view_settings.view_transform='AgX';s.frame_start=1;s.frame_end=160
    for name,loc,energy,size in [('KEY',(4,1,7),2000,7),('FILL',(-6,2,4),1500,6),('UNDER',(0,0,-5),700,5)]:
        d=bpy.data.lights.new(s.name+'_'+name,'AREA');d.energy=energy;d.shape='DISK';d.size=size
        o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc
        o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(s,name,loc,target,scale):
    d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;d.lens=50
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def caption(s,cam,text):
    d=bpy.data.curves.new(cam.name+'_LABEL','FONT');d.body=text;d.size=.017*cam.data.ortho_scale
    d.space_line=1.2;d.materials.append(white)
    o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.parent=cam
    o.location=(-.475*cam.data.ortho_scale,.26*cam.data.ortho_scale,-1)

diag=bpy.context.scene;diag.name='H_CARRIAGE_DIAGNOSTIC';setup(diag)
oi=instance(diag,orion,'ORION_LINKED_APPROVED',(0,0,0))
bi=instance(diag,bdl,'BANDEROL_LINKED_PROVISIONAL',(0,-.70,-.95))
bi['evidence']='C: diagnostic alignment only, not a verified carriage station'
bi['configuration']='Visible extended wings; actual carried wing configuration unknown'
diag['status']='PROVISIONAL FIT REVIEW; exact R3 carriage and rack unverified'
diag['nominal_alignment_metres']='BDL root (0,-0.70,-0.95), axes unchanged; not a physical interface'
diag['source_assets']='Independent linked approved masters; no geometry changes'
for name,loc in [('ORION_PAYLOAD_SOCKET_PROVISIONAL',(0,-.70,-.5)),('BANDEROL_ATTACH_ROOT_PREVIEW',(0,-.70,-.78))]:
    o=bpy.data.objects.new(name,None);diag.collection.objects.link(o);o.location=loc;o.empty_display_type='ARROWS';o.empty_display_size=.15
    o['status']='Alignment helper only. No engineering interface or station authenticity.'
# Renderable abstract guide, deliberately not a fabricated adapter.
d=bpy.data.curves.new('ALIGNMENT_GUIDE_NOT_RACK','CURVE');d.dimensions='3D';d.bevel_depth=.006
sp=d.splines.new('POLY');sp.points.add(1)
sp.points[0].co=(0,-.70,-.50,1);sp.points[1].co=(0,-.70,-.78,1)
o=bpy.data.objects.new(d.name,d);diag.collection.objects.link(o);d.materials.append(amber)
o['status']='Abstract amber alignment guide; not rack geometry'
cams={
 'Side':camera(diag,'H_SIDE',(10,0,-.25),(0,0,-.25),9.5),
 'Underside':camera(diag,'H_UNDERSIDE',(5,7,-6),(0,0,-.45),13),
 'Conflict':camera(diag,'H_FORWARD_FIT',(2.6,4.4,-1.8),(0,1.25,-.95),2.8),
 'Retracted':camera(diag,'H_RETRACTED',(10,0,-.25),(0,0,-.25),9.5),
}
for cam in cams.values():caption(diag,cam,'PROVISIONAL FIT REVIEW - NOT DOCUMENTED CARRIAGE\nApproved scale preserved | amber line = alignment guide, not rack')
diag.camera=cams['Side'];diag.frame_set(1)

scale=bpy.data.scenes.new('H_SEPARATE_SCALE_REVIEW');setup(scale)
instance(scale,orion,'ORION_SCALE_REFERENCE',(0,0,0))
instance(scale,bdl,'BANDEROL_SCALE_REFERENCE',(9.6,0,-.9))
sc= camera(scale,'H_SCALE_OVERVIEW',(15,17,11),(2.0,0,-.3),22)
scale.camera=sc;caption(scale,sc,'SEPARATE ASSET SCALE REVIEW\nOrion nominal 8 m / 16 m | Banderol 5 m body / 0.30 m case / provisional 2.20 m wing span')
scale.frame_set(1)

# Surface-intersection audit: evaluated meshes transformed by each collection instance.
bpy.context.window.scene=diag
def geo(o,T):
    dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);m=ev.to_mesh()
    pts=[T@ev.matrix_world@v.co for v in m.vertices];faces=[tuple(p.vertices) for p in m.polygons]
    ev.to_mesh_clear()
    bb=[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)] if pts else None
    return pts,faces,bb
def touches(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
diag.frame_set(1)
payload={}
for o in bdl.all_objects:
    if o.type=='MESH' and not o.hide_render:
        pts,faces,bb=geo(o,bi.matrix_world);payload[o.name]=(BVHTree.FromPolygons(pts,faces),bb)
audit_groups=['ORION_GEAR','ORION_GEAR_BAYS','ORION_SENSOR_R3','ORION_AIRFRAME','ORION_WINGS','ORION_TAIL_REAR']
objects={o.name:o for c in audit_groups for o in bpy.data.collections[c].all_objects if o.type=='MESH' and not o.hide_render}
moving={o.name for c in ['ORION_GEAR','ORION_GEAR_BAYS'] for o in bpy.data.collections[c].all_objects if o.type=='MESH' and not o.hide_render}
hits=[];static={};tests=0
for frame in range(1,161):
    diag.frame_set(frame)
    for n,o in objects.items():
        if frame>1 and n not in moving:continue
        pts,faces,bb=geo(o,oi.matrix_world)
        if not bb:continue
        possible=[(pn,t) for pn,(t,pb) in payload.items() if touches(bb,pb)]
        if not possible:continue
        t=BVHTree.FromPolygons(pts,faces)
        for pn,pt in possible:
            tests+=1;pairs=t.overlap(pt)
            if pairs:hits.append({'frame':frame,'orion':n,'banderol':pn,'triangle_pairs':len(pairs)})
    if frame%20==0:print('H_CLEARANCE_PROGRESS',frame,flush=True)
diag.frame_set(1)
report={'alignment':list(bi.location),'alignment_evidence':'C, diagnostic only; no station or rack established','wing_pose':'Visible extended wings only; no documented carriage/stowed pose','frames_sampled':160,'groups_sampled':audit_groups,'surface_triangle_tests':tests,'surface_intersections':hits,'limitations':['Surface intersections are not a signed-volume or distance guarantee.','No exact rack/station, carried wing pose or R3 sensor compatibility established.','Sensor and control surfaces left in approved neutral pose; no combined extremes swept.','Source-only propeller pose audit remains separate; no assembly propeller sweep.'],'authenticated_carriage':'BLOCKED BY EVIDENCE','fit_status':'FAILED' if hits else 'No sampled surface intersections; authenticity unresolved'}
(P/'Documentation/H_clearance_v001.json').write_text(json.dumps(report,indent=2))
diag['fit_status']=report['fit_status']
bpy.context.window.scene=diag;diag.camera=cams['Side'];diag.frame_set(1)
(P/'Assembly/checkpoints').mkdir(parents=True,exist_ok=True)
out=P/'Assembly/Orion_Banderol_Preview.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath))
bpy.ops.wm.save_as_mainfile(filepath=str(out))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_H_preview_v001.blend'),copy=True,relative_remap=True)
assert before=={str(p.relative_to(P)):sha(p) for p in sources}
(P/'Documentation/H_source_preservation_v001.json').write_text(json.dumps(before,indent=2))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
for label in ['Side','Underside','Conflict','Retracted']:
    bpy.context.window.scene=diag;diag.camera=cams[label];diag.frame_set(120 if label=='Retracted' else 1)
    diag.render.filepath=str(P/f'Previews/H_v001_{label}.png');bpy.ops.render.render(write_still=True)
bpy.context.window.scene=scale;scale.render.filepath=str(P/'Previews/H_v001_Scale.png');bpy.ops.render.render(write_still=True)
print('H_BUILD_COMPLETE',report['fit_status'],len(hits),'surface contacts; masters unchanged',flush=True)
