from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Banderol_RC8_Motion_v003.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Banderol_RC8_Motion_v002.blend'));s=bpy.context.scene;s.frame_set(31)
root=bpy.data.objects['BANDEROL_VISUALFIT_ROOT'];root['deployment']=1.0;root.id_properties_ui('deployment').update(min=0,max=1,description='0 carried aft-fold pose; 1 approved deployed pose. Illustrative game motion.')
for side,label in [(-1,'L'),(1,'R')]:
 ctrl=bpy.data.objects['BDLF_CTRL_WING_'+label]
 if ctrl.animation_data and ctrl.animation_data.action:ctrl.animation_data.action.use_fake_user=True
 ctrl.animation_data_clear()
 for path,index,expr in [('location',2,f'-.163-{.05 if label=="L" else .10}*min(1,(1-d)/.15)'),('rotation_quaternion',0,f'cos({math.radians(70)/2}*max(0,(1-d-.15)/.85))'),('rotation_quaternion',3,f'sin({-side*math.radians(70)/2}*max(0,(1-d-.15)/.85))')]:
  fc=ctrl.driver_add(path,index);dr=fc.driver;dr.expression=expr;v=dr.variables.new();v.name='d';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["deployment"]'
source=bpy.data.collections['10_SOURCE'];arm=bpy.data.objects['BDL_RC8_EXPORT_RIG'];exports=bpy.data.collections['BDL_RC8_SKINNED_SOURCE']
mat=bpy.data.materials.new('BDLF_RC8_HINGE_SATIN');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.24,.26,.27,1);bs.inputs['Metallic'].default_value=.5;bs.inputs['Roughness'].default_value=.45
for side,label in [(-1,'L'),(1,'R')]:
 for kind,depth,radius,z in [('PIN',.078 if label=='L' else .128,.012,-.184 if label=='L' else -.209),('COLLAR',.009,.033,-.163)]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=(side*.114,.1125,z));o=bpy.context.object;o.name=f'BDLF_RC8_VISUAL_HINGE_{kind}_{label}'
  for c in list(o.users_collection):c.objects.unlink(o)
  source.objects.link(o);o.data.materials.append(mat);o['evidence']='C illustrative exterior hinge detail, no functional mechanism claim'
  M=o.matrix_world.copy();o.parent=root if kind=='PIN' else bpy.data.objects['BDLF_CTRL_WING_'+label];o.matrix_parent_inverse=o.parent.matrix_world.inverted();o.matrix_world=M
  mesh=o.data.copy();mesh.transform(M);copy=bpy.data.objects.new(o.name+'_RC8_SKIN',mesh);exports.objects.link(copy);copy.parent=arm
  bone='ORD_Root' if kind=='PIN' else 'BDL_Wing_'+label;vg=copy.vertex_groups.new(name=bone);vg.add(list(range(len(mesh.vertices))),1,'REPLACE');mod=copy.modifiers.new('Rigid_skin','ARMATURE');mod.object=arm;copy.hide_render=True
mapping=[]
for o in exports.objects:
 o.hide_set(False);mapping.append({'source':o.name.removesuffix('_RC8_SKIN'),'export':o.name,'bone':o.vertex_groups[0].name,'vertices':len(o.data.vertices)})
def geo(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
errors=[];contacts=[];interfaces=[]
for step in range(61):
 root['deployment']=step/60;root.update_tag();bpy.context.view_layer.update()
 verts={};trees={};faces={}
 for n in ['BDLF_BODY','BDLF_WING_L','BDLF_WING_R']:
  v,f=geo(bpy.data.objects[n]);verts[n]=v;faces[n]=f;trees[n]=BVHTree.FromPolygons(v,f)
 for label in ['L','R']:
  name='BDLF_WING_'+label;hits=trees[name].overlap(trees['BDLF_BODY'])
  for a,b in hits:
   # Approved root insertion is an intentional interface, not a swept blade/body crossing.
   centre=sum((verts[name][j] for j in faces[name][a]),Vector())/len(faces[name][a]);hinge=bpy.data.objects['BDLF_CTRL_WING_'+label].matrix_world.translation
   row={'deployment':step/60,'wing':label,'distance_from_hinge':(centre-hinge).length}
   (interfaces if (centre-hinge).length<.21 else contacts).append(row)
  source_v,_=geo(bpy.data.objects[name]);skin_v,_=geo(bpy.data.objects[name+'_RC8_SKIN'])
  err=max((a-b).length for a,b in zip(source_v,skin_v))
  if err>1e-5:errors.append({'deployment':step/60,'wing':label,'max_error_m':err})
 if trees['BDLF_WING_L'].overlap(trees['BDLF_WING_R']):contacts.append({'deployment':step/60,'pair':'wing-wing'})
for o in exports.objects:o.hide_set(True)
root['deployment']=0;root.update_tag();bpy.context.view_layer.update();s.frame_set(1)
s['RC8_status']='v003 property-driven deployment and rigid skin; engine import pending'
s['deployment_usage']='Set BANDEROL_VISUALFIT_ROOT deployment from 0 to 1. Saved source actions retained as motion reference only.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
(I/'Reports/banderol_motion_v003.json').write_text(json.dumps({'deployment_samples':61,'unexpected_contacts':contacts,'root_interface_samples':interfaces,'skin_pose_errors':errors,'skin_mapping':mapping,'engine_import':'not attempted'},indent=2))
print('BDL_V003_CHECK',len(contacts),'contacts',len(errors),'skin errors',flush=True)
