"""Bake the bay skin's own tangent-space normals without a projection cage."""
from pathlib import Path
import shutil
import bpy

base = Path(__file__).resolve().parents[1]
source = base / 'GameSources/Orion_RC8_Game_v009.blend'
target = base / 'GameSources/Orion_RC8_Game_v010.blend'
old_textures = base / 'GameSources/textures_v009'
new_textures = base / 'GameSources/textures_v010'
if target.exists() or new_textures.exists():
    raise RuntimeError('Preserving existing v010 checkpoint')

shutil.copytree(old_textures, new_textures)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
patch = bpy.data.objects['Orion_Bay_Skin_LOD0']
original = patch.data.materials[0]
assert original.name == 'RC8_Orion_Bay_Skin' and len(patch.data.uv_layers) == 1

image = bpy.data.images.new('Orion_Bay_Skin_Normal_Direct', 4096, 4096, alpha=False)
image.colorspace_settings.name = 'Non-Color'
image.filepath_raw = str(new_textures / 'Orion_Bay_Skin_Normal.png')
image.file_format = 'PNG'
material = bpy.data.materials.new('RC8_BAY_SKIN_NORMAL_BAKE')
material.use_nodes = True
tree = material.node_tree
image_node = tree.nodes.new('ShaderNodeTexImage')
image_node.image = image
tree.nodes.active = image_node
image_node.select = True
patch.data.materials.clear()
patch.data.materials.append(material)

scene.render.engine = 'CYCLES'
scene.cycles.samples = 4
scene.render.bake.use_selected_to_active = False
scene.render.bake.use_clear = True
scene.render.bake.margin = 16
scene.render.bake.normal_space = 'TANGENT'
bpy.ops.object.select_all(action='DESELECT')
patch.hide_set(False)
patch.select_set(True)
bpy.context.view_layer.objects.active = patch
bpy.ops.object.bake(type='NORMAL')
image.save()

patch.data.materials.clear()
patch.data.materials.append(original)
for node in original.node_tree.nodes:
    if node.type == 'TEX_IMAGE' and node.image and node.image.name.startswith('Orion_Bay_Skin_Normal'):
        node.image = image
        break
for entry in bpy.data.images:
    if entry.filepath and str(old_textures) in entry.filepath:
        entry.filepath = entry.filepath.replace(str(old_textures), str(new_textures))

scene['RC8_status'] = 'v010: direct-baked bay skin tangent normal'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(target), relative_remap=True)
print('BAY_SKIN_NORMAL_SAVED', target, flush=True)
