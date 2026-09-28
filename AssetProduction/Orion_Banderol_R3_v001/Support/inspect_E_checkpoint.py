from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_E_exterior_rig_v005.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1)
assert s['revision']=='E_v005'
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not Path(bpy.path.abspath(i.filepath)).exists()]
assert not missing
root=bpy.data.objects['ORION_ROOT'];arm=bpy.data.objects['ORION_EXPORT_ARMATURE']
root['propeller_degrees']=45.;root['sensor_yaw_degrees']=25.;root.update_tag();bpy.context.view_layer.update()
errors=[]
for b in arm.pose.bones:
 if b.constraints:
  target=b.constraints[0].target.matrix_world;actual=arm.matrix_world@b.matrix
  err=max(abs(actual[i][j]-target[i][j]) for i in range(4) for j in range(4))
  if err>1e-5:errors.append((b.name,err))
assert not errors
root['propeller_degrees']=0.;root['sensor_yaw_degrees']=0.;root.update_tag();bpy.context.view_layer.update()
manifest=json.loads((P/'Documentation/source_manifest.json').read_text())
old_ok=all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in manifest['existing_asset_sha256'].items())
assert old_ok
report={'numbered_checkpoint_fresh_reopen':True,'reference_dependencies_found':True,'old_assets_sha256_unchanged':old_ok,'posed_bone_matrix_errors':errors,'source_objects':len(bpy.data.collections['10_SOURCE'].all_objects),'bones':len(arm.data.bones),'saved_by_this_inspection':False}
(P/'Documentation/E_checkpoint_reopen_v005.json').write_text(json.dumps(report,indent=2))
s.cycles.samples=32;s.render.resolution_x=1300;s.render.resolution_y=1000;s.render.resolution_percentage=100
camdata=bpy.data.cameras.new('E_INTAKE_INSPECTION');cam=bpy.data.objects.new('E_INTAKE_INSPECTION',camdata);s.collection.objects.link(cam);cam.location=(.7,-2.15,1.5);cam.rotation_euler=(Vector((0,-3.10,.4))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.85;s.camera=cam
bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=True
s.render.filepath=str(P/'Previews/E_v005_Rear_Intake.png');bpy.ops.render.render(write_still=True)
print('E_CHECKPOINT_REOPEN_OK',report)
