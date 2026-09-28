from pathlib import Path
import bpy,json,math
from mathutils import Vector,Quaternion,Matrix
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v004.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v003.blend'));s=bpy.context.scene;s.frame_set(1);root=bpy.data.objects['ORION_ROOT']
main=json.loads((I/'Reports/main_three_axis_doors_search.json').read_text());nose=json.loads((I/'Reports/nose_path_doors_search.json').read_text())['YX']['path'];assert main['path'] and nose
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
  ctrl.rotation_quaternion=q;ctrl.keyframe_insert('rotation_quaternion',frame=frame);wheel.rotation_quaternion=q.inverted();wheel.keyframe_insert('rotation_quaternion',frame=frame)
for o in bpy.data.objects:
 if o.type!='EMPTY' or 'NOSE_DOOR_HINGE' not in o.name:continue
 o.animation_data_clear();sign=int(o.name.rsplit('_',1)[1])
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame;opened=1-max(0,min(1,(f-100)/20))
  o.rotation_quaternion=Quaternion((0,1,0),math.radians(-sign*180)*opened);o.keyframe_insert('rotation_quaternion',frame=frame)
# Correct the existing counter-rotated wheel's axle/fork connections explicitly.
s.frame_set(1);bpy.context.view_layer.update();forks=[]
for label,width in [('NOSE',.13),('MAIN_L',.16),('MAIN_R',.16)]:
 ctrl=bpy.data.objects[f'ORION_{label}_GEAR_PIVOT'];p=ctrl.matrix_world.translation.copy()
 for suffix in ['AXLE','FORK_-1','FORK_1','FORK_BRIDGE_-1','FORK_BRIDGE_1']:
  o=bpy.data.objects[f'ORION_{label}_{suffix}'];M=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=M;o.rotation_mode='QUATERNION';o['RC8_joint']='Illustrative articulated fork, keeps axle and strut visibly connected'
  sign=int(suffix.rsplit('_',1)[1]) if suffix!='AXLE' else 0
  off=Vector((sign*(width/2+.02),0,0));off*=.5 if 'BRIDGE' in suffix else 1
  forks.append((o,ctrl,p,M,off,'BRIDGE' not in suffix and suffix!='AXLE'))
for frame in range(1,241):
 s.frame_set(frame);bpy.context.view_layer.update()
 for o,ctrl,p,M,off,rotates in forks:
  q=ctrl.matrix_world.to_quaternion();N=(q.to_matrix()@M.to_3x3()).to_4x4() if rotates else M.copy();N.translation=p+q@(M.translation-p-off)+off
  o.matrix_world=N;o.keyframe_insert('location',frame=frame);o.keyframe_insert('rotation_quaternion',frame=frame)
# Move the rotating inner housing and its bearing centre together, keeping the aircraft mount fixed.
s.frame_set(1);pitch=bpy.data.objects['ORION_SENSOR_PITCH'];pitch.location.z-=.05
for o in bpy.data.collections['ORION_SENSOR_R3'].objects:
 if o.type!='MESH':continue
 if o.name.startswith('ORION_SENSOR_PITCH_PIVOT_CAP_'):
  T=o.matrix_world.inverted()@Matrix.Translation((0,0,-.05))@o.matrix_world;o.data.transform(T)
 if o.name in ['ORION_SENSOR_YOKE_-1','ORION_SENSOR_YOKE_1']:
  M=o.matrix_world;inv=M.inverted()
  for v in o.data.vertices:p=M@v.co;p.z-=.05*max(0,min(1,(-.38-p.z)/.2));v.co=inv@p
for name,expr in [('ORION_SENSOR_YAW','radians(max(-120,min(120,v)))'),('ORION_SENSOR_PITCH','radians(max(-80,min(35,v)))')]:
 for d in bpy.data.objects[name].animation_data.drivers:d.driver.expression=expr
root.id_properties_ui('sensor_yaw_degrees').update(min=-120,max=120)
root.id_properties_ui('sensor_pitch_degrees').update(min=-80,max=35)
s['RC8_status']='v004 candidate: refined door-aware gear path, connected fork/axle articulation and expanded sensor motion; validation pending'
s.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
print('RC8_MOTION_V004_SAVED',flush=True)
