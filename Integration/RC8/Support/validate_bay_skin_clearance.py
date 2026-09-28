from pathlib import Path
import bpy
import json
from mathutils.bvhtree import BVHTree

integration = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
patches = [bpy.data.objects[f'ORION_MAIN_{s}_CONFORMAL_SKIN'] for s in 'LR']
moving = [o for c in ('ORION_GEAR', 'ORION_GEAR_BAYS')
          for o in bpy.data.collections[c].all_objects
          if o.type == 'MESH' and not o.hide_render
          and ('MAIN_' in o.name or 'NOSE_' in o.name)
          and (c == 'ORION_GEAR' or 'DOOR_' in o.name)]

def geometry(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ p.co for p in mesh.vertices]
    faces = [tuple(p.vertices) for p in mesh.polygons]
    evaluated.to_mesh_clear()
    bounds = [(min(v[i] for v in vertices), max(v[i] for v in vertices)) for i in range(3)]
    return BVHTree.FromPolygons(vertices, faces), bounds

scene.frame_set(1)
static = [(obj.name, geometry(obj)) for obj in patches]
hits = []
for frame in [1 + i * .5 for i in range(479)]:
    scene.frame_set(int(frame), subframe=frame % 1)
    for obj in moving:
        candidate = geometry(obj)
        for name, patch in static:
            if any(candidate[1][i][1] < patch[1][i][0] or patch[1][i][1] < candidate[1][i][0]
                   for i in range(3)):
                continue
            if candidate[0].overlap(patch[0]):
                hits.append({'frame': frame, 'moving': obj.name, 'skin': name})
    if frame % 40 == 1:
        print('BAY_SKIN_CLEARANCE', frame, len(hits), flush=True)
report = {'frames': 479, 'moving_meshes': len(moving), 'contacts': hits}
(integration / 'Reports/bay_skin_clearance_v020.json').write_text(json.dumps(report, indent=2))
print('BAY_SKIN_COMPLETE', len(hits))
