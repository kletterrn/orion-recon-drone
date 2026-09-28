import bpy
from mathutils.bvhtree import BVHTree

scene = bpy.context.scene
scene.frame_set(120)
for side, door in [('L', 'ORION_MAIN_L_DOOR_SHELL_1'), ('R', 'ORION_MAIN_R_DOOR_SHELL_-1')]:
    objects = [bpy.data.objects[door], bpy.data.objects[f'ORION_MAIN_{side}_CONFORMAL_SKIN']]
    trees = []
    for obj in objects:
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        vertices = [evaluated.matrix_world @ p.co for p in mesh.vertices]
        trees.append(BVHTree.FromPolygons(vertices, [tuple(p.vertices) for p in mesh.polygons]))
        evaluated.to_mesh_clear()
    hits = trees[0].overlap(trees[1])
    print(side, 'faces', len(hits), 'patch_angular_indices', sorted({j % 72 for _, j in hits}),
          'patch_along_indices', sorted({j // 72 for _, j in hits}))
