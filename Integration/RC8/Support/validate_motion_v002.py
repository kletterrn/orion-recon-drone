from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';rev=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v002';out=I/f'Blender/Assembly_RC8_Motion_{rev}.blend'
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v001.blend'))
for lib in bpy.data.libraries:
 if 'Orion_RC8_Motion_v001' in lib.filepath:lib.filepath=str(I/f'Blender/Orion_RC8_Motion_{rev}.blend')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),relative_remap=True)
bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
oi=bpy.data.objects['ORION_LINKED_APPROVED'];bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL']
def tree(o,T=Matrix.Identity(4)):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();M=T@e.matrix_world
 v=[M@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear()
 return BVHTree.FromPolygons(v,f),[(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
def broad(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
static={}
for col in ['ORION_AIRFRAME','ORION_GEAR_BAYS','ORION_WINGS','ORION_TAIL_REAR']:
 for o in bpy.data.collections[col].all_objects:
  if o.type not in {'MESH','CURVE'} or o.hide_render or 'DOOR_' in o.name:continue
  static[o.name]=tree(o,oi.matrix_world)
for o in bi.instance_collection.all_objects:
 if o.type=='MESH' and not o.hide_render:static[o.name]=tree(o,bi.matrix_world)
for o in bpy.data.collections['ASSEMBLY_COMPACT_VISUAL_PYLON'].all_objects:
 if o.type=='MESH' and not o.hide_render:static[o.name]=tree(o)
moving=[o for o in bpy.data.collections['ORION_GEAR'].all_objects if o.type in {'MESH','CURVE'} and not o.hide_render]
doors=[o for o in bpy.data.collections['ORION_GEAR_BAYS'].all_objects if o.type in {'MESH','CURVE'} and 'DOOR_' in o.name]
hits=[];joint_contacts=[]
for frame in range(1,121):
 s.frame_set(frame);dynamic={o.name:tree(o,oi.matrix_world) for o in moving+doors}
 for n,(a,ab) in dynamic.items():
  for sn,(b,bb) in static.items():
   if not broad(ab,bb):continue
   overlap=a.overlap(b)
   if overlap:
    rec={'frame':frame,'moving':n,'static':sn,'tri_pairs':len(overlap)}
    (joint_contacts if 'ATTACHMENT_' in sn else hits).append(rec)
  if 'DOOR_' not in n:
   for dn in [o.name for o in doors]:
    b,bb=dynamic[dn]
    if broad(ab,bb) and a.overlap(b):hits.append({'frame':frame,'moving':n,'static':dn})
 if frame%20==1:print('RC8_SWEEP_FRAME',frame,flush=True)
(I/f'Reports/motion_{rev}.json').write_text(json.dumps({'status':'candidate, not acceptance','sampled_frames':list(range(1,121)),'hits':hits,'joint_contacts':joint_contacts},indent=2))
print('RC8_SWEEP_HITS',len(hits),flush=True)
for o in s.objects:
 if o.type=='FONT':o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=24
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100
cam=bpy.data.objects['H_SIDE'];cam.data.type='ORTHO';cam.data.ortho_scale=5.8;cam.location=(7,-.4,-.15);target=Vector((0,-.4,-.45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
for frame,name in [(1,'Down'),(71,'Transit'),(120,'Retracted')]:
 s.frame_set(frame);s.render.filepath=str(I/f'Previews/Motion_{rev}_{name}.png');bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('RC8_MOTION_V002_REVIEW_COMPLETE',flush=True)
