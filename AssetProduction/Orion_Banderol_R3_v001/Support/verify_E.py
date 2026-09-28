from pathlib import Path
import bpy,bmesh,json,hashlib,math,subprocess,tempfile,shutil
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
def digest(o):return hashlib.sha256(b''.join(str(tuple(v.co)).encode() for v in o.data.vertices)).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_D_wing_root_fix_v012.blend'))
old={o.name:digest(o) for o in bpy.data.collections['10_SOURCE'].all_objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1);rev=s['revision'].removeprefix('E_');root=bpy.data.objects['ORION_ROOT']
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear();return t
def defects(o,evaluated=False):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else o;m=ev.to_mesh() if evaluated else o.data;bm=bmesh.new();bm.from_mesh(m);r={'name':o.name,'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'volume':bm.calc_volume()};bm.free()
 if evaluated:ev.to_mesh_clear()
 return r
bad=[]
for o in bpy.data.collections['10_SOURCE'].all_objects:
 if o.type!='MESH':continue
 r=defects(o)
 if r['nonmanifold'] or r['degenerate'] or r['volume']<=0:bad.append(r)
props=json.loads((P/f'Documentation/E_controls_{rev}.json').read_text())['properties'];contacts=[];motion=[]
for name,data in props.items():
 prop=data['property'];o=bpy.data.objects[name];base=o.matrix_world.copy()
 if 'WHEEL' in name or 'PROPELLER' in name:values=[0,45,90,180]
 else:values=[-data['limit_degrees'],0,data['limit_degrees']]
 for value in values:
  root[prop]=value;root.update_tag();bpy.context.view_layer.update()
  # Changing the property must move its control and every associated armature bone.
  moved=max(abs(o.matrix_world[i][j]-base[i][j]) for i in range(3) for j in range(3));motion.append({'control':name,'degrees':value,'rotation_delta':moved})
  if not value or 'WHEEL' in name:continue
  if 'PROPELLER' in name:
   moving=[bpy.data.objects['ORION_PROPELLER_BLADE_'+l] for l in ['A','B']];obstacles=[bpy.data.objects[n] for n in ['ORION_FUSELAGE','ORION_TAIL_L','ORION_TAIL_R','ORION_RUDDERVATOR_L','ORION_RUDDERVATOR_R']]
  elif 'SENSOR' in name:
   moving=[bpy.data.objects['ORION_SENSOR_PITCH_HOUSING']];obstacles=[bpy.data.objects['ORION_FUSELAGE'],bpy.data.objects['ORION_NOSE_WHITE']]+[ob for ob in bpy.data.collections['ORION_GEAR'].all_objects if ob.type=='MESH']
  else:
   moving=list(o.children);obstacles=[bpy.data.objects[n] for n in ['ORION_FUSELAGE','ORION_WING_L','ORION_WING_R','ORION_WING_ROOT_BLEND_L','ORION_WING_ROOT_BLEND_R','ORION_TAIL_L','ORION_TAIL_R']]
  for mo in moving:
   if mo.type!='MESH':continue
   mt=tree(mo)
   for ob in obstacles:
    hit=mt.overlap(tree(ob))
    if hit:contacts.append({'control':name,'degrees':value,'moving':mo.name,'obstacle':ob.name,'pairs':len(hit)})
 root[prop]=0.;root.update_tag();bpy.context.view_layer.update()
gear_hits=[]
externals=[o for o in bpy.data.collections['ORION_EXTERIOR_DETAILS_R3'].objects if o.type=='MESH'];et={o.name:tree(o) for o in externals}
for fr in range(1,161):
 s.frame_set(fr)
 for mo in bpy.data.collections['ORION_GEAR'].objects:
  if mo.type!='MESH':continue
  mt=tree(mo)
  for n,t in et.items():
   hit=mt.overlap(t)
   if hit:gear_hits.append({'frame':fr,'gear':mo.name,'exterior':n,'pairs':len(hit)})
s.frame_set(1)
evaluated=[defects(bpy.data.objects[n],True) for n in ['ORION_FUSELAGE','ORION_REAR_DORSAL_INTAKE_SHELL','ORION_FORWARD_UNDERSIDE_APERTURE_FAIRING']]
arm=bpy.data.objects['ORION_EXPORT_ARMATURE'];bone_errors=[]
for bone in arm.pose.bones:
 if not bone.constraints:continue
 c=bone.constraints[0];m=arm.matrix_world@bone.matrix;err=max(abs(m[i][j]-c.target.matrix_world[i][j]) for i in range(4) for j in range(4))
 if err>1e-5:bone_errors.append({'bone':bone.name,'matrix_error':err})
dest=Path(tempfile.mkdtemp(prefix='Orion_E_reopen_'));(dest/'Orion').mkdir();shutil.copy2(P/'Orion/Orion_Master.blend',dest/'Orion/Orion_Master.blend');shutil.copytree(P/'Support/references_private',dest/'Support/references_private')
probe=dest/'probe.py';probe.write_text("import bpy\nfrom pathlib import Path\np=Path(__file__).parent\nbpy.ops.wm.open_mainfile(filepath=str(p/'Orion/Orion_Master.blend'))\nassert all(Path(bpy.path.abspath(i.filepath)).exists() for i in bpy.data.images if i.source=='FILE')\nassert len(bpy.data.objects['ORION_EXPORT_ARMATURE'].data.bones)==23\nprint('E_RELOCATED_REOPEN_OK')\n")
result=subprocess.run([bpy.app.binary_path,'--background','--python',str(probe)],capture_output=True,text=True,timeout=60)
report={'fresh_master_reopen':True,'all_prior_mesh_vertex_arrays_preserved':all(old[n]==digest(bpy.data.objects[n]) for n in old),'base_mesh_defects':bad,'evaluated_mesh_checks':evaluated,'control_motion_checks':motion,'control_surface_sensor_propeller_surface_contacts':contacts,'gear_to_new_exterior_contacts_all_160_frames':gear_hits,'bone_target_matrix_errors':bone_errors,'relocated_reopen':result.returncode==0 and 'E_RELOCATED_REOPEN_OK' in result.stdout,'engine_validation':'NOT ATTEMPTED','clips_and_weights':'No game-copy skinning or baked engine animation yet'}
(P/f'Documentation/E_validation_{rev}.json').write_text(json.dumps(report,indent=2));print('E_VALIDATION',len(bad),'base defects',len(contacts),'pose contacts',len(gear_hits),'gear exterior contacts',len(bone_errors),'bone errors','relocation',report['relocated_reopen'])
