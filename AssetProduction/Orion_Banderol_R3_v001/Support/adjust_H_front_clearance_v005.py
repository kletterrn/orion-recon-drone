from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
sources=[P/'Orion/Orion_Master.blend',P/'Banderol/S8000_Banderol_Master.blend']
hashes={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL'];oi=bpy.data.objects['ORION_LINKED_APPROVED']
old=list(bi.location);bi.location.y=-1.75;bi.location.z=-1.07
for name in ['ORION_PAYLOAD_SOCKET_PROVISIONAL','BANDEROL_ATTACH_ROOT_PREVIEW']:
    bpy.data.objects[name].location.y=-1.75
    bpy.data.objects[name].location.z-=.12
for point in bpy.data.curves['ALIGNMENT_GUIDE_NOT_RACK'].splines[0].points:point.co.y=-1.75;point.co.z-=.12
bpy.context.view_layer.update()
def mesh(o,T):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    vs=[T@ev.matrix_world@v.co for v in m.vertices];faces=[tuple(p.vertices) for p in m.polygons];ev.to_mesh_clear()
    bb=[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)]
    return vs,faces,bb
def overlap(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
payload={}
for o in bi.instance_collection.all_objects:
    if o.type=='MESH' and not o.hide_render:
        v,f,bb=mesh(o,bi.matrix_world);payload[o.name]=(BVHTree.FromPolygons(v,f),bb)
groups=['ORION_GEAR','ORION_GEAR_BAYS','ORION_SENSOR_R3','ORION_AIRFRAME','ORION_WINGS','ORION_TAIL_REAR']
objects={o.name:o for n in groups for o in bpy.data.collections[n].all_objects if o.type=='MESH' and not o.hide_render}
moving={o.name for n in ['ORION_GEAR','ORION_GEAR_BAYS'] for o in bpy.data.collections[n].all_objects if o.type=='MESH' and not o.hide_render}
hits=[]
for frame in range(1,161):
    s.frame_set(frame)
    for n,o in objects.items():
        if frame>1 and n not in moving:continue
        v,f,bb=mesh(o,oi.matrix_world)
        candidates=[(pn,pt) for pn,(pt,pb) in payload.items() if overlap(bb,pb)]
        if not candidates:continue
        tree=BVHTree.FromPolygons(v,f)
        for pn,pt in candidates:
            pairs=tree.overlap(pt)
            if pairs:hits.append({'frame':frame,'orion':n,'banderol':pn,'pairs':len(pairs)})
    if frame%40==0:print('V005_CHECK',frame,flush=True)
default=[h for h in hits if h['frame']==1]
frontwing=[h for h in default if h['banderol'] in ['BDL_WING_L','BDL_WING_R']]
assert not frontwing,frontwing
assert not default,default
s.frame_set(1);s.camera=bpy.data.objects['H_SIDE']
s['revision']='H_front_clearance_v005';s['fit_status']='Front/main-wing intersections cleared in gear-down; see H_clearance_v005.json for complete sampled contacts'
s['nominal_alignment_metres']='BDL root (0,-1.75,-1.07), unchanged axes/scale; user-authorized visual adjustment'
for o in s.objects:
    if o.type=='FONT' and not o.library:
        o.data.body='VISUAL PLACEMENT REVIEW - FRONT WINGS CLEARED\nApproved shapes and scale preserved | exact carriage remains provisional'
        o.hide_render=o.parent!=s.camera
report={'previous_translation':old,'new_translation':list(bi.location),'source_dimensions_and_shapes':'unchanged','default_pose_contacts':default,'default_front_wing_contacts':frontwing,'sampled_frames':160,'all_sampled_contacts':hits,'evidence':'User-authorized artistic clearance adjustment; not an authenticated rack/station','limitations':'Surface intersection check only; sensor/control/propeller motion extremes not swept.'}
(P/'Documentation/H_clearance_v005.json').write_text(json.dumps(report,indent=2))
assert hashes=={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_H_front_clearance_v005.blend'),copy=True,relative_remap=True)
# Reopen the saved canonical file before the native review renders.
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
assert all(Path(bpy.path.abspath(l.filepath)).exists() for l in bpy.data.libraries)
assert abs(bpy.data.objects['BANDEROL_LINKED_PROVISIONAL'].location.y+1.75)<1e-5
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
for label,cam in [('Side','H_SIDE'),('FrontClearance','H_FORWARD_FIT'),('Underside','H_UNDERSIDE')]:
    s.camera=bpy.data.objects[cam]
    for o in s.objects:
        if o.type=='FONT' and not o.library:o.hide_render=o.parent!=s.camera
    s.render.filepath=str(P/f'Previews/H_v005_{label}.png');bpy.ops.render.render(write_still=True)
print('V005_COMPLETE',len(default),'default contacts;',len(hits),'sampled contacts',flush=True)

