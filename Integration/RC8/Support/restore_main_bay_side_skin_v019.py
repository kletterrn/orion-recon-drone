"""Replace the externally exposed main-bay side with a conformal skin patch."""
from pathlib import Path
import bpy
import json
import math

integration = Path(__file__).resolve().parents[1]
output = integration / 'Blender/Orion_RC8_Motion_v020.blend'
if output.exists():
    raise RuntimeError(f'Preserving existing checkpoint: {output}')

stations = json.loads(bpy.data.objects['ORION_FUSELAGE']['stations_json'])

def pchip(index, y):
    xs = [p[0] for p in stations]
    values = [p[index] for p in stations]
    delta = [(values[i + 1] - values[i]) / (xs[i + 1] - xs[i]) for i in range(len(xs) - 1)]
    tangent = [delta[0]]
    for i in range(1, len(xs) - 1):
        if delta[i - 1] * delta[i] <= 0:
            tangent.append(0)
        else:
            h0 = xs[i] - xs[i - 1]
            h1 = xs[i + 1] - xs[i]
            w0, w1 = 2 * h1 + h0, h1 + 2 * h0
            tangent.append((w0 + w1) / (w0 / delta[i - 1] + w1 / delta[i]))
    tangent.append(delta[-1])
    i = next((i for i in range(len(xs) - 1) if y <= xs[i + 1]), len(xs) - 2)
    h = xs[i + 1] - xs[i]
    t = max(0, min(1, (y - xs[i]) / h))
    return ((2 * t**3 - 3 * t**2 + 1) * values[i]
            + (t**3 - 2 * t**2 + t) * h * tangent[i]
            + (-2 * t**3 + 3 * t**2) * values[i + 1]
            + (t**3 - t**2) * h * tangent[i + 1])

root = bpy.data.objects['ORION_ROOT']
collection = bpy.data.collections['ORION_AIRFRAME']
publish = bpy.data.collections['ORION_ASSET']
for sign, label in [(-1, 'L'), (1, 'R')]:
    vertices, faces = [], []
    along, around = 84, 72
    for i in range(along + 1):
        y = -2.47 + 2.04 * i / along
        width, crown, keel = pchip(1, y), pchip(2, y), pchip(3, y)
        # The closed main doors sweep across the aft lower corner. Leave that
        # exact corner clear while continuing the skin over the exposed side.
        lower = -.25
        if i > 15:
            t = min(1, (i - 15) / 25)
            t = t * t * (3 - 2 * t)
            lower = -.25 - .26 * t
        for j in range(around + 1):
            a = lower + (1.55 - lower) * j / around
            u, v = math.cos(a), math.sin(a)
            x = width * abs(u)**(1.18 if v >= 0 else .45)
            zn = .17 + .83 * v if v >= 0 else .17 * (1 + v)
            z = keel + (crown - keel) * zn
            # Slight stand-off avoids coincident faces, feathered to zero at edges.
            blend = math.sin(math.pi * i / along)**2 * math.sin(math.pi * j / around)**2
            lift = .0025 * blend
            vertices.append((sign * (x + lift * u), y, z + lift * v))
    stride = around + 1
    for i in range(along):
        for j in range(around):
            a = i * stride + j
            face = (a, a + stride, a + stride + 1, a + 1)
            faces.append(face if sign > 0 else tuple(reversed(face)))
    mesh = bpy.data.meshes.new(f'ORION_MAIN_{label}_CONFORMAL_SKIN_MESH')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f'ORION_MAIN_{label}_CONFORMAL_SKIN', mesh)
    collection.objects.link(obj)
    if obj.name not in publish.all_objects:
        publish.objects.link(obj)
    obj.parent = root
    mesh.materials.append(bpy.data.materials['ORION_GREY_REVIEW'])
    for face in mesh.polygons:
        face.use_smooth = True
    obj['evidence'] = 'C visual completion of exposed main-bay side; fuselage section derived from approved source'
    obj['RC8_revision'] = 'v020 patch clears aft main doors; no gear/cutter alteration'

bpy.context.scene['RC8_status'] = 'v020 candidate: external side skin restored with aft door clearance'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(output))
print('RC8_SKIN_RESTORED', output)
