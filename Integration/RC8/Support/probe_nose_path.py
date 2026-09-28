from pathlib import Path
import bpy,math,json,collections
from mathutils import Vector,Quaternion,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8'
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Assembly_RC8_Motion_v003.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
oi=bpy.data.objects['ORION_LINKED_APPROVED'];bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL'];dg=bpy.context.evaluated_depsgraph_get()
def geo(o,T):
 e=o.evaluated_get(dg);m=e.to_mesh();v=[T@e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def bounds(v):return [(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
def broad(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
static={}
for col in ['ORION_AIRFRAME','ORION_GEAR_BAYS','ORION_SENSOR_R3']:
 for o in bpy.data.collections[col].all_objects:
  if o.type not in {'MESH','CURVE'} or o.hide_render or any(k in o.name for k in ['ATTACHMENT_','OPENING_LIP']):continue
  if o.name=='ORION_FUSELAGE':
   clone=o.copy();clone.data=o.data.copy();s.collection.objects.link(clone)
   bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.76,-.3975));c=bpy.context.object;c.scale=(.48,1.5,1.205)
   mod=clone.modifiers.new('RC8_nose_probe','BOOLEAN');mod.operation='DIFFERENCE';mod.object=c;mod.solver='EXACT';bpy.context.view_layer.update()
   v,f=geo(clone,oi.matrix_world)
  else:v,f=geo(o,oi.matrix_world)
  if o.name.startswith('ORION_NOSE_DOOR_'):
   h=o.parent;sign=int(h.name.rsplit('_',1)[1]);pivot=oi.matrix_world@h.matrix_world.translation
   R=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(-sign*60),4,'Y')@Matrix.Translation(-pivot);v=[R@p for p in v]
  static[o.name]=(BVHTree.FromPolygons(v,f),bounds(v))
for o in bi.instance_collection.all_objects:
 if o.type!='MESH' or o.hide_render:continue
 v,f=geo(o,bi.matrix_world);static[o.name]=(BVHTree.FromPolygons(v,f),bounds(v))
ctrl=bpy.data.objects['ORION_NOSE_GEAR_PIVOT'];wheel=bpy.data.objects['ORION_NOSE_WHEEL_AXLE'];p=oi.matrix_world@ctrl.matrix_world.translation;wc=oi.matrix_world@wheel.matrix_world.translation;d=wc-p
wn={o.name for o in wheel.children_recursive};moving={}
for o in ctrl.children_recursive:
 if o.type not in {'MESH','CURVE'} or o.hide_render:continue
 v,f=geo(o,oi.matrix_world);moving[o.name]=([x-(wc if o.name in wn else p) for x in v],f,o.name in wn)
def check(q):
 hits=[]
 for n,(v,f,iswheel) in moving.items():
  vv=[x+p+q@d for x in v] if iswheel else [p+q@x for x in v];bb=bounds(vv)
  cand=[(sn,st) for sn,(st,sb) in static.items() if broad(bb,sb)]
  if cand:
   tree=BVHTree.FromPolygons(vv,f);hits.extend((n,sn) for sn,st in cand if tree.overlap(st))
 return hits
report={}
for order in ['YX']:
 grid={}
 for t in range(41):
  for b in range(41):
   x=Quaternion((1,0,0),math.radians(-107)*t/40);y=Quaternion((0,1,0),math.radians(-50)*b/40)
   grid[(t,b)]=check(x@y if order=='XY' else y@x)
  print('NOSE',order,t,flush=True)
 prev={(0,0):None};queue=collections.deque([(0,0)])
 while queue:
  n=queue.popleft()
  if n==(40,0):break
  for dt,db in [(1,0),(0,1),(0,-1),(1,1),(1,-1)]:
   m=(n[0]+dt,n[1]+db)
   if m in grid and not grid[m] and m not in prev:
    safe=True
    for f in [.25,.5,.75]:
     t=n[0]+(m[0]-n[0])*f;b=n[1]+(m[1]-n[1])*f
     x=Quaternion((1,0,0),math.radians(-107)*t/40);y=Quaternion((0,1,0),math.radians(-50)*b/40)
     if check(x@y if order=='XY' else y@x):safe=False;break
    if safe:prev[m]=n;queue.append(m)
 path=[];n=(40,0)
 if n in prev:
  while n is not None:path.append(n);n=prev[n]
  path.reverse()
 report[order]={'path':[[a/2,b/2] for a,b in path],'grid':{f'{a},{b}':v for (a,b),v in grid.items()},'door_open_angle':180,'grid_steps':40}
 print('NOSE_PATH',order,path,flush=True)
(I/'Reports/nose_path_doors_search.json').write_text(json.dumps(report,indent=2))
print('NOSE_PROBE_COMPLETE',flush=True)
