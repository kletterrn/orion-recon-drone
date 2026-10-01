"""Summarize captured EO/IR/inset evidence; no synthetic screenshots."""
import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument("profile", type=Path)
p.add_argument("output", type=Path)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
report = {"profile": str(a.profile), "images": {}, "performance": {}}
for name in ("ReconEO", "ReconIR", "ReconBlend", "ReconWide", "ReconSchematic", "ReconMap", "ReconReader"):
    source = a.profile / "profile" / (name + ".bmp.bmp")
    picture = Image.open(source).convert("RGB")
    picture.save(a.output / (name + ".png"))
    w, h = picture.size
    pixels = np.asarray(picture, dtype=float)[int(h*.23):int(h*.79), int(w*.27):int(w*.75)]
    report["images"][name] = {
        "resolution": [w, h],
        "central_mean_luminance": float(pixels.mean()),
        "central_mean_channel_span": float((pixels.max(axis=2)-pixels.min(axis=2)).mean()),
    }
results = json.loads((a.profile / "game-results.json").read_text())
for line in results["observations"]:
    match = re.search(r"ORD_TEST_PERF (\w+) frames=(\d+) seconds=([\d.]+)", line)
    if match:
        mode, frames, seconds = match.groups()
        report["performance"][mode] = {"frames": int(frames), "seconds": float(seconds), "average_fps": int(frames)/float(seconds), "average_frame_ms": float(seconds)*1000/int(frames)}
report["note"] = "Four-second sequential scene samples include screenshot/transition overhead; configured FPS cap applies. Not isolated GPU timings or a sustained gameplay benchmark. Channel spans distinguish captured color contribution, not thermal calibration."
(a.output / "render-metrics.json").write_text(json.dumps(report, indent=2))
(a.output / "engine-results.json").write_text(json.dumps(results, indent=2))
print(json.dumps(report["performance"], indent=2))
