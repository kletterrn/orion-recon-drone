import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[1]
f=p/'Orion/checkpoints/Orion_D_gear_bays_sensor_v010.blend'
bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s
assert s.frame_current==1
assert len(bpy.data.collections['10_SOURCE'].all_objects)==234
assert all(Path(bpy.path.abspath(i.filepath)).exists() for i in bpy.data.images if i.source=='FILE')
print('FRESH_CHECKPOINT_REOPEN_OK')
d=bpy.data.cameras.new('D_HERO_RESIZED');o=bpy.data.objects.new('D_HERO_RESIZED',d);s.collection.objects.link(o);o.location=(12,16,8);o.rotation_euler=(Vector((0,0,-.05))-o.location).to_track_quat('-Z','Y').to_euler();d.lens=40;s.camera=o;s.render.resolution_x=1500;s.render.resolution_y=1100;s.cycles.samples=24;s.render.filepath=str(p/'Previews/D_v010_Hero.png');bpy.ops.render.render(write_still=True)
