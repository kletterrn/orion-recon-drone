"""Preserve new supplied references and render a private, labeled comparison board."""
import bpy,json,shutil,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v004'
R10_MODE='R10' in sys.argv
refs=[('R6','ab7d5663-1f88-42be-b69d-9850c35e7e5a','Exhibition 03 photo; compatible side contour only'),
('R7','a76ff791-3357-48f6-9f75-d0208b7906b4','Ramp photograph; R3-compatible white-nose aircraft'),
('R8','28fd54da-8240-4404-b373-628b47634912','Airborne photograph; low resolution silhouette'),
('R9','03c4aebd-bbe9-499c-99bd-6a867d665d48','Illustration/render; supporting comparison, no geometry authority')]
records=[]
for rid,uid,role in refs:
    source=Path('C:/Users/david/AppData/Local/Temp')/f'codex-clipboard-{uid}.png'
    dest=ROOT/f'Support/references_private/{rid}.png'
    if not dest.exists():shutil.copy2(source,dest)
    h=hashlib.sha256(source.read_bytes()).hexdigest();assert hashlib.sha256(dest.read_bytes()).hexdigest()==h
    records.append({'id':rid,'source':str(source),'local':str(dest.relative_to(ROOT)),'sha256':h,'role':role,'permission':'Private reference only; attribution and redistribution rights unresolved'})
(ROOT/'Documentation/additional_reference_manifest.json').write_text(json.dumps(records,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.name='C_NOSE_COMPARISON_PRIVATE';s.world=bpy.data.worlds.new('ComparisonWorld');s.world.color=(.035,.035,.035)
def label(txt,x,y,size=.24):
    d=bpy.data.curves.new(txt,'FONT');d.body=txt;d.size=size
    o=bpy.data.objects.new(txt,d);s.collection.objects.link(o);o.location=(x,y,.02)
    m=bpy.data.materials.new('Label');m.use_nodes=True;n=m.node_tree.nodes;n.clear()
    e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(.8,.85,.9,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs[0]);d.materials.append(m)
def picture(path,x,y,w):
    im=bpy.data.images.load(str(path));h=w*im.size[1]/im.size[0]
    d=bpy.data.meshes.new(path.stem);d.from_pydata([(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)],[],[(0,1,2,3)])
    uv=d.uv_layers.new()
    for p,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):p.uv=co
    o=bpy.data.objects.new(path.stem,d);s.collection.objects.link(o);o.location=(x,y,0)
    m=bpy.data.materials.new(path.stem);m.use_nodes=True;n=m.node_tree.nodes;n.clear()
    t=n.new('ShaderNodeTexImage');t.image=im;e=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(t.outputs[0],e.inputs[0]);m.node_tree.links.new(e.outputs[0],out.inputs[0]);d.materials.append(m)
layout=[('Support/references_private/R3.png',-6.3,4,'R3 / PRIMARY WHITE-NOSE PHOTO'),
(f'Previews/C_{REV}_R3_Perspective.png',6.3,4,f'{REV} / APPROXIMATE VIEWPOINT, NOT CALIBRATED'),
('Support/references_private/R6.png',-6.3,-4.3,'R6 / EXHIBITION SIDE-CONTOUR SUPPORT'),
(f'Previews/C_{REV}_Left.png',6.3,-4.3,f'{REV} / ORTHOGRAPHIC SIDE / DETAIL PROXIES')]
if R10_MODE:
    layout=[('Support/references_private/R10.png',-6.3,4,'R10 / FRONTAL-OBLIQUE PHOTO / LOW RESOLUTION'),
    (f'Previews/C_{REV}_Nose_ThreeQuarter.png',6.3,4,f'{REV} / NOSE CROSS-SECTION / VIEW NOT CALIBRATED'),
    (f'Previews/C_{REV}_Nose_Profile.png',-6.3,-4.3,f'{REV} / SIDE PROFILE / SENSOR IS A PROXY'),
    (f'Previews/C_{REV}_Nose_Front.png',6.3,-4.3,f'{REV} / FRONT / ISOLATED NOSE AND FOREBODY')]
for path,x,y,title in layout:picture(ROOT/path,x,y,11.8);label(title,x-5.9,y+4.05,.21)
label('ORION / NOSE AND FORWARD-FUSELAGE REVISION '+REV,-12.2,9.0,.34)
label('PRIVATE REFERENCES / DISTINCT VARIANTS / VIEWPOINTS ARE NOT A PIXEL-MATCHED OVERLAY',-12.2,-9,.20)
d=bpy.data.cameras.new('ComparisonCamera');o=bpy.data.objects.new('ComparisonCamera',d);s.collection.objects.link(o);o.location=(0,0,30);d.type='ORTHO';d.ortho_scale=26;s.camera=o
s.render.engine='CYCLES';s.cycles.samples=1;s.render.resolution_x=3000;s.render.resolution_y=2300;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
s.render.filepath=str(ROOT/f'Previews/C_{REV}_Nose_Comparison_PRIVATE.png');bpy.ops.render.render(write_still=True)
print('NOSE_COMPARISON_RENDERED')
