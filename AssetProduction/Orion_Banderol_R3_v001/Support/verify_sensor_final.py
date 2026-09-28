from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
def digest(o):return hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_E_exterior_rig_v005.blend'))
old={o.name:digest(o) for o in bpy.data.collections['10_SOURCE'].all_objects if o.type=='MESH' and not o.name.startswith('ORION_SENSOR_')}
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_E_sensor_fix_v007.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;root=bpy.data.objects['ORION_ROOT'];assert s['revision']=='E_sensor_v007'
assert all(digest(bpy.data.objects[n])==h for n,h in old.items())
assert all(Path(bpy.path.abspath(i.filepath)).exists() for i in bpy.data.images if i.source=='FILE')
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);ev.to_mesh_clear();return t
sensor=[o for o in bpy.data.collections['ORION_SENSOR_R3'].objects if o.type=='MESH'];gear=[o for o in bpy.data.collections['ORION_GEAR'].objects if o.type=='MESH'];hits=[]
for fr in range(1,161):
 s.frame_set(fr);ts={o.name:tree(o) for o in sensor}
 for g in gear:
  tg=tree(g)
  for n,t in ts.items():
   if t.overlap(tg):hits.append({'frame':fr,'sensor':n,'gear':g.name})
posehits=[]
for fr in [1,120]:
 s.frame_set(fr)
 for y in [-35,0,35]:
  for p in [-10,0,10]:
   root['sensor_yaw_degrees']=y;root['sensor_pitch_degrees']=p;root.update_tag();bpy.context.view_layer.update()
   obstacles=gear+[bpy.data.objects['ORION_FUSELAGE'],bpy.data.objects['ORION_NOSE_WHITE']]
   for o in sensor:
    if o.parent not in [bpy.data.objects['ORION_SENSOR_YAW'],bpy.data.objects['ORION_SENSOR_PITCH']]:continue
    t=tree(o)
    for ob in obstacles:
     if t.overlap(tree(ob)):posehits.append({'frame':fr,'yaw':y,'pitch':p,'sensor':o.name,'obstacle':ob.name})
arm=bpy.data.objects['ORION_EXPORT_ARMATURE'];errors=[]
for b in arm.pose.bones:
 if b.constraints:
  a=arm.matrix_world@b.matrix;c=b.constraints[0].target.matrix_world;err=max(abs(a[i][j]-c[i][j]) for i in range(4) for j in range(4))
  if err>1e-5:errors.append((b.name,err))
allowed=[h for h in posehits if h['obstacle']=='ORION_FUSELAGE' and h['sensor'] in ['ORION_SENSOR_YAW_COLLAR','ORION_SENSOR_YOKE_TOP_BRIDGE']]
unexpected=[h for h in posehits if h not in allowed]
report={'fresh_numbered_checkpoint_open':True,'non_sensor_source_vertices_unchanged':True,'image_dependencies_found':True,'all_160_gear_frames_sensor_contacts':hits,'complete_moving_sensor_pose_contacts':posehits,'intentional_attachment_interface_contacts':allowed,'unexpected_pose_contacts':unexpected,'posed_bone_errors':errors,'engine_validation':'NOT ATTEMPTED'}
(P/'Documentation/SENSOR_final_validation_v007.json').write_text(json.dumps(report,indent=2));print('SENSOR_FINAL',len(hits),'gear contacts',len(posehits),'posed contacts',len(errors),'bone errors')
