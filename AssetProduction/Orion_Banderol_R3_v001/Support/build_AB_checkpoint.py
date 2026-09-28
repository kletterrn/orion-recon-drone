"""Execute in Blender 5.2.2. Build the approved A/B setup, not aircraft geometry."""
from pathlib import Path
import bpy
import hashlib
import json
import math
import shutil
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
REFS = ROOT / 'Support' / 'references_private'
PREVIEWS = ROOT / 'Previews'
DOCS = ROOT / 'Documentation'
for folder in ['Orion/checkpoints', 'Orion/textures', 'Orion/exports',
               'Banderol/checkpoints', 'Banderol/textures', 'Banderol/exports',
               'Assembly', 'Documentation', 'Previews', 'Support/references_private']:
    (ROOT / folder).mkdir(parents=True, exist_ok=True)

MASTER = ROOT / 'Orion' / 'Orion_Master.blend'
if MASTER.exists():
    raise RuntimeError('Existing checkpoint found; use a new version instead of overwriting.')

source_files = [
    WORKSPACE / 'Assets/ORD/Models/OrionE_Detailed/OrionE_Detailed.blend',
    WORKSPACE / 'Assets/ORD/Models/OrionE_Game/ORD_Orion_Detailed.blend',
    WORKSPACE / 'Assets/ORD/Models/ORD_Missile.blend',
]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
source_hashes = {str(p): digest(p) for p in source_files}
provided = [
    ('R1', 'codex-clipboard-a937edfa-25c3-4607-a701-eb58f497244c.png', 'Side illustration / compatible layout only', 'SUPPORTING_PROJECTION'),
    ('R2', 'codex-clipboard-2e75e101-7b5d-4673-beb1-2cc8b872e020.png', 'Airframe 01 / compatible structure only', 'CONDITIONAL_PHOTO'),
    ('R3', 'codex-clipboard-74f8d8c5-b408-45ea-b6ca-df551a3a0ca6.png', 'Grey airframe / white nose / primary appearance', 'PRIMARY_PHOTO'),
    ('R4', 'codex-clipboard-73ed205f-9d66-4644-acb3-a5a2f9dc1ff4.png', 'Unidentified missile render / excluded', 'EXCLUDED_GEOMETRY'),
    ('R5', 'codex-clipboard-0a25e247-6aca-4166-88f8-3293dbaef80b.png', 'Banderol-like render / comparison lead only', 'ILLUSTRATION_ONLY'),
]
records = []
for rid, filename, caption, role in provided:
    src = Path('C:/Users/david/AppData/Local/Temp') / filename
    dst = REFS / (rid + '.png')
    if not src.exists():
        raise FileNotFoundError(src)
    shutil.copy2(src, dst)
    records.append(dict(id=rid, source=str(src), local=f'Support/references_private/{rid}.png',
                        sha256=digest(dst), caption=caption, role=role,
                        reuse='Private supplied reference; redistribution permission unestablished'))
(DOCS / 'source_manifest.json').write_text(json.dumps(dict(
    existing_asset_sha256=source_hashes, references=records,
    blender_version=bpy.app.version_string, stage='A/B setup; no aircraft geometry'), indent=2), encoding='utf-8')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'ORION_SCALE_REVIEW'
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene['stage'] = 'B_SETUP_PENDING_REVIEW'
scene['configuration'] = 'Orion_R3'
scene['forward'] = '+Y'; scene['right'] = '+X'; scene['up'] = '+Z'
scene['nominal_length_m'] = 8.0; scene['nominal_span_m'] = 16.0
scene['measurement_status'] = 'Published nominal family dimensions; R3 station coordinates unmeasured'
scene['reference_camera_status'] = 'Initial perspective setup; not solved or matched to a 3D aircraft'
scene['model_status'] = 'No aircraft source or export meshes yet'
scene.world = bpy.data.worlds.new('ORION_SETUP_WORLD')
scene.world.color = (0.03, 0.03, 0.03)

def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent.children if parent else scene.collection.children).link(c)
    return c

cols = {name: collection(name) for name in ['00_REFERENCE', '10_SOURCE', '20_PRESENTATION',
        '30_RIG_HELPERS', '40_EXPORT', '50_CAMERAS_LIGHTS']}
publish = collection('ORION_ASSET', None)
publish.children.link(cols['10_SOURCE'])
publish.children.link(cols['30_RIG_HELPERS'])
scene.collection.children.unlink(cols['10_SOURCE'])
scene.collection.children.unlink(cols['30_RIG_HELPERS'])
guides = collection('ORION_SETUP_GUIDES', cols['20_PRESENTATION'])
refcol = cols['00_REFERENCE']
refcol.hide_render = True

def obj(name, data, col, location=(0, 0, 0)):
    o = bpy.data.objects.new(name, data); col.objects.link(o); o.location = location
    return o

root = obj('ORION_ROOT', None, cols['30_RIG_HELPERS'])
root.empty_display_type = 'ARROWS'; root.empty_display_size = 0.6
root['datum'] = 'Provisional longitudinal midpoint; centerline at z=0; independent of floor'
root['configuration'] = 'Orion_R3'; root['evidence'] = 'C_DATUM / nominal dimensions published'
root['nominal_length_m'] = 8.0; root['nominal_span_m'] = 16.0
socket = obj('ORION_PAYLOAD_SOCKET', None, cols['30_RIG_HELPERS'])
socket.parent = root; socket.empty_display_type = 'CUBE'; socket.empty_display_size = 0.15
socket.hide_viewport = True; socket.hide_render = True
socket['status'] = 'UNPLACED: origin is a placeholder, not a mounting station'
socket['purpose'] = 'Scene alignment only; no physical engineering interface'

def emission(name, color):
    m = bpy.data.materials.new(name); m.use_nodes = True
    ns = m.node_tree.nodes; ns.clear()
    out = ns.new('ShaderNodeOutputMaterial'); e = ns.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*color, 1)
    m.node_tree.links.new(e.outputs[0], out.inputs['Surface'])
    return m

white = emission('SETUP_TEXT', (0.8, 0.88, 0.97))
muted = emission('SETUP_MUTED', (0.28, 0.38, 0.49))
blue = emission('SETUP_BLUE', (0.12, 0.53, 0.95))
gold = emission('SETUP_GOLD', (1, 0.65, 0.12))
red = emission('SETUP_EXCLUDED', (0.92, 0.2, 0.15))

def line(name, pts, material=muted, width=0.012, col=guides):
    c = bpy.data.curves.new(name, 'CURVE'); c.dimensions = '3D'; c.bevel_depth = width; c.bevel_resolution = 1
    s = c.splines.new('POLY'); s.points.add(len(pts)-1)
    for p, xyz in zip(s.points, pts): p.co = (*xyz, 1)
    o = obj(name, c, col); c.materials.append(material)
    o['role'] = 'Setup guide, not aircraft geometry'; return o

def text(name, body, location, size=0.22, material=white, col=guides):
    d = bpy.data.curves.new(name, 'FONT'); d.body = body; d.size = size
    o = obj(name, d, col, location); d.materials.append(material); return o

for i in range(-9, 10):
    line(f'ORION_GRID_X_{i:+d}', [(i, -5, -0.025), (i, 5, -0.025)], width=0.003)
for i in range(-5, 6):
    line(f'ORION_GRID_Y_{i:+d}', [(-9, i, -0.025), (9, i, -0.025)], width=0.003)
length = line('ORION_NOMINAL_LENGTH_8M', [(0, -4, 0), (0, 4, 0)], gold, 0.025)
span = line('ORION_NOMINAL_SPAN_16M', [(-8, 0, 0), (8, 0, 0)], blue, 0.025)
length['measurement_m'] = 8.0; span['measurement_m'] = 16.0
for y in [-4, 4]: line(f'ORION_LENGTH_END_{y:+d}', [(-0.3,y,0),(0.3,y,0)],gold)
for x in [-8, 8]: line(f'ORION_SPAN_END_{x:+d}', [(x,-0.3,0),(x,0.3,0)],blue)
line('ORION_FORWARD_ARROW', [(-0.16,3.7,0),(0,4,0),(0.16,3.7,0)], gold)
line('ORION_RIGHT_ARROW', [(7.7,-0.16,0),(8,0,0),(7.7,0.16,0)], blue)
text('ORION_SETUP_TITLE','ORION R3 / METRIC REFERENCE SETUP',(-8.5,5.0,0),0.4)
text('ORION_SETUP_SUBTITLE','STAGE A-B ONLY / AIRCRAFT GEOMETRY NOT CREATED',(-8.5,4.5,0),0.24,gold)
text('ORION_SPAN_LABEL','16.00 m nominal span',(-3.1,0.25,0),0.3,blue)
text('ORION_LENGTH_LABEL','8.00 m nominal length',(0.4,2.0,0),0.25,gold)
text('ORION_NOSE_LABEL','NOSE / +Y',(0.4,3.8,0),0.22,gold)
text('ORION_AFT_LABEL','AFT',(0.4,-4.0,0),0.22)
text('ORION_PORT_LABEL','PORT / -X',(-8.4,-0.7,0),0.2)
text('ORION_RIGHT_LABEL','STARBOARD / +X',(5.8,-0.7,0),0.2)
text('ORION_DATUM_LABEL','DATUM / (0,0,0)',(0.4,-0.5,0),0.2)
text('ORION_SCALE_NOTE','1 grid square = 1 m | +Z up | endpoint stations remain provisional',(-8.5,-5.5,0),0.22)
text('ORION_VIEW_NOTE','R3 governs white nose, turret and gear. R1/R2 provide compatible support only.',(-8.5,-5.95,0),0.22)

images = {}
for record in records:
    rid = record['id']; image = bpy.data.images.load(str(ROOT / record['local']))
    images[rid] = image
    image['reference_role'] = record['role']; image['redistribution'] = 'Unestablished permission; private reference'
    o = obj(f'ORION_REF_{rid}', None, refcol)
    o.empty_display_type = 'IMAGE'; o.data = image; o.empty_display_size = 8.0
    o['reference_id'] = rid; o['role'] = record['role']; o['projection_status'] = 'Uncalibrated reference, not a blueprint'
    o.hide_viewport = True
ref3 = bpy.data.objects['ORION_REF_R3']; ref3.hide_viewport = False
ref3.location = (12, 0, 0); ref3.empty_display_size = 10
ref3['placement'] = 'Reference board beside datum; not a measured image plane'

def camera(name, location, target=(0,0,0), ortho=None):
    d = bpy.data.cameras.new(name); o = obj(name, d, cols['50_CAMERAS_LIGHTS'], location)
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.clip_start = 0.05; d.clip_end = 200
    if ortho: d.type = 'ORTHO'; d.ortho_scale = ortho
    else: d.lens = 50
    return o

top = camera('ORION_CAM_TOP',(0,-0.3,30),(0,-0.3,0),27)
top.rotation_euler = (0,0,0)
for name,loc in [('FRONT',(0,24,0)),('REAR',(0,-24,0)),('LEFT',(-24,0,0)),('RIGHT',(24,0,0)),('UNDERSIDE',(0,0,-30))]:
    camera('ORION_CAM_'+name,loc,ortho=20 if name in ['FRONT','REAR','UNDERSIDE'] else 11)
persp = camera('ORION_CAM_R3_INITIAL',(12,18,3.2),(0,1.5,-0.2))
persp['match_status'] = 'INITIAL_ONLY: orientation, lens and framing await silhouette camera solve'
bg = persp.data.background_images.new(); bg.image = images['R3']; bg.alpha = 0.45; bg.display_depth = 'BACK'
persp.data.show_background_images = True
scene.camera = top

# Private renderable audit board is a separate scene, never part of ORION_ASSET.
board = bpy.data.scenes.new('REFERENCE_AUDIT_PRIVATE')
board.unit_settings.system = 'METRIC'; board.unit_settings.scale_length = 1
board['purpose'] = 'Private reference audit; contains no modeled aircraft'
board['redistribution'] = 'Do not redistribute supplied images without permission'
bc = bpy.data.collections.new('PRIVATE_AUDIT_BOARD'); board.collection.children.link(bc)
def picture(rid, x, y, width):
    image=images[rid]; height=width*image.size[1]/image.size[0]
    mesh=bpy.data.meshes.new('PRIVATE_'+rid)
    mesh.from_pydata([(-width/2,-height/2,0),(width/2,-height/2,0),(width/2,height/2,0),(-width/2,height/2,0)],[],[(0,1,2,3)])
    uv=mesh.uv_layers.new(name='UVMap')
    for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]): loop.uv=co
    o=obj('PRIVATE_IMAGE_'+rid,mesh,bc,(x,y,0))
    m=bpy.data.materials.new('PRIVATE_IMAGE_'+rid);m.use_nodes=True
    ns=m.node_tree.nodes;ns.clear();tex=ns.new('ShaderNodeTexImage');tex.image=image
    e=ns.new('ShaderNodeEmission');out=ns.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(tex.outputs['Color'],e.inputs['Color']);m.node_tree.links.new(e.outputs[0],out.inputs['Surface'])
    mesh.materials.append(m);return height
layout=[('R3',0,0.25,11.0),('R1',-9,2.55,5.7),('R2',-9,-1.3,5.7),('R4',9,2.3,5.7),('R5',9,-1.6,5.7)]
for rid,x,y,w in layout:
    h=picture(rid,x,y,w);role=next(r['caption'] for r in records if r['id']==rid)
    text('PRIVATE_LABEL_'+rid,rid+' / '+role,(x-w/2,y+h/2+0.15,0.02),0.18,red if rid=='R4' else gold if rid=='R3' else white,bc)
text('PRIVATE_BOARD_TITLE','REFERENCE AUDIT / ORION R3',( -12,5.0,0.02),0.42,white,bc)
text('PRIVATE_BOARD_NOTE','PRIVATE SUPPLIED REFERENCES / R4 EXCLUDED / R5 IS AN ILLUSTRATION / NO MODEL GEOMETRY',(-12,-5.0,0.02),0.23,gold,bc)
cd=bpy.data.cameras.new('PRIVATE_BOARD_CAMERA');cam=obj('PRIVATE_BOARD_CAMERA',cd,bc,(0,0,30));cam.rotation_euler=(0,0,0)
cd.type='ORTHO';cd.ortho_scale=26;board.camera=cam
board.world=bpy.data.worlds.new('PRIVATE_BOARD_WORLD');board.world.color=(0.02,0.025,0.035)

for s in [scene,board]:
    s.render.engine='CYCLES';s.cycles.samples=8
    s.render.resolution_x=2400;s.render.resolution_y=1200;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'
    s.view_settings.view_transform='Standard'
    s.render.film_transparent=False

# Keep a camera view ready when the master opens in the interactive application.
bpy.context.window.scene=scene
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
scene.render.filepath=str(PREVIEWS/'Orion_AB_Scale_Setup.png')
bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
for record in records:
    images[record['id']].filepath = '//../' + record['local']
bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
checkpoint=ROOT/'Orion/checkpoints/Orion_B_reference_scale_v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint),copy=True)
bpy.ops.render.render(write_still=True,scene=scene.name)
board.render.filepath=str(PREVIEWS/'AB_Reference_Audit_PRIVATE.png')
bpy.ops.render.render(write_still=True,scene=board.name)
# Saving again preserves the audit-board output path; never touches existing assets.
bpy.context.window.scene=scene
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint),copy=True)
assert all(digest(Path(p))==h for p,h in source_hashes.items())
print('A/B_CHECKPOINT_CREATED',MASTER)
