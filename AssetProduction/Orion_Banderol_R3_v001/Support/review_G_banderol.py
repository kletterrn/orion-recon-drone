from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,tempfile,subprocess
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'));s=bpy.context.scene;src=bpy.data.collections['10_SOURCE'];REV=s['revision'].removeprefix('G_')
bad=[];bounds=[]
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
for o in [o for o in src.objects if o.type=='MESH']:
 bm=bmesh.new();bm.from_mesh(o.data);nm=sum(not e.is_manifold for e in bm.edges);dg=sum(f.calc_area()<1e-10 for f in bm.faces);vol=bm.calc_volume(signed=True)
 if nm or dg or vol<=0:bad.append({'name':o.name,'nonmanifold':nm,'degenerate':dg,'volume':vol})
 bm.free();bounds += [o.matrix_world@v.co for v in o.data.vertices]
body=bpy.data.objects['BDL_BODY'];bt=tree(body);interfaces={n:bool(tree(bpy.data.objects[n]).overlap(bt)) for n in ['BDL_WING_L','BDL_WING_R','BDL_WING_ROOT_FAIRING_L','BDL_WING_ROOT_FAIRING_R','BDL_TAIL_L','BDL_TAIL_R','BDL_TAIL_TOP']}
length=max(v.y for v in bounds)-min(v.y for v in bounds);span=max(v.x for v in bounds)-min(v.x for v in bounds);diam=body.dimensions.x
assert abs(length-5)<1e-5 and abs(diam-.3)<1e-5
manifest=json.loads((P/'Documentation/source_manifest.json').read_text());unchanged=all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in manifest['existing_asset_sha256'].items())
report={'fresh_master_open':True,'source_objects':len(src.objects),'source_meshes':len([o for o in src.objects if o.type=='MESH']),'source_curves':len([o for o in src.objects if o.type=='CURVE']),'base_mesh_defects':bad,'length_m':length,'body_width_m':diam,'wing_span_provisional_m':span,'intentional_connected_interfaces':interfaces,'original_mod_assets_unchanged':unchanged,'material_external_images':len([i for i in bpy.data.images if i.source=='FILE']),'game_validation':'NOT ATTEMPTED','proportions':'Nominal public dimensions; illustrated sections, wing span and local layout C'}
# Reopen the numbered source in a separate process and verify standalone paths/collections.
probe=P/'Support/G_reopen_probe.py';probe.write_text("import bpy\nfrom pathlib import Path\np=Path(__file__).resolve().parents[1]\nbpy.ops.wm.open_mainfile(filepath=str(p/'Banderol/checkpoints/S8000_Banderol_G_wings_v003.blend'))\nassert bpy.data.scenes['BANDEROL_GEOMETRY_REVIEW']['revision']=='G_v003'\nassert 'BANDEROL_ROOT' in bpy.data.objects\nassert 'ORION_ROOT' not in bpy.data.objects\nassert len(bpy.data.collections['10_SOURCE'].objects)>11\nprint('G_STANDALONE_REOPEN_OK')\n")
r=subprocess.run([bpy.app.binary_path,'--background','--python',str(probe)],capture_output=True,text=True,timeout=60);report['fresh_standalone_checkpoint_open']=r.returncode==0 and 'G_STANDALONE_REOPEN_OK' in r.stdout
(P/f'Documentation/G_validation_{REV}.json').write_text(json.dumps(report,indent=2));print('G_CHECKS',report)
clay=bpy.data.materials.get('BDL_NEUTRAL_CLAY') or bpy.data.materials.new('BDL_NEUTRAL_CLAY')
clay.use_nodes=True
clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.24,.24,.24,1)
clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7
d=bpy.data.lights.new('BDL_REVIEW_BOTTOM','AREA');d.energy=650;d.size=5
bottom=bpy.data.objects.new(d.name,d);s.collection.objects.link(bottom);bottom.location=(0,0,-4);bottom.rotation_euler=(Vector((0,0,0))-bottom.location).to_track_quat('-Z','Y').to_euler()
renders=[]
for name in ['Hero','Front','Rear','Left','Right','Top','Underside','Nose','Rear_Close','Clay']:
 bottom.hide_render=name!='Underside';s.camera=bpy.data.objects['BDL_CAM_'+name];bpy.data.objects['BDL_REVIEW_FLOOR'].hide_render=name not in ['Hero','Clay'];s.view_layers[0].material_override=bpy.data.materials['BDL_NEUTRAL_CLAY'] if name=='Clay' else None;s.render.filepath=str(P/f'Previews/Banderol_G_{REV}_{name}.png');
 if name in ['Clay','Underside'] or not Path(s.render.filepath).exists():bpy.ops.render.render(write_still=True)
 renders.append(s.render.filepath)
(P/f'Documentation/G_renders_{REV}.json').write_text(json.dumps(renders,indent=2));print('G_RENDERS',len(renders))






