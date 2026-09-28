from pathlib import Path
import bpy,json,math
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8'
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v012.blend'))
for lib in bpy.data.libraries:
 if 'Orion_RC8_Motion_v012' in lib.filepath:lib.filepath=str(I/'Blender/Orion_RC8_Motion_v017.blend')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v017.blend'),relative_remap=True);bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v017.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s
oi=bpy.data.objects['ORION_LINKED_APPROVED'];bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL']
with bpy.data.libraries.load(str(I/'Blender/Banderol_RC8_Motion_v004.blend'),link=False) as (a,b):b.collections=['BDL_ASSET_FIT']
bdl=b.collections[0];bi.instance_collection=bdl
root=next(o for o in bdl.all_objects if o.name.startswith('BANDEROL_VISUALFIT_ROOT'))
def tree(o,T=Matrix.Identity(4)):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();M=T@e.matrix_world
 v=[M@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear()
 return BVHTree.FromPolygons(v,f),[(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
def overlap(a,b):return all(a[1][i][1]>=b[1][i][0] and b[1][i][1]>=a[1][i][0] for i in range(3)) and bool(a[0].overlap(b[0]))
def visible(o):return o.type in {'MESH','CURVE'} and not o.hide_render
moving=[o for o in bpy.data.collections['ORION_GEAR'].all_objects if visible(o)]
doors=[o for o in bpy.data.collections['ORION_GEAR_BAYS'].all_objects if visible(o) and 'DOOR_' in o.name]
fixed=[o for col in ['ORION_AIRFRAME','ORION_GEAR_BAYS','ORION_WINGS','ORION_TAIL_REAR'] for o in bpy.data.collections[col].all_objects if visible(o) and 'DOOR_' not in o.name]
fixed=list({o.name:o for o in fixed}.values())
s.frame_set(1);static={o.name:tree(o,oi.matrix_world) for o in fixed}
static.update({o.name:tree(o) for o in bpy.data.collections['ASSEMBLY_COMPACT_VISUAL_PYLON'].all_objects if visible(o)})
hits=[];interfaces={};frames=[1+i*.5 for i in range(479)]
for deployment in [0,1]:
 root['deployment']=float(deployment);root.update_tag();bpy.context.view_layer.update()
 payload={o.name:tree(o,bi.matrix_world) for o in bdl.all_objects if visible(o)}
 for fi,frame in enumerate(frames):
  s.frame_set(int(frame),subframe=frame%1);dyn={o.name:tree(o,oi.matrix_world) for o in moving+doors}
  for n,a in dyn.items():
   for sn,b in (static|payload).items():
    if not overlap(a,b):continue
    # Pins, bearings and their mounting ears intentionally intersect at their fixed or moving seat.
    joint=('ATTACHMENT_' in sn or ('DOOR_HINGE_' in n and ('EAR_' in n or 'BARREL_' in n) and ('FUSELAGE' in sn or 'OPENING_LIP' in sn or 'BAY_SIDE' in sn)))
    if joint:interfaces[(n,sn)]=interfaces.get((n,sn),0)+1
    else:hits.append(dict(deployment=deployment,frame=frame,moving=n,obstacle=sn))
   if 'DOOR_' not in n:
    for door in doors:
     if overlap(a,dyn[door.name]):hits.append(dict(deployment=deployment,frame=frame,moving=n,obstacle=door.name))
  # Cross-assembly contacts: same-assembly tire/hub/strut overlaps are designed joints.
  for group1,group2 in [('MAIN_L','MAIN_R'),('NOSE','MAIN_L'),('NOSE','MAIN_R')]:
   for n,a in dyn.items():
    if group1 not in n:continue
    for sn,b in dyn.items():
     if group2 in sn and overlap(a,b):hits.append(dict(deployment=deployment,frame=frame,moving=n,obstacle=sn))
  if fi%80==0:print('FULL_MOTION',deployment,frame,len(hits),flush=True)
 report=dict(status='sampled mesh-surface checks; not continuous collision proof',frames=frames,payload_states=['folded','deployed'],unexpected_contacts=hits,bearing_interfaces=[dict(a=a,b=b,samples=n) for (a,b),n in interfaces.items()])
 (I/'Reports/motion_full_v017.json').write_text(json.dumps(report,indent=2))
print('FULL_MOTION_COMPLETE',len(hits),flush=True)


