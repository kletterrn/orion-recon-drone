"""Put the conformal bay skins in the same export material group as the fuselage."""
from pathlib import Path
import bpy

base = Path(__file__).resolve().parents[1]
target = base / 'Blender/Orion_RC8_Motion_v021.blend'
if target.exists():
    raise RuntimeError(f'Checkpoint already exists: {target}')

fuselage = bpy.data.objects['ORION_FUSELAGE']
material = fuselage.data.materials[0]
assert material.name.endswith('__I_Orion_Airframe'), material.name

for side in 'LR':
    patch = bpy.data.objects[f'ORION_MAIN_{side}_CONFORMAL_SKIN']
    patch.data.materials.clear()
    patch.data.materials.append(material)
    patch['RC8_revision'] = 'v021: same source and engine material group as Orion fuselage'
    assert patch.data.materials[0] is material

bpy.context.scene['RC8_status'] = 'v021: conformal side skins use fuselage material group'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print('BAY_SKIN_MATERIAL_MATCH', material.name, target, flush=True)
