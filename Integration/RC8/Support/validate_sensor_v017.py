from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8'
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v017.blend'));s=bpy.context.scene;s.frame_set(1)
def geometry(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def bounds(v):return [(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
def broad(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
yaw=bpy.data.objects['ORION_SENSOR_YAW'];pitch=bpy.data.objects['ORION_SENSOR_PITCH'];yp=yaw.matrix_world.translation.copy();pp=pitch.matrix_world.translation.copy()

moving={};yoke={}
for o in bpy.data.collections['ORION_SENSOR_R3'].all_objects:
 if o.type!='MESH' or o.hide_render:continue
 ancestors=[];a=o.parent
 while a:ancestors.append(a.name);a=a.parent
 if yaw.name not in ancestors:continue
 v,f=geometry(o)
 
 moving[o.name]=(v,f,pitch.name in ancestors)
 if o.name.startswith('ORION_SENSOR_YOKE_'):yoke[o.name]=(v,f)
allhits=[];pose_results=[]
for frame in [1,30,60,90,120]:
 s.frame_set(frame);static={}
 obstacles=[bpy.data.objects['ORION_FUSELAGE'],bpy.data.objects['ORION_NOSE_WHITE']]+[o for o in bpy.data.collections['ORION_GEAR'].all_objects if o.type in {'MESH','CURVE'} and not o.hide_render]
 for o in obstacles:
  v,f=geometry(o);static[o.name]=(BVHTree.FromPolygons(v,f),bounds(v))
 for yd in range(-120,121,15):
  Y=Matrix.Translation(yp)@Matrix.Rotation(math.radians(yd),4,'Z')@Matrix.Translation(-yp)
  yt={n:(BVHTree.FromPolygons([Y@v for v in vs],fs),bounds([Y@v for v in vs])) for n,(vs,fs) in yoke.items()}
  for pd in range(-80,36,5):
   P=Y@Matrix.Translation(pp)@Matrix.Rotation(math.radians(pd),4,'X')@Matrix.Translation(-pp);hits=[]
   for n,(vs,fs,inner) in moving.items():
    T=P if inner else Y;v=[T@p for p in vs];bb=bounds(v);candidates=[]
    for sn,(st,sb) in static.items():
     if sn=='ORION_FUSELAGE' and n in ['ORION_SENSOR_YAW_COLLAR','ORION_SENSOR_YOKE_TOP_BRIDGE']:continue
     if broad(bb,sb):candidates.append((sn,st))
    if inner and 'PIVOT' not in n and 'SIDE_ACCESS' not in n and 'SIDE_FASTENER' not in n:
     candidates.extend((sn,st) for sn,(st,sb) in yt.items() if broad(bb,sb))
    if candidates:
     tree=BVHTree.FromPolygons(v,fs);hits.extend([n,sn] for sn,st in candidates if tree.overlap(st))
   pose_results.append({'gear_frame':frame,'yaw':yd,'pitch':pd,'clear':not hits})
   if hits:allhits.append({'gear_frame':frame,'yaw':yd,'pitch':pd,'pairs':hits})
  print('SENSOR_SCAN',frame,yd,flush=True)
(I/'Reports/sensor_actual_v017.json').write_text(json.dumps({'poses':pose_results,'contacts':allhits,'pitch_assembly_shift_z':0,'status':'sampled pose grid, intermediate gear/angles still require validation'},indent=2))
print('SENSOR_RANGE_COMPLETE',len(pose_results),len(allhits),flush=True)
