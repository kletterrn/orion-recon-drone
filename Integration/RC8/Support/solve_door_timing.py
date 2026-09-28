"""Find coordinated visual door timing without changing the accepted gear path."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8'
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v009.blend'));s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(120)
oi=bpy.data.objects['ORION_LINKED_APPROVED'];bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL']
def geo(o,T=Matrix.Identity(4)):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[T@e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def union(items):
 v=[];f=[]
 for vs,fs in items:
  n=len(v);v.extend(vs);f.extend(tuple(n+j for j in face) for face in fs)
 return BVHTree.FromPolygons(v,f)
fixed=[]
for col in ['ORION_AIRFRAME','ORION_GEAR_BAYS','ORION_SENSOR_R3']:
 for o in bpy.data.collections[col].all_objects:
  if o.type not in {'MESH','CURVE'} or o.hide_render or 'DOOR_' in o.name:continue
  fixed.append(geo(o,oi.matrix_world))
for o in bi.instance_collection.all_objects:
 if o.type=='MESH' and not o.hide_render:fixed.append(geo(o,bi.matrix_world))
st=union(fixed);candidates={};report={'source':'Assembly_RC8_Motion_v009.blend','groups':{}}
for group in ['MAIN','NOSE']:
 parts=[]
 for o in bpy.data.collections['ORION_GEAR_BAYS'].all_objects:
  if o.type not in {'MESH','CURVE'} or 'DOOR_' not in o.name or '_'+group+'_' not in o.name or 'FIXED_EAR' in o.name:continue
  h=o.parent
  if not h or 'DOOR_HINGE' not in h.name:continue
  side=1 if h.matrix_world.translation.x>0 else -1
  parts.append((geo(o,oi.matrix_world),oi.matrix_world@h.matrix_world.translation,side,'DOOR_SHELL' in o.name))
 candidates[group]={}
 for angle in range(0,241,3):
  transformed=[];shells=[]
  for (v,f),p,side,shell in parts:
   R=Matrix.Translation(p)@Matrix.Rotation(math.radians(-side*angle),4,'Y')@Matrix.Translation(-p);g=([R@x for x in v],f);transformed.append(g)
   if shell:shells.append(g)
  t=union(transformed)
  if not union(shells).overlap(st):candidates[group][angle]=t
 print('STATIC_SAFE',group,list(candidates[group]),flush=True)
 report['groups'][group]={'static_safe_angles':list(candidates[group]),'allowed_by_frame':{}}
gear=[o for o in bpy.data.collections['ORION_GEAR'].all_objects if o.type in {'MESH','CURVE'} and not o.hide_render]
for frame in range(1,101):
 s.frame_set(frame);gt=union([geo(o,oi.matrix_world) for o in gear])
 for group,poses in candidates.items():report['groups'][group]['allowed_by_frame'][str(frame)]=[a for a,t in poses.items() if not t.overlap(gt)]
 if frame%20==0:print('DOOR_TIMING',frame,flush=True)
for group,data in report['groups'].items():
 states={a:(abs(a-90)*.01,None) for a in data['allowed_by_frame']['1']};history={1:states}
 for frame in range(2,101):
  nxt={}
  for a in data['allowed_by_frame'][str(frame)]:
   choices=[(cost+(a-b)**2+.02*abs(a-110),b) for b,(cost,_) in states.items() if abs(a-b)<=18]
   if choices:nxt[a]=min(choices)
  states=nxt;history[frame]=states
 path=[]
 if states:
  a=min(states,key=lambda a:states[a][0])
  for frame in range(100,0,-1):path.append([frame,a]);a=history[frame][a][1]
  path.reverse()
 data['timing']=path;data['empty_frames']=[int(f) for f,a in data['allowed_by_frame'].items() if not a]
 print('DOOR_RESULT',group,'timing',len(path),'blocked frames',data['empty_frames'],flush=True)
(I/'Reports/door_timing_search_v009.json').write_text(json.dumps(report,indent=2));print('DOOR_TIMING_SEARCH_COMPLETE',flush=True)
