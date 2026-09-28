"""Separate the close-fitting bay skin from both fuselage and equipment bakes."""
from pathlib import Path
import bpy

base = Path(__file__).resolve().parents[1]
target = base / 'Blender/Orion_RC8_Motion_v022.blend'
if target.exists():
    raise RuntimeError(f'Checkpoint already exists: {target}')

fuselage_material = bpy.data.objects['ORION_FUSELAGE'].data.materials[0]
skin_material = fuselage_material.copy()
skin_material.name = 'ORION_GREY_BAY_SKIN__I_Orion_Bay_Skin'
assert skin_material.name.endswith('__I_Orion_Bay_Skin')

for side in 'LR':
    patch = bpy.data.objects[f'ORION_MAIN_{side}_CONFORMAL_SKIN']
    patch.data.materials.clear()
    patch.data.materials.append(skin_material)
    patch['RC8_revision'] = 'v022: separate atlas, same source paint and engine tint as fuselage'

bpy.context.scene['RC8_status'] = 'v022: bay skin own bake atlas, fuselage paint settings'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print('BAY_SKIN_MATERIAL_ISOLATED', skin_material.name, target, flush=True)
