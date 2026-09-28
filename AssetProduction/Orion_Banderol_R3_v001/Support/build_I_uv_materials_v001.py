from pathlib import Path
import bpy,json,hashlib,math,time
from mathutils import Vector
P=Path(__file__).resolve().parents[1];RES=4096
def digest(o):return hashlib.sha256(str(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
def classify(o,gear):
 n=o.name
 if n in gear:return 'Gear_Bays'
 if 'SENSOR' in n or 'OPTIC' in n:return 'Sensor'
 if any(p in n for p in ['WING','FLAP','AILERON']) and n.endswith('_L'):return 'Wing_L'
 if any(p in n for p in ['WING','FLAP','AILERON']) and n.endswith('_R'):return 'Wing_R'
 if any(p in n for p in ['TAIL','RUDDERVATOR','PROPELLER','REAR_','SPINNER']):return 'Tail_Rear'
 return 'Airframe'
def tune(m):
 p=m.node_tree.nodes.get('Principled BSDF')
 if not p:return
 n=m.name
 if 'GREY_REVIEW' in n:p.inputs['Base Color'].default_value=(.24,.27,.29,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.46
 if 'LIGHT_GREY' in n:p.inputs['Base Color'].default_value=(.37,.395,.40,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.43
 if 'WHITE_NOSE' in n:p.inputs['Base Color'].default_value=(.80,.81,.80,1);p.inputs['Roughness'].default_value=.43;p.inputs['Metallic'].default_value=0
 if 'TIRE' in n:p.inputs['Base Color'].default_value=(.016,.018,.019,1);p.inputs['Roughness'].default_value=.79;p.inputs['Metallic'].default_value=0
 if 'BAY_INTERIOR' in n:p.inputs['Base Color'].default_value=(.15,.17,.18,1);p.inputs['Roughness'].default_value=.59
 if 'EXPOSED_SLIDING' in n:p.inputs['Metallic'].default_value=.92;p.inputs['Roughness'].default_value=.23
 if 'GEAR_SATIN' in n:p.inputs['Metallic'].default_value=.7;p.inputs['Roughness'].default_value=.38
 if 'SEAL' in n:p.inputs['Roughness'].default_value=.70;p.inputs['Metallic'].default_value=0
 if 'OPTIC' in n:p.inputs['Roughness'].default_value=.10;p.inputs['Metallic'].default_value=.05;p.inputs['Coat Weight'].default_value=.35;p.inputs['IOR'].default_value=1.46
 if n.endswith('_LENS'):p.inputs['Roughness'].default_value=.14;p.inputs['Coat Weight'].default_value=.35
def uv_unwrap(objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:
  if o.data.users>1:o.data=o.data.copy()
  o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
 bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.004,area_weight=1,correct_aspect=True,scale_to_bounds=False)
 bpy.ops.uv.average_islands_scale()
 args={'rotate':True,'margin':.004}
 props=bpy.ops.uv.pack_islands.get_rna_type().properties
 if 'margin_method' in props:args['margin_method']='FRACTION'
 if 'shape_method' in props:args['shape_method']='AABB'
 bpy.ops.uv.pack_islands(**args)
 bpy.ops.object.mode_set(mode='OBJECT')
 for o in objects:o.data.uv_layers.active.name='UV_Asset'
def image(name,kind,folder):
 i=bpy.data.images.new(name+'_'+kind,width=RES,height=RES,alpha=False,float_buffer=False)
 i.colorspace_settings.name='sRGB' if kind=='BaseColor' else 'Non-Color'
 i.file_format='PNG';i.filepath_raw=str(folder/(name+'_'+kind+'.png'));return i
def bake_set(name,objects,folder):
 print('I_UNWRAP_START',name,len(objects),flush=True)
 uv_unwrap(objects);mats=[];cache={}
 print('I_UNWRAP_COMPLETE',name,flush=True)
 for o in objects:
  for slot in o.material_slots:
   old=slot.material
   if not old:continue
   if old not in cache:
    m=old.copy();m.name=old.name+'__I_'+name;tune(m);cache[old]=m;mats.append(m)
   slot.material=cache[old]
 # Bake one evaluated temporary aggregate. Authoritative components remain separate.
 bpy.ops.object.select_all(action='DESELECT');dg=bpy.context.evaluated_depsgraph_get();copies=[]
 for o in objects:
  ev=o.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
  # new_from_object copies data slots; explicitly preserve OBJECT-linked overrides too.
  mesh.materials.clear()
  for slot in o.material_slots:mesh.materials.append(slot.material)
  tmp=bpy.data.objects.new('I_TEMP_BAKE_'+o.name,mesh);bpy.context.scene.collection.objects.link(tmp);tmp.matrix_world=ev.matrix_world.copy();tmp.select_set(True);copies.append(tmp)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();aggregate=bpy.context.object
 hidden={o:o.hide_render for o in objects}
 for o in objects:o.hide_render=True
 # Preserve physical shader graph except for temporary emission outputs during scalar baking.
 saved={}
 for m in mats:
  nt=m.node_tree;p=nt.nodes.get('Principled BSDF');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');saved[m]=(p,out,[(l.from_socket,l.to_socket) for l in nt.links if l.to_node==out])
 maps={}
 for kind in ['BaseColor','Roughness','Metallic','Normal']:
  existing=folder/(name+'_'+kind+'.png')
  if existing.exists():
   maps[kind]=bpy.data.images.load(str(existing),check_existing=False);maps[kind].colorspace_settings.name='sRGB' if kind=='BaseColor' else 'Non-Color';maps[kind].filepath=bpy.path.relpath(str(existing));print('I_REUSE_COMPLETED_MAP',name,kind,flush=True);continue
  bpy.context.scene.cycles.samples=4 if kind=='Normal' else 1
  img=image(name,kind,folder);maps[kind]=img
  temps=[]
  for m in mats:
   nt=m.node_tree;p,out,links=saved[m]
   for l in list(nt.links):
    if l.to_node==out:nt.links.remove(l)
   if kind=='Normal':
    for a,b in links:nt.links.new(a,b)
   else:
    e=nt.nodes.new('ShaderNodeEmission');temps.append((nt,e));key={'BaseColor':'Base Color','Roughness':'Roughness','Metallic':'Metallic'}[kind]
    value=p.inputs[key].default_value
    e.inputs[0].default_value=value if kind=='BaseColor' else (value,value,value,1)
    if p.inputs[key].is_linked:nt.links.new(p.inputs[key].links[0].from_socket,e.inputs[0])
    nt.links.new(e.outputs[0],out.inputs['Surface'])
   target=nt.nodes.get('I_BAKE_TARGET') or nt.nodes.new('ShaderNodeTexImage');target.name='I_BAKE_TARGET';target.image=img;nt.nodes.active=target
  bpy.ops.object.bake(type='NORMAL' if kind=='Normal' else 'EMIT',use_clear=False,margin=16)
  img.save();img.filepath=bpy.path.relpath(img.filepath_raw)
  for nt,e in temps:nt.nodes.remove(e)
  print('I_BAKE',name,kind,flush=True)
 for m in mats:
  nt=m.node_tree;p,out,links=saved[m]
  for l in list(nt.links):
   if l.to_node==out:nt.links.remove(l)
  for a,b in links:nt.links.new(a,b)
  target=nt.nodes.get('I_BAKE_TARGET')
  if target:nt.nodes.remove(target)
  for kind,img in maps.items():
   t=nt.nodes.new('ShaderNodeTexImage');t.name='I_'+kind;t.label=name+' '+kind;t.image=img
   if kind=='Normal':
    nm=nt.nodes.new('ShaderNodeNormalMap');nt.links.new(t.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
   else:nt.links.new(t.outputs['Color'],p.inputs[{'BaseColor':'Base Color','Roughness':'Roughness','Metallic':'Metallic'}[kind]])
 bpy.data.objects.remove(aggregate,do_unlink=True)
 for o,state in hidden.items():o.hide_render=state
 report={'set':name,'resolution':RES,'objects':[o.name for o in objects],'materials':[m.name for m in mats],'images':{k:i.filepath for k,i in maps.items()},'uv_loops':sum(len(o.data.loops) for o in objects),'zero_area_uv_faces':[],'uv_bounds_errors':[]}
 for o in objects:
  uv=o.data.uv_layers.active.data
  for poly in o.data.polygons:
   coords=[uv[j].uv for j in poly.loop_indices];a=abs(sum(coords[j].x*coords[(j+1)%len(coords)].y-coords[(j+1)%len(coords)].x*coords[j].y for j in range(len(coords))))*.5
   if a<1e-13:report['zero_area_uv_faces'].append([o.name,poly.index])
  if any(not(-1e-5<=l.uv.x<=1.00001 and -1e-5<=l.uv.y<=1.00001) for l in uv):report['uv_bounds_errors'].append(o.name)
 return report
reports=[]
for filename,prefix in [('Orion/Orion_Master.blend','Orion'),('Banderol/S8000_Banderol_Master.blend','BDL_Reference'),('Banderol/S8000_Banderol_VisualFit_Master.blend','BDL_VisualFit')]:
 bpy.ops.wm.open_mainfile(filepath=str(P/filename));s=bpy.context.scene;s.frame_set(1)
 source=[o for o in bpy.data.collections['10_SOURCE'].all_objects if o.type=='MESH' and not o.hide_render]
 before={o.name:digest(o) for o in source}
 for m in bpy.data.materials:
  if m.use_nodes and m.node_tree.nodes.get('Principled BSDF'):tune(m)
 if prefix=='Orion':
  gear={o.name for n in ['ORION_GEAR','ORION_GEAR_BAYS'] for o in bpy.data.collections[n].all_objects};sets={}
  for o in source:sets.setdefault(classify(o,gear),[]).append(o)
 else:
  sets={'Body':[],'Appendages':[]}
  for o in source:sets['Body' if any(k in o.name for k in ['BODY','NOSE','REAR_COWLING','REAR_OPENING','FASTENER']) else 'Appendages'].append(o)
 folder=(P/filename).parent/'textures/I_v001';folder.mkdir(parents=True,exist_ok=True)
 s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=16;s.render.bake.use_selected_to_active=False
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 asset_report={'file':filename,'sets':[],'geometry_preserved':False,'curve_materials':'Editable curves retain procedural shaders; not baked mesh geometry'}
 for group,objects in sets.items():asset_report['sets'].append(bake_set(prefix+'_'+group,objects,folder))
 assert all(digest(o)==before[o.name] for o in source)
 asset_report['geometry_preserved']=True
 s['material_stage']='I v001: UV_Asset and 4K base/roughness/metallic/tangent normal textures; no lighting baked into base colour'
 # Save source and new numbered checkpoints; previous geometry checkpoints remain intact.
 checkpoint=(P/filename).parent/'checkpoints'/(prefix+'_I_uv_materials_v001.blend')
 bpy.ops.wm.save_as_mainfile(filepath=str(P/filename));bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint),copy=True,relative_remap=True)
 reports.append(asset_report);(P/'Documentation/I_build_v001.json').write_text(json.dumps(reports,indent=2))
 print('I_ASSET_COMPLETE',filename,flush=True)
print('I_ALL_SOURCE_MATERIALS_COMPLETE')
