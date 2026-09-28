from pathlib import Path
import bpy,json,math
from mathutils import Vector,Quaternion,Matrix
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Orion_RC8_Motion_v011.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v010.blend'));s=bpy.context.scene;s.frame_set(1);root=bpy.data.objects['ORION_ROOT']
main=json.loads((I/'Reports/main_three_axis_doors_v010_search.json').read_text());assert main['path']
timing=json.loads((I/'Reports/door_timing_search_v009.json').read_text())['groups']['NOSE']['timing'];assert len(timing)==100
def sample(points,t):
 u=t*(len(points)-1);k=min(len(points)-2,int(u));v=u-k;return [points[k][j]*(1-v)+points[k+1][j]*v for j in range(len(points[0]))]
for label in ['MAIN_L','MAIN_R']:
 ctrl=bpy.data.objects[f'ORION_{label}_GEAR_PIVOT'];wheel=bpy.data.objects[f'ORION_{label}_WHEEL_AXLE'];ctrl.animation_data_clear();wheel.animation_data_clear();side=1 if label.endswith('R') else -1
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame;t=max(0,min(1,(f-20)/80));x,z,b=sample(main['path'],t)
  q=Quaternion((1,0,0),main['step_pitch']*x)@Quaternion((0,0,1),side*main['step_yaw']*z)@Quaternion((0,1,0),side*main['step_bank']*b)
  ctrl.rotation_quaternion=q;ctrl.keyframe_insert('rotation_quaternion',frame=frame);wheel.rotation_quaternion=q.inverted();wheel.keyframe_insert('rotation_quaternion',frame=frame)
for side in [-1,1]:
 lip=bpy.data.objects[f'ORION_NOSE_OPENING_LIP_{side}']
 for sp in lip.data.splines:
  for p in sp.points:p.co.x=side*.247
 hinge=bpy.data.objects[f'ORION_NOSE_DOOR_HINGE_{side}'];hinge.animation_data_clear()
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame
  angle=timing[f-1][1] if f<=100 else timing[-1][1]*(120-f)/20
  hinge.rotation_quaternion=Quaternion((0,1,0),math.radians(-side*angle));hinge.keyframe_insert('rotation_quaternion',frame=frame)
# Re-bake the articulated forks from the unchanged extended pose around the corrected hidden pivots.
s.frame_set(1);bpy.context.view_layer.update();forks=[]
for label,width in [('NOSE',.13),('MAIN_L',.16),('MAIN_R',.16)]:
 ctrl=bpy.data.objects[f'ORION_{label}_GEAR_PIVOT'];p=ctrl.matrix_world.translation.copy()
 for suffix in ['AXLE','FORK_-1','FORK_1','FORK_BRIDGE_-1','FORK_BRIDGE_1']:
  o=bpy.data.objects[f'ORION_{label}_{suffix}'];M=o.matrix_world.copy();o.animation_data_clear();o.rotation_mode='QUATERNION'
  sign=int(suffix.rsplit('_',1)[1]) if suffix!='AXLE' else 0;off=Vector((sign*(width/2+.02),0,0));off*=.5 if 'BRIDGE' in suffix else 1
  forks.append((o,ctrl,p,M,off,'BRIDGE' not in suffix and suffix!='AXLE'))
for frame in range(1,241):
 s.frame_set(frame);bpy.context.view_layer.update()
 for o,ctrl,p,M,off,rotates in forks:
  q=ctrl.matrix_world.to_quaternion();N=(q.to_matrix()@M.to_3x3()).to_4x4() if rotates else M.copy();N.translation=p+q@(M.translation-p-off)+off;o.matrix_world=N;o.keyframe_insert('location',frame=frame);o.keyframe_insert('rotation_quaternion',frame=frame)
for action in bpy.data.actions:
 if action.library:continue
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);s['RC8_status']='v011 coordinated motion candidate; complete sweep validation pending'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
print('RC8_V011_SAVED',flush=True)
