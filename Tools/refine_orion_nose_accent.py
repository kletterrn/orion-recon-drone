"""Apply the curved decal correction to the saved model and refresh affected views."""
import ast, json, math
from pathlib import Path
import bpy, bmesh

root=Path(__file__).resolve().parent
out=root.parent/'Assets/ORD/Models/OrionE_Detailed'
bpy.ops.wm.open_mainfile(filepath=str(out/'OrionE_Detailed.blend'))
for file,functions,variables in [
 ('build_orion_e_detailed.py',{'profile'},{'stations','SECTION_X_POWER','SECTION_UPPER_POWER','SECTION_LOWER_POWER'}),
 ('orion_exhibition_details.py',{'surface_point','path_resample','nose_accent_geometry'},set())]:
 tree=ast.parse((root/file).read_text(encoding='utf-8'))
 nodes=[n for n in tree.body if (isinstance(n,ast.FunctionDef) and n.name in functions) or
        (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in variables for t in n.targets))]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),file,'exec'),globals())
for obj in [o for o in bpy.data.objects if o.name.startswith('Curved graphite nose underside accent')]:
 side=1 if sum(v.co.x for v in obj.data.vertices)>0 else -1
 verts,faces=nose_accent_geometry(side)
 data=bpy.data.meshes.new(obj.name+' conforming surface');data.from_pydata(verts,[],faces);data.update()
 for material in obj.data.materials:data.materials.append(material)
 obj.data=data
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 for p in data.polygons:p.use_smooth=True
scene=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OrionE_Detailed.blend'))
stats={'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'base_polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'file':str(out/'OrionE_Detailed.blend')}
(out/'asset_statistics.json').write_text(json.dumps(stats,indent=2))
for camera,name in [('02 | NOSE DETAIL','Nose_Detail'),('07 | REFERENCE ANGLE','Reference_Angle'),('01 | HERO','Hero'),('04 | SIDE','Side'),('06 | FORWARD PROFILE','Forward_Profile')]:
 scene.camera=bpy.data.objects[camera]
 scene.render.resolution_x=1920 if name in ['Side','Forward_Profile'] else 3840
 scene.render.resolution_y=int(scene.render.resolution_x*2/3)
 scene.cycles.samples=96
 for ground in ['Studio ground','Studio curved backdrop']:bpy.data.objects[ground].hide_render=name in ['Side','Forward_Profile']
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['01 | HERO']
for ground in ['Studio ground','Studio curved backdrop']:bpy.data.objects[ground].hide_render=False
scene.render.resolution_x=3840;scene.render.resolution_y=2560
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OrionE_Detailed.blend'))
print('NOSE_ACCENT_REFINEMENT_COMPLETE',flush=True)
