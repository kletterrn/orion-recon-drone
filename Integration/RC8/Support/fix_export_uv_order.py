"""Keep each optimized export mesh's active atlas UV as native UV set zero."""
from pathlib import Path
import bpy
import json
import sys

base = Path("C:/Users/david/Desktop/RECON DRONES/Integration/RC8")
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
source = base / ("GameSources/Orion_RC8_Game_" + args[0] + ".blend") if args else base / "GameSources/Orion_RC8_Game.blend"
destination = base / ("GameSources/Orion_RC8_Game_" + args[1] + ".blend") if len(args) > 1 else base / "GameSources/Orion_RC8_Game_v002.blend"
if args and destination.exists():
    raise RuntimeError(f'Preserving existing UV checkpoint: {destination}')
bpy.ops.wm.open_mainfile(filepath=str(source))
changes = []
for obj in bpy.data.objects:
    if obj.type != "MESH" or not any(obj.name.endswith(f"_LOD{i}") for i in range(4)):
        continue
    layers = obj.data.uv_layers
    if not layers or not layers.active:
        raise RuntimeError(f"Missing atlas UV: {obj.name}")
    active = layers.active.name
    before = [layer.name for layer in layers]
    for layer in list(layers):
        if layer.name != active:
            layers.remove(layer)
    layers.active_index = 0
    if len(layers) != 1 or layers[0].name != active:
        raise RuntimeError(f"UV set zero mismatch: {obj.name}")
    if len(before) > 1:
        changes.append({"mesh": obj.name, "before": before, "atlas_uv": active})
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
report = {"source": str(source), "saved": str(destination), "changed": changes,
          "rule": "All exported LOD meshes have exactly one UV layer, the active atlas UV."}
(base / ("Reports/orion_uv_order_fix_" + args[1] + ".json") if len(args) > 1 else base / "Reports/orion_uv_order_fix.json").write_text(json.dumps(report, indent=2))
print("UV_ORDER_FIXED", len(changes), flush=True)
