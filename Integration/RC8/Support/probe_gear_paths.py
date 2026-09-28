"""Read-only evaluated-mesh path experiments; never saves source assets."""
from pathlib import Path
import bpy,math,json,sys,collections
from mathutils import Vector,Quaternion,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3]; P=W/'AssetProduction/Orion_Banderol_R3_v001'
outer=float(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else .33
bpy.ops.wm.open_mainfile(filepath=str(W/'Integration/RC8/Blender/Assembly_RC8_Motion_v010.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(20)
dg=bpy.context.evaluated_depsgraph_get()
def geo(o,T=Matrix.Identity(4)):
 e=o.evaluated_get(dg);m=e.to_mesh();M=T@e.matrix_world
 v=[M@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def bounds(v):return [(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
def broad(a,b):return all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3))
bi=bpy.data.objects['BANDEROL_LINKED_PROVISIONAL'];oi=bpy.data.objects['ORION_LINKED_APPROVED']
static={}
for o in bi.instance_collection.all_objects:
 if o.type!='MESH' or o.hide_render:continue
 v,f=geo(o,bi.matrix_world);static[o.name]=(BVHTree.FromPolygons(v,f),bounds(v))
for cname in ['ORION_AIRFRAME','ORION_GEAR_BAYS','ORION_WINGS','ORION_TAIL_REAR']:
 for o in bpy.data.collections[cname].all_objects:
  if o.type not in {'MESH','CURVE'} or o.hide_render:continue
  if o.name=='ORION_FUSELAGE':
   clone=o.copy();clone.data=o.data.copy();s.collection.objects.link(clone)
   for side in [-1,1]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(side*(outer+.01)/2,-1.46,-.3975))
    cutter=bpy.context.object;cutter.scale=(outer-.01,1.88,1.205)
    bo=clone.modifiers.new('RC8_probe_hidden_mouth','BOOLEAN');bo.operation='DIFFERENCE';bo.object=cutter;bo.solver='EXACT'
   bpy.context.view_layer.update();v,f=geo(clone,oi.matrix_world)
  else:v,f=geo(o,oi.matrix_world)
  static[o.name]=(BVHTree.FromPolygons(v,f),bounds(v))
moving={};pivot=bpy.data.objects['ORION_MAIN_R_GEAR_PIVOT'];p=oi.matrix_world@pivot.matrix_world.translation
wheel=bpy.data.objects['ORION_MAIN_R_WHEEL_AXLE'];wc=oi.matrix_world@wheel.matrix_world.translation;d=wc-p
wheel_names={o.name for o in wheel.children_recursive if o.type in {'MESH','CURVE'}}
end=wc-d.normalized()*.14
for o in bpy.data.collections['ORION_GEAR'].all_objects:
 if not o.name.startswith('ORION_MAIN_R_'):continue
 if o.type not in {'MESH','CURVE'} or o.hide_render:continue
 v,f=geo(o,oi.matrix_world)
 if o.name in wheel_names or o.name=='ORION_MAIN_R_AXLE':moving[o.name]=([x-wc for x in v],f,'wheel')
 elif 'FORK_BRIDGE_' in o.name:moving[o.name]=([x-end for x in v],f,'bridge')
 elif 'FORK_' in o.name:
  off=Vector((int(o.name.rsplit('_',1)[1])*.1,0,0));moving[o.name]=([x-p-off for x in v],f,off)
 else:moving[o.name]=([x-p for x in v],f,'leg')
def check(q):
 hits=[]
 for n,(v,f,mode) in moving.items():
  if mode=='wheel':vv=[x+p+q@d for x in v]
  elif mode=='bridge':vv=[x+p+q@(end-p) for x in v]
  elif mode=='leg':vv=[p+q@x for x in v]
  else:vv=[p+q@x+mode for x in v]
  bb=bounds(vv);candidates=[(sn,st) for sn,(st,sb) in static.items() if broad(bb,sb)]
  if candidates:
   tree=BVHTree.FromPolygons(vv,f)
   hits.extend((n,sn) for sn,st in candidates if tree.overlap(st))
 return hits
horiz=math.hypot(d.x,d.y);tx=.035;ty=-math.sqrt(horiz*horiz-tx*tx)
az=math.atan2(ty,tx)-math.atan2(d.y,d.x)
folded=Quaternion((0,0,1),az)@d
updy=-math.sqrt(d.length_squared-tx*tx-.28*.28)
ax=math.atan2(.28,updy)-math.atan2(folded.z,folded.y)
ax=(ax+math.pi)%(2*math.pi)-math.pi
report={'experimental_bay_outer_x':outer,'az_deg':math.degrees(az),'ax_deg':math.degrees(ax),'paths':{}}
grid={}
for xi in range(21):
 for zi in range(21):
  q=Quaternion((1,0,0),ax*xi/20)@Quaternion((0,0,1),az*zi/20)
  hits=check(q)
  bad=[h for h in hits if 'ATTACHMENT_' not in h[1] and 'OPENING_LIP' not in h[1]]
  grid[f'{xi},{zi}']=bad
 print('GRID_ROW',xi,flush=True)
report['grid']=grid
prev={(0,0):None};queue=collections.deque([(0,0)])
while queue:
 n=queue.popleft()
 if n==(20,20):break
 for dx,dz in [(1,0),(0,1),(1,1),(-1,0),(0,-1)]:
  m=(n[0]+dx,n[1]+dz);key=f'{m[0]},{m[1]}'
  if key in grid and not grid[key] and m not in prev:prev[m]=n;queue.append(m)
path=[];n=(20,20)
if n in prev:
 while n is not None:path.append(n);n=prev[n]
 path.reverse()
report['grid_path']=path
print('GRID_PATH',path,flush=True)
for mode in ['old','simultaneous','lift_then_yaw','early_lift']:
 rows=[]
 for i in range(21):
  t=i/20
  if mode=='old':z=min(1,t*2);x=max(0,t*2-1)
  elif mode=='simultaneous':z=t;x=t
  elif mode=='lift_then_yaw':x=min(1,t*2);z=max(0,t*2-1)
  else:x=min(1,t*3);z=t
  q=Quaternion((1,0,0),ax*x)@Quaternion((0,0,1),az*z)
  hits=check(q)
  rows.append({'t':t,'pairs':hits,'wheel':list(p+q@d)})
 report['paths'][mode]=rows
 print('PATH',mode,'contacts',sum(len(r['pairs']) for r in rows),flush=True)
(W/f'Integration/RC8/Reports/gear_path_deployed_{outer:.3f}.json').write_text(json.dumps(report,indent=2))
print('RC8_PATH_PROBE_COMPLETE',flush=True)
