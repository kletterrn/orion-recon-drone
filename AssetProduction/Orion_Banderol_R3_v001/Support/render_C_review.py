"""Render actual stage-C geometry; presentation proxies remain explicit."""
import bpy,sys,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/f'Orion/checkpoints/Orion_C_primary_geometry_{REV}.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s
floor=bpy.data.objects['ORION_REVIEW_FLOOR'];renders=[]
if 'ORION_NEUTRAL_CLAY' not in bpy.data.materials:
    clay=bpy.data.materials.new('ORION_NEUTRAL_CLAY');clay.use_nodes=True
    clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.48,.51,.54,1)
    clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
for view in ['Hero','Front','Rear','Left','Right','Top','Underside','R3_Perspective','Nose_Profile','Nose_Front','Nose_ThreeQuarter']:
    name='ORION_CAM_'+('HERO' if view=='Hero' else 'R3_INITIAL' if view=='R3_Perspective' else 'RIGHT' if view=='Nose_Profile' else view.upper())
    if view in ['Nose_Front','Nose_ThreeQuarter']:
        d=bpy.data.cameras.new(view);cam=bpy.data.objects.new(view,d);s.collection.objects.link(cam)
        target=Vector((0,3.35,-.01))
        cam.location=(0,12,-.01) if view=='Nose_Front' else (3.8,7.5,1.25)
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        d.type='ORTHO';d.ortho_scale=1.6 if view=='Nose_Front' else 2.2
        for o in s.objects:
            if o.type=='MESH' and o.name not in ['ORION_FUSELAGE','ORION_NOSE_WHITE']:o.hide_render=True
    else:cam=bpy.data.objects[name]
    s.camera=cam
    floor.hide_render=view in ['Front','Rear','Left','Right','Top','Underside','Nose_Profile','Nose_Front','Nose_ThreeQuarter']
    s.view_layers[0].material_override=bpy.data.materials['ORION_NEUTRAL_CLAY'] if view in ['Front','Rear','Left','Right','Top','Underside'] else None
    if view in ['Top','Underside']:
        s.render.resolution_x=1800;s.render.resolution_y=1200
    elif view in ['Front','Rear']:
        s.render.resolution_x=1800;s.render.resolution_y=800
    else:s.render.resolution_x=1800;s.render.resolution_y=1200
    if view=='Nose_Profile':
        cam.location=(-12,2.90,-.10);cam.data.ortho_scale=2.9
        cam.rotation_euler=(Vector((0,2.90,-.10))-cam.location).to_track_quat('-Z','Y').to_euler()
    path=ROOT/f'Previews/C_{REV}_{view}.png';s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True,scene=s.name)
    renders.append({'view':view,'file':str(path.relative_to(ROOT)),'width':s.render.resolution_x,'height':s.render.resolution_y})
(ROOT/f'Documentation/C_renders_{REV}.json').write_text(json.dumps(renders,indent=2),encoding='utf-8')
print('STAGE_C_RENDERS_COMPLETE',len(renders))
