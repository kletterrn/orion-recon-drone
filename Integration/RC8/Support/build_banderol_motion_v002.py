from pathlib import Path
import bpy,math,json
from mathutils import Vector,Quaternion,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';dest=I/'Blender/Banderol_RC8_Motion_v002.blend'
if dest.exists():raise RuntimeError('Checkpoint exists')
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Banderol_RC8_Motion_v001.blend'));s=bpy.context.scene;s.frame_set(1)
root=bpy.data.objects['BANDEROL_VISUALFIT_ROOT'];helpers=bpy.data.collections['30_RIG_HELPERS']
controls={}
for side,label in [(-1,'L'),(1,'R')]:
 wing=bpy.data.objects[f'BDLF_WING_{label}'];M=wing.matrix_world.copy()
 ctrl=bpy.data.objects.new(f'BDLF_CTRL_WING_{label}',None);helpers.objects.link(ctrl);ctrl.parent=root;ctrl.location=(side*.114,.1125,-.163);ctrl.rotation_mode='QUATERNION';ctrl.empty_display_type='ARROWS';ctrl.empty_display_size=.1
 bpy.context.view_layer.update();wing.parent=ctrl;wing.matrix_parent_inverse=ctrl.matrix_world.inverted();wing.matrix_world=M;controls[label]=ctrl
 ctrl['evidence']='C: game-only illustrative aft fold, vertically staggered below exterior body; not a real deployment mechanism'
 for frame in range(1,32):
  deployed=(frame-1)/30;fold=1-deployed;drop=min(1,fold/.15);rot=max(0,(fold-.15)/.85)
  ctrl.location.z=-.163-(.05 if label=='L' else .10)*drop
  ctrl.rotation_quaternion=Quaternion((0,0,1),-side*math.radians(70)*rot)
  ctrl.keyframe_insert('location',frame=frame);ctrl.keyframe_insert('rotation_quaternion',frame=frame)
s.frame_end=31;s.render.fps=30
# One rigid bind per component; export geometry is a separate evaluated copy.
s.frame_set(31);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
source=[o for o in bpy.data.collections['10_SOURCE'].all_objects if o.type in {'MESH','CURVE'} and not o.hide_render]
armdata=bpy.data.armatures.new('BDL_RC8_SKELETON');arm=bpy.data.objects.new('BDL_RC8_EXPORT_RIG',armdata);helpers.objects.link(arm)
bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
rb=armdata.edit_bones.new('ORD_Root');rb.head=(0,0,0);rb.tail=(0,.2,0)
for label,ctrl in controls.items():
 b=armdata.edit_bones.new('BDL_Wing_'+label);b.head=ctrl.matrix_world.translation;b.tail=b.head+Vector((0,0,.12));b.parent=rb
bpy.ops.object.mode_set(mode='OBJECT');arm.select_set(False)
exports=bpy.data.collections.new('BDL_RC8_SKINNED_SOURCE');bpy.data.collections['40_EXPORT'].children.link(exports)
mapping=[]
for o in source:
 e=o.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(e,preserve_all_data_layers=True,depsgraph=dg);mesh.transform(e.matrix_world)
 copy=bpy.data.objects.new(o.name+'_RC8_SKIN',mesh);exports.objects.link(copy)
 bone='BDL_Wing_'+o.name[-1] if o.name in ['BDLF_WING_L','BDLF_WING_R'] else 'ORD_Root'
 g=copy.vertex_groups.new(name=bone);g.add(list(range(len(mesh.vertices))),1,'REPLACE')
 mod=copy.modifiers.new('RC8_rigid_skin','ARMATURE');mod.object=arm;copy.parent=arm;copy.hide_render=True;copy.hide_set(True)
 mapping.append({'source':o.name,'export':copy.name,'bone':bone,'vertices':len(mesh.vertices)})
for label,ctrl in controls.items():
 b=arm.pose.bones['BDL_Wing_'+label];c=b.constraints.new('COPY_TRANSFORMS');c.target=ctrl;c.target_space='WORLD';c.owner_space='WORLD'
 # Blender bone local Y points along the hinge shaft, whereas control local Z does.
 # Copy world location/rotation through a rest-basis helper so the skin is identity when deployed.
 b.constraints.remove(c)
 follow=bpy.data.objects.new('BDLF_BIND_FOLLOW_'+label,None);helpers.objects.link(follow);follow.parent=ctrl
 follow.matrix_parent_inverse=ctrl.matrix_world.inverted();follow.matrix_world=arm.matrix_world@b.bone.matrix_local
 c=b.constraints.new('COPY_TRANSFORMS');c.target=follow;c.target_space='WORLD';c.owner_space='WORLD'
s.frame_set(1);s['RC8_status']='Illustrative deployment candidate; rigid skin created; engine import not tested'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
(I/'Reports/banderol_skin_mapping_v002.json').write_text(json.dumps(mapping,indent=2))
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return BVHTree.FromPolygons(v,f)
body=tree(bpy.data.objects['BDLF_BODY']);contacts=[]
for frame in range(1,32):
 s.frame_set(frame);wings=[tree(bpy.data.objects['BDLF_WING_'+l]) for l in ['L','R']]
 for i,l in enumerate(['L','R']):
  if wings[i].overlap(body):contacts.append({'frame':frame,'a':'WING_'+l,'b':'BODY'})
 if wings[0].overlap(wings[1]):contacts.append({'frame':frame,'a':'WING_L','b':'WING_R'})
(I/'Reports/banderol_deployment_v002.json').write_text(json.dumps({'status':'candidate; root fairing interfaces still require inspection','wing_body_or_wing_wing_contacts':contacts,'sampled_frames':31,'duration_seconds':1},indent=2))
print('BDL_RC8_DEPLOYMENT_CONTACTS',contacts,flush=True)
print('BDL_RC8_MOTION_V002_COMPLETE',flush=True)
