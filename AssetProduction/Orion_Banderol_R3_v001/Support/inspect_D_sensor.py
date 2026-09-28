import bpy
from pathlib import Path
p=Path(r'C:\Users\david\Desktop\RECON DRONES\AssetProduction\Orion_Banderol_R3_v001')
bpy.ops.wm.open_mainfile(filepath=str(p/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s
h=bpy.data.objects['ORION_SENSOR_PITCH_HOUSING'];c=bpy.data.objects['ORION_SENSOR_MAIN_RECESS_CUTTER']
print('CUT',c.rotation_euler[:],c.scale[:],len(c.data.vertices),[tuple(c.matrix_world@v.co) for v in c.data.vertices][:6])
print('MODS',[(m.name,m.type) for m in h.modifiers]);print('HIDE',c.hide_render,c.hide_viewport)
# Explicitly triangulate the original large cap before CSG, to avoid n-gon hole-fill artifacts.
tri=h.modifiers.new('Triangulate_before_CSG','TRIANGULATE');bpy.context.view_layer.objects.active=h;bpy.ops.object.modifier_move_up(modifier=tri.name)
for i in range(len(h.modifiers)-2):bpy.ops.object.modifier_move_up(modifier=tri.name)
s.frame_set(1)
d=bpy.data.cameras.new('Test');o=bpy.data.objects.new('Test',d);s.collection.objects.link(o)
from mathutils import Vector
o.location=(1.6,4.7,-.50);o.rotation_euler=(Vector((0,2.05,-.8))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=1.15;s.camera=o;s.render.resolution_x=1000;s.render.resolution_y=800;s.cycles.samples=16;s.render.filepath=str(p/'Previews/D_sensor_CSG_test.png');bpy.ops.render.render(write_still=True)
