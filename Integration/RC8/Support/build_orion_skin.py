"""Versioned evaluated game copy. Component ownership comes from the actual source hierarchy."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';out=W/'Assets/ORD/Models/RC8';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Motion_v017.blend'));s=bpy.context.scene;s.frame_set(1)
source=bpy.data.collections['ORION_ASSET'];root=bpy.data.objects['ORION_ROOT']
aliases={'ORION_CTRL_PROPELLER':'ORD_Propeller','ORION_CTRL_AILERON_L':'ORD_Aileron_L','ORION_CTRL_AILERON_R':'ORD_Aileron_R','ORION_CTRL_FLAP_L':'ORD_Flap_L','ORION_CTRL_FLAP_R':'ORD_Flap_R','ORION_CTRL_RUDDERVATOR_L':'ORD_Tail_L','ORION_CTRL_RUDDERVATOR_R':'ORD_Tail_R','ORION_SENSOR_YAW':'ORD_SensorYaw','ORION_SENSOR_PITCH':'ORD_SensorPitch','ORION_CTRL_NOSE_WHEEL_SPIN':'front_wheel','ORION_CTRL_MAIN_L_WHEEL_SPIN':'rear_wheel_l','ORION_CTRL_MAIN_R_WHEEL_SPIN':'rear_wheel_r'}
controllers=[o for o in source.all_objects if (o.type=='EMPTY' and o.name not in ['ORION_ROOT','ORION_PAYLOAD_SOCKET'] and not o.name.startswith('ORION_REF_')) or (o.type=='MESH' and o.animation_data and o.animation_data.action)]
controllers=sorted({o.name:o for o in controllers}.values(),key=lambda o:o.name)
names={o.name:aliases.get(o.name,o.name.replace('ORION_','ORD_').replace('-1','Minus').replace('.','_')) for o in controllers}
rest={o.name:o.matrix_world.copy() for o in controllers}
export=bpy.data.collections.new('ORION_RC8_SKINNED_SOURCE');bpy.data.collections['40_EXPORT'].children.link(export)
armdata=bpy.data.armatures.new('ORD_RC8_Skeleton');arm=bpy.data.objects.new('ORD_RC8_ExportRig',armdata);export.objects.link(arm);bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
rb=armdata.edit_bones.new('ORD_Root');rb.head=(0,0,0);rb.tail=(0,.1,0)
for o in controllers:
 b=armdata.edit_bones.new(names[o.name]);b.head=(0,0,0);b.tail=(0,.08,0);b.matrix=rest[o.name].normalized();b.parent=rb
helpers={'ORION_PAYLOAD_SOCKET':Matrix.Translation((0,-1.26,-.86)),'ORD_EngineAudio':Matrix.Translation((0,-3.25,.05))}
for label,bone in [('NOSE','front_wheel'),('MAIN_L','rear_wheel_l'),('MAIN_R','rear_wheel_r')]:
 ctrl=bpy.data.objects[f'ORION_CTRL_{label}_WHEEL_SPIN'];helpers[bone+'_contact']=Matrix.Translation(ctrl.matrix_world.translation)
# Contact helpers are wheel centres as required by the existing PFC wheel-radius convention.
# View marker is the centre of the forward optical assembly; runtime aim remains independent.
helpers['ORD_SensorView']=bpy.data.objects['ORION_SENSOR_PITCH'].matrix_world.copy()
for n,M in helpers.items():b=armdata.edit_bones.new(n);b.head=(0,0,0);b.tail=(0,.06,0);b.matrix=M;b.parent=rb
bpy.ops.object.mode_set(mode='OBJECT')
mapping=[];copies=[]
for o in source.all_objects:
 if o.type not in {'MESH','CURVE'} or o.hide_render:continue
 bone='ORD_Root';ancestor=o
 while ancestor:
  if ancestor.name in names:bone=names[ancestor.name];break
  ancestor=ancestor.parent
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(e,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());mesh.transform(e.matrix_world)
 copy=bpy.data.objects.new(o.name+'_RC8_SKIN',mesh);export.objects.link(copy);copy.parent=arm;vg=copy.vertex_groups.new(name=bone);vg.add(list(range(len(mesh.vertices))),1,'REPLACE');mod=copy.modifiers.new('Rigid_skin','ARMATURE');mod.object=arm;copies.append(copy);mapping.append(dict(source=o.name,export=copy.name,bone=bone,vertices=len(mesh.vertices)))
# The approved visible adapter stays with Orion after launch.
with bpy.data.libraries.load(str(I/'Blender/Assembly_RC8_Motion_v012.blend'),link=False) as (a,b):b.collections=['ASSEMBLY_COMPACT_VISUAL_PYLON']
pylon=b.collections[0];s.collection.children.link(pylon);bpy.context.view_layer.update()
for o in pylon.all_objects:
 if o.type!='MESH' or o.hide_render:continue
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(e,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());mesh.transform(e.matrix_world);copy=bpy.data.objects.new(o.name+'_RC8_SKIN',mesh);export.objects.link(copy);copy.parent=arm;vg=copy.vertex_groups.new(name='ORD_Root');vg.add(list(range(len(mesh.vertices))),1,'REPLACE');mod=copy.modifiers.new('Rigid_skin','ARMATURE');mod.object=arm;copies.append(copy);mapping.append(dict(source=o.name,export=copy.name,bone='ORD_Root',vertices=len(mesh.vertices)))
for o in controllers:
 c=arm.pose.bones[names[o.name]].constraints.new('COPY_TRANSFORMS');c.target=o;c.target_space='WORLD';c.owner_space='WORLD'
frames=[];errors=[]
for frame in range(1,121):
 s.frame_set(frame);bpy.context.view_layer.update();frames.append({names[o.name]:[list(row) for row in o.matrix_world] for o in controllers})
 if frame in [1,31,63,100,120]:
  for row in mapping:
   if row['source'] not in source.all_objects:continue
   src=bpy.data.objects[row['source']];dst=bpy.data.objects[row['export']];a=src.evaluated_get(bpy.context.evaluated_depsgraph_get());b=dst.evaluated_get(bpy.context.evaluated_depsgraph_get());am=a.to_mesh();bm=b.to_mesh()
   if len(am.vertices)==len(bm.vertices):err=max(((a.matrix_world@v.co-b.matrix_world@w.co).length for v,w in zip(am.vertices,bm.vertices)),default=0)
   else:err=999
   a.to_mesh_clear();b.to_mesh_clear()
   if err>1e-4:errors.append(dict(frame=frame,source=src.name,error_m=err))
s.frame_set(1);bpy.context.view_layer.update()
report=dict(source='Orion_RC8_Motion_v017.blend',bones=names,rest={names[n]:[list(r) for r in M] for n,M in rest.items()},helpers={n:[list(r) for r in M] for n,M in helpers.items()},mapping=mapping,skin_pose_errors=errors,gear_frames=frames,notes=['Rigid skin, all animated bones children of ORD_Root; sampled model-space poses preserve source articulation.','Helper engine audio position is a presentation emitter, not an engineering datum.'])
(I/'Reports/orion_skin_v002.json').write_text(json.dumps(report,indent=2))
for o in copies:o.hide_render=True;o.hide_set(True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(I/'Blender/Orion_RC8_Skinned_v002.blend'),relative_remap=True)
print('ORION_SKIN_COMPLETE',len(copies),len(names),len(errors),'pose errors',flush=True)
