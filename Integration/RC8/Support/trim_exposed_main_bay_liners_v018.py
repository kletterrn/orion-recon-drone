"""Keep the main-bay liner inside the aircraft's original exterior skin."""
from pathlib import Path
import bpy

integration = Path(__file__).resolve().parents[1]
output = integration / 'Blender/Orion_RC8_Motion_v018.blend'
if output.exists():
    raise RuntimeError(f'Preserving existing checkpoint: {output}')

body = bpy.data.objects['ORION_FUSELAGE']
disabled = []
for modifier in body.modifiers:
    if modifier.type == 'BOOLEAN':
        disabled.append((modifier, modifier.show_viewport))
        modifier.show_viewport = False
bpy.context.view_layer.update()
evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
hull_mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True,
    depsgraph=bpy.context.evaluated_depsgraph_get())
for modifier, old in disabled:
    modifier.show_viewport = old
hull = bpy.data.objects.new('RC8_TEMP_UNCUT_FUSELAGE_ENVELOPE', hull_mesh)
bpy.context.scene.collection.objects.link(hull)
hull.matrix_world = body.matrix_world.copy()
for vertex in hull_mesh.vertices:
    vertex.co -= vertex.normal * .006
bpy.context.view_layer.update()

changed = []
for side in ('L', 'R'):
    for name in (f'ORION_MAIN_{side}_BAY_SIDE_{-1 if side == "L" else 1}',
                 f'ORION_MAIN_{side}_BAY_END_-1', f'ORION_MAIN_{side}_BAY_END_1',
                 f'ORION_MAIN_{side}_BAY_ROOF'):
        obj = bpy.data.objects[name]
        before = len(obj.data.polygons)
        modifier = obj.modifiers.new('RC8_Keep_Liner_Inside_Exterior', 'BOOLEAN')
        modifier.operation = 'INTERSECT'
        modifier.solver = 'EXACT'
        modifier.object = hull
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        if not obj.data.polygons:
            raise RuntimeError(f'Clipping erased {name}')
        obj['RC8_liner_fix'] = 'Trimmed against uncut fuselage with 6 mm inset; source v017 preserved'
        changed.append((name, before, len(obj.data.polygons)))

bpy.data.objects.remove(hull, do_unlink=True)
bpy.context.scene['RC8_status'] = 'v018 candidate: main bay liner protrusion trimmed; motion check pending'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(output))
print('RC8_LINER_TRIM_SAVED', output, changed)
