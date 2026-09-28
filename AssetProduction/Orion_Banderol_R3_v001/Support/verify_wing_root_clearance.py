from pathlib import Path
import bpy,json,hashlib,bmesh
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;rev=s['revision'].replace('D_','')
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear();return t
s.frame_set(1)
roots=[bpy.data.objects['ORION_WING_ROOT_BLEND_'+label] for label in ['L','R']];rt={o.name:tree(o) for o in roots};hits=[]
for fr in range(1,161):
 s.frame_set(fr)
 for moving in bpy.data.collections['ORION_GEAR'].all_objects:
  if moving.type!='MESH':continue
  t=tree(moving)
  for name,tr in rt.items():
   overlap=t.overlap(tr)
   if overlap:hits.append({'frame':fr,'gear':moving.name,'root':name,'pairs':len(overlap)})
s.frame_set(1)
static_hits=[]
obstacles=[o for o in bpy.data.collections['ORION_GEAR_BAYS'].all_objects if o.type=='MESH']+[bpy.data.objects['ORION_FLAP_'+l] for l in ['L','R']]
for ob in obstacles:
 t=tree(ob)
 for name,tr in rt.items():
  overlap=t.overlap(tr)
  if overlap:static_hits.append({'obstacle':ob.name,'root':name,'pairs':len(overlap)})
report={'revision':rev,'gear_all_160_frames_against_new_roots':hits,'bays_doors_flaps_against_roots':static_hits,'old_assets_unchanged':{path:hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in json.loads((P/'Documentation/source_manifest.json').read_text(encoding='utf-8'))['existing_asset_sha256'].items()}}
checkpoint=P/f'Orion/checkpoints/Orion_D_wing_root_fix_{rev}.blend'
bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
report['fresh_checkpoint_reopen']=True
report['relative_images_resolve']=all(Path(bpy.path.abspath(i.filepath)).exists() for i in bpy.data.images if i.source=='FILE')
assert bpy.data.scenes['ORION_GEOMETRY_REVIEW'].frame_current==1
(P/f'Documentation/D_wing_root_clearance_{rev}.json').write_text(json.dumps(report,indent=2))
print('WING_ROOT_CLEARANCE',len(hits),'gear contacts',len(static_hits),'bay/flap contacts',report['fresh_checkpoint_reopen'])
