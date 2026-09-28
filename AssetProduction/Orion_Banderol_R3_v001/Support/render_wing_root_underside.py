import bpy
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(p/'Orion/Orion_Master.blend'));s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1)
d=bpy.data.cameras.new('ROOT_UNDERSIDE');cam=bpy.data.objects.new('ROOT_UNDERSIDE',d);s.collection.objects.link(cam);cam.location=(2.8,1.8,-1.4);cam.rotation_euler=(Vector((0,-1.1,.24))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=3.5;s.camera=cam;bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=True;s.cycles.samples=32;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.filepath=str(p/'Previews/D_v012_Wing_Root_Underside.png');bpy.ops.render.render(write_still=True)
