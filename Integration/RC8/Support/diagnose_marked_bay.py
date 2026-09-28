"""Color-code the marked wing-root obstruction in a temporary render."""
from pathlib import Path
import bpy
from mathutils import Vector

scene = bpy.context.scene
names = {'ORION_FUSELAGE', 'ORION_WING_R', 'ORION_WING_ROOT_BLEND_R',
         'ORION_MAIN_R_BAY_SIDE_1', 'ORION_MAIN_R_BAY_END_-1',
         'ORION_MAIN_R_BAY_END_1', 'ORION_MAIN_R_BAY_ROOF',
         'ORION_MAIN_R_CONFORMAL_SKIN'}
colors = {'ORION_MAIN_R_BAY_SIDE_1': (1, .05, .05, 1),
          'ORION_MAIN_R_BAY_END_-1': (1, .45, .02, 1),
          'ORION_MAIN_R_BAY_END_1': (1, .45, .02, 1),
          'ORION_MAIN_R_BAY_ROOF': (.03, .8, .1, 1)}
for ob in bpy.data.objects:
    if ob.type != 'MESH':
        continue
    ob.hide_render = ob.name not in names
    if ob.name in names:
        material = bpy.data.materials.new(ob.name + '_DIAGNOSTIC')
        material.diffuse_color = colors.get(ob.name, (.65, .65, .65, 1))
        ob.data.materials.clear()
        ob.data.materials.append(material)
cam_data = bpy.data.cameras.new('MarkedBlockCamera')
cam = bpy.data.objects.new('MarkedBlockCamera', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
target = Vector((.22, -1.5, -.03))
cam.location = (2.1, -3.3, .18)
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 2.8
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(Path(__file__).resolve().parents[1] / 'Reports/marked_bay_id.png')
bpy.ops.render.render(write_still=True)
