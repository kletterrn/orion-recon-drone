from pathlib import Path
import bpy, json, sys

label = "Banderol" if sys.argv[-1] == "Banderol" else "Orion"
name = "Banderol_RC8_Game_v003.blend" if label == "Banderol" else "Orion_RC8_Game.blend"
source = Path("C:/Users/david/Desktop/RECON DRONES/Integration/RC8/GameSources") / name
bpy.ops.wm.open_mainfile(filepath=str(source))
report = []
for obj in bpy.data.objects:
    if obj.type != "MESH" or not obj.name.endswith("_LOD0"):
        continue
    mesh = obj.data
    if not mesh.uv_layers.active:
        report.append({"name": obj.name, "error": "no active UV"})
        continue
    uv = mesh.uv_layers.active.data
    count = len(uv)
    limits = [min((v.uv[i] for v in uv), default=0) for i in (0, 1)] + [max((v.uv[i] for v in uv), default=0) for i in (0, 1)]
    first = [list(uv[j].uv) for j in range(min(count, 5))]
    report.append({"name": obj.name, "polygons": len(mesh.polygons), "uv_count": count,
                   "active_uv": mesh.uv_layers.active.name,
                   "uv_layers": [layer.name for layer in mesh.uv_layers], "limits": limits,
                   "first_uv": first, "materials": [m.name if m else None for m in mesh.materials],
                   "modifiers": [m.type for m in obj.modifiers]})
    if obj.name == "Orion_Airframe_LOD0":
        outward = 0
        inward = 0
        examples = []
        for face in mesh.polygons:
            c = obj.matrix_world @ face.center
            n = (obj.matrix_world.to_3x3() @ face.normal).normalized()
            # Fuselage outer shell around its longitudinal Y axis.
            if abs(c.x) > 0.15 or abs(c.z) > 0.15:
                radial = c.copy(); radial.y = 0
                if radial.length > 0:
                    score = n.dot(radial.normalized())
                    if score > 0.2: outward += 1
                    if score < -0.2: inward += 1
                    if len(examples) < 8 and abs(score) > 0.7:
                        examples.append({"center": list(c), "normal": list(n), "radial_dot": score})
        report[-1]["radial_normal_counts"] = {"outward": outward, "inward": inward}
        report[-1]["normal_examples"] = examples
path = Path("C:/Users/david/Desktop/RECON DRONES/Integration/RC8/Reports") / (label.lower() + "_uv_inspection.json")
path.write_text(json.dumps(report, indent=2))
print("UV_INSPECTION", len(report), flush=True)
