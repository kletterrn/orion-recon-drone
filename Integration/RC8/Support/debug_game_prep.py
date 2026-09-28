"""Build real skinned LODs and transfer source shading onto unique game UVs."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Matrix
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';T=I/'GameSources/textures';T.mkdir(parents=True,exist_ok=True)
label=sys.argv[-1] if sys.argv[-1] in ['Orion','Banderol'] else 'Orion'
file,col,rig,targets=('Orion_RC8_Skinned_v003.blend','ORION_RC8_SKINNED_SOURCE','ORD_RC8_ExportRig',[200000,80000,30000,8000]) if label=='Orion' else ('Banderol_RC8_Motion_v004.blend','BDL_RC8_SKINNED_SOURCE','BDL_RC8_EXPORT_RIG',[35000,12000,4000,1000])
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender'/file));old=bpy.context.scene;old.frame_set(1);arm=bpy.data.objects[rig];src=list(bpy.data.collections[col].objects)
fold_bind={}
if label=='Banderol':
 bpy.context.view_layer.update();fold_bind={p.name:p.matrix.copy() for p in arm.pose.bones}
for p in arm.pose.bones:
 for c in list(p.constraints):p.constraints.remove(c)
 p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
s=bpy.data.scenes.new(label+'_RC8_Game');bpy.context.window.scene=s;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.collection.objects.link(arm);arm.hide_set(False);arm.hide_render=False
high=bpy.data.collections.new('10_BAKE_SOURCE');s.collection.children.link(high);low=bpy.data.collections.new('20_GAME_LODS');s.collection.children.link(low)
groups={};report={'asset':label,'groups':{},'lod_triangles':[],'bakes':[]}
for o in src:
 if o.type!='MESH':continue
 group=label+'_Equipment'
 for m in o.data.materials:
  if m and '__I_' in m.name:group=m.name.split('__I_')[-1].split('.')[0];break
 if label=='Banderol' and group=='Banderol_Equipment':group='Banderol_Details'
 q=o.copy()
 if label=='Banderol':
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());q.data=bpy.data.meshes.new_from_object(e,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());q.data.transform(e.matrix_world);q.parent=None;q.matrix_world=Matrix.Identity(4)
 else:q.data=o.data.copy()
 high.objects.link(q);q.hide_set(False);q.hide_render=False
 for mod in list(q.modifiers):q.modifiers.remove(mod)
 vg=q.vertex_groups.new(name='RC8_SRC_'+o.name.removesuffix('_RC8_SKIN'));vg.add(list(range(len(q.data.vertices))),1,'REPLACE')
 groups.setdefault(group,[]).append(q)
if fold_bind:
 bpy.context.view_layer.objects.active=arm;arm.hide_set(False);bpy.ops.object.mode_set(mode='EDIT')
 for name,M in fold_bind.items():
  b=arm.data.edit_bones[name];b.head=(0,0,0);b.tail=(0,.08,0);b.matrix=M
 bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()

for grp,os in groups.items():
 for ob in os:
  for bn in ["BDL_Wing_L","BDL_Wing_R"]:
   g=ob.vertex_groups.get(bn)
   if not g:continue
   p=[]
   for v in ob.data.vertices:
    try:g.weight(v.index);p.append(ob.matrix_world@v.co)
    except RuntimeError:pass
   print("AT_PRE_JOIN",grp,bn,len(p),[min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)],flush=True)
