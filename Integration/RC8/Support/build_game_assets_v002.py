"""Build real skinned LODs and transfer source shading onto unique game UVs."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Matrix
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
label=args[0] if args else 'Orion';source_revision=args[1] if len(args)>1 else 'v003';game_revision=args[2] if len(args)>2 else ''
T=I/'GameSources'/('textures_'+game_revision if game_revision else 'textures');T.mkdir(parents=True,exist_ok=True)
file,col,rig,targets=(f'Orion_RC8_Skinned_{source_revision}.blend','ORION_RC8_SKINNED_SOURCE','ORD_RC8_ExportRig',[200000,80000,30000,8000]) if label=='Orion' else ('Banderol_RC8_Motion_v004.blend','BDL_RC8_SKINNED_SOURCE','BDL_RC8_EXPORT_RIG',[35000,12000,4000,1000])
save=I/'GameSources'/(label+'_RC8_Game'+('_'+game_revision if game_revision else '')+'.blend')
if game_revision and save.exists():raise RuntimeError('Preserve existing game checkpoint: '+str(save))
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
def tris(o):return sum(len(p.vertices)-2 for p in o.data.polygons)
def active_only(objects,active):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=active
for group,objs in groups.items():
 active_only(objs,objs[0]);bpy.ops.object.join();joined=bpy.context.object;joined.name=group+'_HIGH';groups[group]=[joined]
base=sum(tris(o) for objs in groups.values() for o in objs);ratio=min(1,targets[0]/base)
print('BUILD',label,base,'groups',list(groups),flush=True)
low0=[]
for group,objects in groups.items():
 copies=[]
 for o in objects:
  q=o.copy();q.data=o.data.copy();low.objects.link(q);q.name=o.name+'_GAME';q.hide_set(False);q.hide_render=False
  if tris(q)>24 and ratio<1:
   active_only([q],q);d=q.modifiers.new('LOD0 silhouette reduction','DECIMATE');d.ratio=ratio;d.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=d.name)
  copies.append(q)
 active_only(copies,copies[0]);bpy.ops.object.join();q=bpy.context.object;q.name=group+'_LOD0';low0.append(q)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.003,area_weight=.2,correct_aspect=True);bpy.ops.object.mode_set(mode='OBJECT')
 # Each target uses a unique atlas. Source UVs/materials remain on the high meshes.
 mat=bpy.data.materials.new('RC8_'+group);mat.use_nodes=True;q.data.materials.clear();q.data.materials.append(mat)
 for p in q.data.polygons:p.material_index=0
 report['groups'][group]={'triangles':tris(q),'source_meshes':len(objects),'resolution':4096}
# Bake only the active group; independently articulated parts keep their own silhouette.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.render.bake.use_selected_to_active=True;s.render.bake.cage_extrusion=.015;s.render.bake.max_ray_distance=.08;s.render.bake.margin=16;s.render.bake.use_clear=True
for objects in groups.values():
 for o in objects:o.hide_render=True
for q in low0:q.hide_render=True
for group,objects in groups.items():
 q=next(o for o in low0 if o.name==group+'_LOD0');mat=q.data.materials[0];nt=mat.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');images={}
 for o in objects:o.hide_render=False
 q.hide_render=False
 for channel in ['BaseColor','Roughness','Metallic','Normal','AO']:
  path=T/(group+'_'+channel+'.png');img=bpy.data.images.new(group+'_'+channel,4096,4096,alpha=False);img.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color';img.filepath_raw=str(path);img.file_format='PNG';node=nt.nodes.new('ShaderNodeTexImage');node.image=img;nt.nodes.active=node;node.select=True
  changes=[]
  if channel in ['BaseColor','Roughness','Metallic']:
   key={'BaseColor':'Base Color','Roughness':'Roughness','Metallic':'Metallic'}[channel]
   for m in {m for o in objects for m in o.data.materials if m and m.use_nodes}:
    tree=m.node_tree;out=next((n for n in tree.nodes if n.type=='OUTPUT_MATERIAL'),None);b=next((n for n in tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not out or not b:continue
    oldlink=out.inputs['Surface'].links[0].from_socket if out.inputs['Surface'].is_linked else None
    em=tree.nodes.new('ShaderNodeEmission');inp=b.inputs[key]
    if inp.is_linked:tree.links.new(inp.links[0].from_socket,em.inputs['Color'])
    else:
     v=inp.default_value;em.inputs['Color'].default_value=v if channel=='BaseColor' else (v,v,v,1)
    tree.links.new(em.outputs[0],out.inputs['Surface']);changes.append((tree,out,oldlink,em))
  active_only(objects+[q],q);print('BAKE_BEGIN',group,channel,flush=True)
  bpy.ops.object.bake(type='EMIT' if changes else channel.upper())
  img.save();images[channel]=img
  for tree,out,oldlink,em in changes:
   tree.nodes.remove(em)
   if oldlink:tree.links.new(oldlink,out.inputs['Surface'])
  report['bakes'].append({'group':group,'channel':channel,'file':str(path),'actual_selected_to_active':True})
  print('BAKE_DONE',group,channel,flush=True)
 for channel,socket in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic')]:
  n=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image==images[channel]);nt.links.new(n.outputs['Color'],bsdf.inputs[socket])
 n=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image==images['Normal']);nm=nt.nodes.new('ShaderNodeNormalMap');nt.links.new(n.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],bsdf.inputs['Normal'])
 for o in objects:o.hide_render=True
 q.hide_render=True
 (I/'Reports'/(label.lower()+'_game_build'+('_'+game_revision if game_revision else '')+'.json')).write_text(json.dumps(report,indent=2))
# LOD reductions preserve disconnected parts and their rigid bone assignments.
for level,target in enumerate(targets):
 meshes=low0 if level==0 else []
 if level:
  for baseq in low0:
   q=baseq.copy();q.data=baseq.data.copy();low.objects.link(q);q.name=baseq.name.replace('_LOD0','_LOD'+str(level));active_only([q],q);d=q.modifiers.new('LOD reduction','DECIMATE');d.ratio=target/sum(tris(o) for o in low0);d.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=d.name);meshes.append(q)
 for q in meshes:
  mod=q.modifiers.new('Rigid skin','ARMATURE');mod.object=arm;q.parent=arm;q.hide_render=level!=0;q.hide_set(level!=0)
 report['lod_triangles'].append(sum(tris(o) for o in meshes))
for objs in groups.values():
 for o in objs:o.hide_render=True;o.hide_set(True)
for o in low0:o.hide_render=False;o.hide_set(False)
s.render.engine='CYCLES';bpy.context.preferences.filepaths.save_version=0
# Preserve editable bake source but remove unrelated scenes and private reference dependencies.
for scene in list(bpy.data.scenes):
 if scene!=s:bpy.data.scenes.remove(scene)
bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(save),relative_remap=True)
report['status']='built and baked; native import and visual inspection pending';(I/'Reports'/(label.lower()+'_game_build'+('_'+game_revision if game_revision else '')+'.json')).write_text(json.dumps(report,indent=2));print('GAME_BUILD_DONE',report['lod_triangles'],flush=True)
