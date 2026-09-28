from pathlib import Path
import ast,bpy,json
P=Path(__file__).resolve().parents[1]
# Share tested bake functions without executing the standalone asset loop.
tree=ast.parse((P/'Support/build_I_uv_materials_v001.py').read_text())
keep=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='reports' for t in node.targets):break
 keep.append(node)
exec(compile(ast.Module(body=keep,type_ignores=[]),'I_bake_helpers','exec'))
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
objects=[o for o in bpy.data.collections['ASSEMBLY_COMPACT_VISUAL_PYLON'].all_objects if o.type=='MESH']
before={o.name:digest(o) for o in objects}
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=16
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
folder=P/'Assembly/textures/I_v001';folder.mkdir(parents=True,exist_ok=True)
r=bake_set('Assembly_Pylon',objects,folder)
assert all(digest(o)==before[o.name] for o in objects)
r['geometry_preserved']=True
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath))
s.camera=bpy.data.objects['H_SIDE'];s['material_stage']='I v001: independent materialized sources and baked compact exterior pylon'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_I_materials_v001.blend'),copy=True,relative_remap=True)
(P/'Documentation/I_pylon_v001.json').write_text(json.dumps(r,indent=2))
print('I_PYLON_COMPLETE',flush=True)
