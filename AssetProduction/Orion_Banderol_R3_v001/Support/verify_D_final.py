from pathlib import Path
import bpy,bmesh,hashlib,json,tempfile,shutil,subprocess
from mathutils.bvhtree import BVHTree
from mathutils import Quaternion
P=Path(__file__).resolve().parents[1]
def digest(o):return hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'utf8') for v in o.data.vertices)).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_C_primary_geometry_v007.blend'))
old={o.name:digest(o) for o in bpy.data.collections['10_SOURCE'].all_objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1);rev=s['revision'].replace('D_','')
unchanged={n:old[n]==digest(bpy.data.objects[n]) for n in old}
def tree(o,dg):
 ev=o.evaluated_get(dg);m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear();return t
body=bpy.data.objects['ORION_FUSELAGE'];sensor=bpy.data.objects['ORION_SENSOR_PITCH_HOUSING'];yaw=bpy.data.objects['ORION_SENSOR_YAW'];pitch=bpy.data.objects['ORION_SENSOR_PITCH']
sensor_hits=[]
for y in [-35,0,35]:
 for p in [-15,0,15]:
  yaw.rotation_quaternion=Quaternion((0,0,1),__import__('math').radians(y));pitch.rotation_quaternion=Quaternion((1,0,0),__import__('math').radians(p));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();st=tree(sensor,dg)
  for obstacle in [body,bpy.data.objects['ORION_NOSE_WHITE']]+[o for o in bpy.data.collections['ORION_GEAR'].objects if o.type=='MESH']:
   hits=st.overlap(tree(obstacle,dg))
   if hits:sensor_hits.append({'yaw':y,'pitch':p,'obstacle':obstacle.name,'pairs':len(hits)})
yaw.rotation_quaternion=Quaternion();pitch.rotation_quaternion=Quaternion();bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();eval_defects=[]
for o in [body,sensor]:
 ev=o.evaluated_get(dg);m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);non=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);vol=bm.calc_volume();bm.free();ev.to_mesh_clear()
 eval_defects.append({'object':o.name,'nonmanifold':non,'degenerate':deg,'volume':vol})
pose_contacts=[]
for fr in range(1,161):
 s.frame_set(fr);dg=bpy.context.evaluated_depsgraph_get()
 left=[o for o in bpy.data.collections['ORION_GEAR'].objects if o.type=='MESH' and 'MAIN_L_' in o.name];right=[o for o in bpy.data.collections['ORION_GEAR'].objects if o.type=='MESH' and 'MAIN_R_' in o.name]
 lt={o.name:tree(o,dg) for o in left};rt={o.name:tree(o,dg) for o in right}
 for n,t in lt.items():
  for r,u in rt.items():
   hits=t.overlap(u)
   if hits:pose_contacts.append({'frame':fr,'left':n,'right':r,'pairs':len(hits)})
s.frame_set(1)
manifest=json.loads((P/'Documentation/source_manifest.json').read_text(encoding='utf-8'))
preserved={path:hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in manifest['existing_asset_sha256'].items()}
refs=[{'name':i.name,'relative':i.filepath.startswith('//'),'exists':Path(bpy.path.abspath(i.filepath)).exists()} for i in bpy.data.images if i.source=='FILE']
# New Blender process opens a relocated copy; copy only necessary current dependencies.
dest=Path(tempfile.mkdtemp(prefix='Orion_D_reopen_'));(dest/'Orion').mkdir();shutil.copy2(P/'Orion/Orion_Master.blend',dest/'Orion/Orion_Master.blend');shutil.copytree(P/'Support/references_private',dest/'Support/references_private')
probe=dest/'probe.py';probe.write_text("import bpy,json\nfrom pathlib import Path\np=Path(__file__).parent\nbpy.ops.wm.open_mainfile(filepath=str(p/'Orion/Orion_Master.blend'))\nassert all(Path(bpy.path.abspath(i.filepath)).exists() for i in bpy.data.images if i.source=='FILE')\nassert bpy.data.objects['ORION_ROOT'].scale[:]==(1.,1.,1.)\nassert bpy.data.scenes['ORION_GEOMETRY_REVIEW'].frame_current==1\nprint('RELOCATED_MASTER_REOPEN_OK')\n")
result=subprocess.run([bpy.app.binary_path,'--background','--python',str(probe)],capture_output=True,text=True,timeout=60)
report={'approved_C_primary_meshes_unchanged':unchanged,'sensor_nine_orientation_checks':sensor_hits,'evaluated_mesh_checks':eval_defects,'left_right_main_gear_intersections_all_160_frames':pose_contacts,'old_assets_preserved':preserved,'relative_images':refs,'relocated_master_reopen':result.returncode==0 and 'RELOCATED_MASTER_REOPEN_OK' in result.stdout,'relocated_test_directory':str(dest),'fresh_reopen_log':result.stdout+result.stderr,'exports_and_engine_import':'NOT ATTEMPTED; later milestone','real_gear_motion':'NOT VERIFIED; animation is illustrative'}
(P/f'Documentation/D_final_validation_{rev}.json').write_text(json.dumps(report,indent=2))
print('FINAL_CHECKS',sum(unchanged.values()),'unchanged primary meshes',len(sensor_hits),'sensor contacts',len(pose_contacts),'main-gear cross contacts','relocation',report['relocated_master_reopen'])
