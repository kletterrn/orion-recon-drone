"""Illustrative local clearance revision. Authoritative approved masters stay untouched."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector,Quaternion
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8'
target=I/'Blender/Orion_RC8_Motion_v002.blend'
if target.exists():raise RuntimeError('Checkpoint already exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v001.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(120)
closed={o.name:o.matrix_world.copy() for o in bpy.data.objects if 'MAIN_' in o.name and 'DOOR_' in o.name}
s.frame_set(1);bpy.context.view_layer.update()
body=bpy.data.objects['ORION_FUSELAGE'];stations=json.loads(body['stations_json'])
def interp(y,i):
 xs=[p[0] for p in stations];ys=[p[i] for p in stations];ds=[(ys[k+1]-ys[k])/(xs[k+1]-xs[k]) for k in range(len(xs)-1)];ts=[ds[0]]
 for k in range(1,len(xs)-1):
  h0=xs[k]-xs[k-1];h1=xs[k+1]-xs[k];a=2*h1+h0;b=h1+2*h0;ts.append(0 if ds[k-1]*ds[k]<=0 else (a+b)/(a/ds[k-1]+b/ds[k]))
 ts.append(ds[-1]);k=next((j for j in range(len(xs)-1) if y<=xs[j+1]),len(xs)-2);h=xs[k+1]-xs[k];t=(y-xs[k])/h
 return (2*t**3-3*t*t+1)*ys[k]+(t**3-2*t*t+t)*h*ts[k]+(-2*t**3+3*t*t)*ys[k+1]+(t**3-t*t)*h*ts[k+1]
def skin(x,y):
 w=interp(y,1);bt=interp(y,3);top=interp(y,2);u=min(.999,abs(x)/w)**(1/.45)
 return bt+(top-bt)*.17*(1-math.sqrt(1-u*u))
outer=.33
for side,label in [(-1,'L'),(1,'R')]:
 prefix=f'ORION_MAIN_{label}_';c=bpy.data.objects[prefix+'BAY_CUTTER']
 # Scale the retained cutter's mesh about its centre; this changes only the bay opening.
 for v in c.data.vertices:v.co.x*= (outer-.01)/.21
 c.location.x=side*(outer+.01)/2
 wall=bpy.data.objects[prefix+'BAY_SIDE_'+str(side)];wall.location.x=side*(outer+.003)
 for end in [-1,1]:
  o=bpy.data.objects[prefix+'BAY_END_'+str(end)];o.location.x=side*(outer+.01)/2
  for v in o.data.vertices:v.co.x*=(outer-.01)/.21
 for n in ['BAY_ROOF','BAY_ROOF_SUPPORT_0','BAY_ROOF_SUPPORT_1']:
  o=bpy.data.objects[prefix+n];o.location.x=side*(outer+.01)/2
  for v in o.data.vertices:v.co.x*=(outer-.01)/.21
 lip=bpy.data.objects[prefix+'OPENING_LIP_'+str(side)]
 for sp in lip.data.splines:
  for p in sp.points:p.co.x=side*outer;p.co.z=skin(side*outer,p.co.y)-.002
 hinge=bpy.data.objects[prefix+'DOOR_HINGE_'+str(-side)]
 children=list(hinge.children);hinge.animation_data_clear();hinge.rotation_quaternion=Quaternion();hinge.location=(side*outer,-1.46,skin(side*outer,-1.46))
 bpy.context.view_layer.update()
 for o in children:
  M=closed[o.name];o.parent=None;o.matrix_world=M
  if 'SHELL' in o.name:
   inv=M.inverted()
   for v in o.data.vertices:
    p=M@v.co;oldx=p.x;p.x=side*(.01+(abs(oldx)-.01)*(outer-.01)/.21);p.z+=skin(p.x,p.y)-skin(oldx,p.y);v.co=inv@p
  else:
   o.matrix_world.translation.x=side*outer
   o.matrix_world.translation.z=skin(side*outer,o.matrix_world.translation.y)
  saved=o.matrix_world.copy();o.parent=hinge;o.matrix_parent_inverse=hinge.matrix_world.inverted();o.matrix_world=saved
 hinge['RC8_change']='Illustrative outboard hinge; clears centreline payload. Bay widened locally, exterior contour retained.'
def path(t):
 knots=[(0,0,0),(.45,.45,.70),(.65,.60,.90),(.80,.75,.90),(1,1,1)]
 for a,b in zip(knots,knots[1:]):
  if t<=b[0]:
   k=(t-a[0])/(b[0]-a[0]);return a[1]+(b[1]-a[1])*k,a[2]+(b[2]-a[2])*k
 return 1,1
for label in ['NOSE','MAIN_L','MAIN_R']:
 ctrl=bpy.data.objects[f'ORION_{label}_GEAR_PIVOT'];wheel=bpy.data.objects[f'ORION_{label}_WHEEL_AXLE']
 d=wheel.matrix_world.translation-ctrl.matrix_world.translation
 ctrl.animation_data_clear();wheel.animation_data_clear()
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame;t=max(0,min(1,(f-20)/80))
  if label=='NOSE':q=Quaternion((1,0,0),math.radians(-107)*t)
  else:
   side=1 if label.endswith('R') else -1;tx=side*.035;ty=-math.sqrt(d.x*d.x+d.y*d.y-tx*tx)
   az=math.atan2(ty,tx)-math.atan2(d.y,d.x);az=(az+math.pi)%(2*math.pi)-math.pi
   folded=Quaternion((0,0,1),az)@d;dy=-math.sqrt(d.length_squared-tx*tx-.22**2)
   ax=math.atan2(.22,dy)-math.atan2(folded.z,folded.y);ax=(ax+math.pi)%(2*math.pi)-math.pi;x,z=path(t)
   q=Quaternion((1,0,0),ax*x)@Quaternion((0,0,1),az*z)
  ctrl.rotation_quaternion=q;ctrl.keyframe_insert('rotation_quaternion',frame=frame)
  wheel.rotation_quaternion=q.inverted();wheel.keyframe_insert('rotation_quaternion',frame=frame)
for o in bpy.data.objects:
 if o.type!='EMPTY' or 'DOOR_HINGE' not in o.name:continue
 o.animation_data_clear();side=1 if 'MAIN_R' in o.name else -1
 for frame in range(1,241):
  f=frame if frame<=120 else 241-frame;opened=1-max(0,min(1,(f-100)/20))
  sign=int(o.name.rsplit('_',1)[1]);angle=-side*130 if 'MAIN_' in o.name else -sign*85
  o.rotation_quaternion=Quaternion((0,1,0),math.radians(angle)*opened);o.keyframe_insert('rotation_quaternion',frame=frame)
s.frame_end=240;s.frame_set(1);s['RC8_status']='v002 clearance candidate; widened main bay mouths and outboard doors; validation pending'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=True)
print('RC8_MOTION_V002_SAVED',flush=True)
