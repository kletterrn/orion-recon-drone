"""Bake constant fuselage paint directly to the already-UVed bay skin.

Selected-to-active ray baking misses this very thin, coincident shell. A direct
emission bake keeps the same editable geometry and UVs without ray projection.
"""
from pathlib import Path
import shutil
import bpy

base = Path(__file__).resolve().parents[1]
source = base / 'GameSources/Orion_RC8_Game_v008.blend'
target = base / 'GameSources/Orion_RC8_Game_v009.blend'
old_textures = base / 'GameSources/textures_v007'
new_textures = base / 'GameSources/textures_v009'
if target.exists() or new_textures.exists():
    raise RuntimeError('Preserving existing v009 checkpoint')

shutil.copytree(old_textures, new_textures)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
patch = bpy.data.objects['Orion_Bay_Skin_LOD0']
original = patch.data.materials[0]
assert original.name == 'RC8_Orion_Bay_Skin'
assert len(patch.data.uv_layers) == 1

scene.render.engine = 'CYCLES'
scene.cycles.samples = 4
scene.render.bake.use_selected_to_active = False
scene.render.bake.use_clear = True
scene.render.bake.margin = 16

bpy.ops.object.select_all(action='DESELECT')
patch.hide_set(False)
patch.select_set(True)
bpy.context.view_layer.objects.active = patch

for channel, value in (
    ('BaseColor', (0.24, 0.27, 0.29, 1)),
    ('Roughness', (0.46, 0.46, 0.46, 1)),
    ('Metallic', (0, 0, 0, 1)),
):
    image = bpy.data.images.new('Orion_Bay_Skin_' + channel + '_Direct', 4096, 4096, alpha=False)
    image.colorspace_settings.name = 'sRGB' if channel == 'BaseColor' else 'Non-Color'
    image.filepath_raw = str(new_textures / ('Orion_Bay_Skin_' + channel + '.png'))
    image.file_format = 'PNG'

    material = bpy.data.materials.new('RC8_BAY_SKIN_' + channel + '_BAKE')
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    output = tree.nodes.new('ShaderNodeOutputMaterial')
    emission = tree.nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = value
    tree.links.new(emission.outputs[0], output.inputs['Surface'])
    image_node = tree.nodes.new('ShaderNodeTexImage')
    image_node.image = image
    tree.nodes.active = image_node
    image_node.select = True
    patch.data.materials.clear()
    patch.data.materials.append(material)
    bpy.ops.object.bake(type='EMIT')
    image.save()
    patch.data.materials.clear()
    patch.data.materials.append(original)
    for node in original.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image and node.image.name.startswith('Orion_Bay_Skin_' + channel):
            node.image = image
            break
    print('DIRECT_BAKE_DONE', channel, image.filepath_raw, flush=True)

for image in bpy.data.images:
    if image.filepath and str(old_textures) in image.filepath:
        image.filepath = image.filepath.replace(str(old_textures), str(new_textures))

scene['RC8_status'] = 'v009: bay skin grey/roughness direct-baked, normal/AO retained'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(target), relative_remap=True)
print('BAY_SKIN_PAINT_SAVED', target, flush=True)
