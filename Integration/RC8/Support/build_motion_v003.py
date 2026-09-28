from pathlib import Path
import bpy,json,math
from mathutils import Vector,Quaternion
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v003.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v002.blend'));s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s
s.frame_set(120);closed={o.name:o.matrix_world.copy() for o in bpy.data.objects if 'DOOR_' in o.name};s.frame_set(1)
c=bpy.data.objects['ORION_NOSE_BAY_CUTTER']
for v in c.data.vertices:v.co.x*=1.5
for side in [-1,1]:
 bpy.data.objects[f'ORION_NOSE_BAY_SIDE_{side}'].location.x=side*.243
 for n in [f'ORION_NOSE_BAY_END_{side}']:
  for v in bpy.data.objects[n].data.vertices:v.co.x*=1.5
 lip=bpy.data.objects[f'ORION_NOSE_OPENING_LIP_{side}']
 for sp in lip.data.splines:
  for p in sp.points:p.co.x*=1.5
 hinge=bpy.data.objects[f'ORION_NOSE_DOOR_HINGE_{side}'];children=list(hinge.children);hinge.animation_data_clear();hinge.rotation_quaternion=Quaternion();hinge.location.x=side*.24
 bpy.context.view_layer.update()
 for o in children:
  M=closed[o.name];o.parent=None;o.matrix_world=M
  if 'SHELL' in o.name:
   for v in o.data.vertices:p=M@v.co;p.x*=1.5;v.co=M.inverted()@p
  else:o.location.x=side*.24
  keep=o.matrix_world.copy();o.parent=hinge;o.matrix_parent_inverse=hinge.matrix_world.inverted();o.matrix_world=keep
for n in ['ORION_NOSE_BAY_ROOF','ORION_NOSE_BAY_ROOF_SUPPORT_0','ORION_NOSE_BAY_ROOF_SUPPORT_1']:
 for v in bpy.data.objects[n].data.vertices:v.co.x*=1.5
main=json.loads((I/'Reports/main_three_axis_search.json').read_text());nose=json.loads((I/'Reports/nose_path_experiments_wide.json').read_text())['YX']['path']
assert main['path'] and nose
def sample(points,t):
 u=t*(len(points)-1);k=min(len(points)-2,int(u));v=u-k;return [points[k][j]*(1-v)+points[k+1][j]*v for j in range(len(points[0]))]
for label in ['NOSE','MAIN_L','MAIN_R']:
 ctrl=bpy.data.objects[f'ORION_{label}_GEAR_PIVOT'];wheel=bpy.data.objects[f'ORION_{label}_WHEEL_AXLE'];ctrl.animation_data_clear();wheel.animation_data_clear()
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame;t=max(0,min(1,(f-20)/80))
  if label=='NOSE':
   x,b=sample(nose,t);q=Quaternion((0,1,0),math.radians(-50)*b/20)@Quaternion((1,0,0),math.radians(-107)*x/20)
  else:
   x,z,b=sample(main['path'],t);side=1 if label.endswith('R') else -1
   q=Quaternion((1,0,0),main['step_pitch']*x)@Quaternion((0,0,1),side*main['step_yaw']*z)@Quaternion((0,1,0),side*main['step_bank']*b)
  ctrl.rotation_quaternion=q;ctrl.keyframe_insert('rotation_quaternion',frame=frame)
  wheel.rotation_quaternion=q.inverted();wheel.keyframe_insert('rotation_quaternion',frame=frame)
for o in bpy.data.objects:
 if o.type!='EMPTY' or 'DOOR_HINGE' not in o.name:continue
 o.animation_data_clear();side=1 if 'MAIN_R' in o.name else -1
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame;opened=1-max(0,min(1,(f-100)/20));sign=int(o.name.rsplit('_',1)[1])
  angle=-side*180 if 'MAIN_' in o.name else -sign*120
  o.rotation_quaternion=Quaternion((0,1,0),math.radians(angle)*opened);o.keyframe_insert('rotation_quaternion',frame=frame)
s.frame_set(1);s['RC8_status']='v003 candidate; three-axis main hinge and side-clearing nose path; full validation pending'
s['motion_evidence']='C illustrative visual articulation; no real-aircraft retraction claim'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
print('RC8_MOTION_V003_SAVED',flush=True)
