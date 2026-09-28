"""Read-only RC8 native asset audit; does not claim a rendered engine test."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "Assets/ORD/Models/RC8"
REPORT = ROOT / "Integration/RC8/Reports/native_resource_manifest.json"
entries = json.loads(REPORT.read_text(encoding="utf-8"))
checks = []

def check(name, condition, detail=""):
    checks.append({"check": name, "passed": bool(condition), "detail": detail})

def parse_resource(value):
    match = re.fullmatch(r"(\{[A-Fa-f0-9]{16}\})(.+)", value)
    if not match:
        raise ValueError(value)
    return match.group(1), ROOT / match.group(2)

def verify_resource(value, name, require_native=True):
    guid, path = parse_resource(value)
    metadata = Path(str(path) + ".meta")
    native = path
    check(name + " metadata", metadata.is_file() and value in metadata.read_text(errors="replace"))
    if require_native:
        check(name + " native data", native.is_file() and native.stat().st_size > 1024,
              f"{native.stat().st_size if native.is_file() else 0} bytes")
    return path

for item in entries:
    if "material" in item:
        material = verify_resource(item["emat"], item["material"], False)
        source = material.read_text(errors="replace")
        for kind, value in item["textures"].items():
            texture = verify_resource(value, item["material"] + " " + kind)
            check(item["material"] + " " + kind + " link", value in source)
            source_tiff = texture.with_suffix(".tif")
            check(item["material"] + " " + kind + " source", source_tiff.is_file())
    else:
        name = item["asset"]
        model = verify_resource(item["model"], name + " model")
        fbx = ROOT / item["source"]
        check(name + " FBX source", fbx.is_file() and fbx.stat().st_size > 1024)
        txo = model.with_suffix(".txo")
        check(name + " imported hierarchy", txo.is_file() and txo.stat().st_size > 1024)
        if txo.is_file():
            text = txo.read_text(errors="replace")
            lods = sorted(set(int(v) for v in re.findall(r"^\s*\$lod\s+(\d+)", text, re.M)))
            check(name + " four LODs", lods == [0, 1, 2, 3], str(lods))
            needed = (["ORION_PAYLOAD_SOCKET", "ORD_EngineAudio", "front_wheel_contact",
                       "ORD_SensorYaw", "ORD_SensorPitch", "ORD_Propeller"] if name == "Orion"
                      else ["BDL_Wing_L", "BDL_Wing_R"])
            for bone in needed:
                check(name + " " + bone, bone in text)
        prefab_names = ["ORD_Aircraft.et"] if name == "Orion" else ["ORD_Banderol.et", "ORD_BanderolStore.et"]
        for prefab_name in prefab_names:
            prefab = ROOT / "Prefabs/ORD" / prefab_name
            check(prefab_name + " final model", item["model"] in prefab.read_text(errors="replace"))

check("no obsolete TIFF metadata", not list((BASE / "Textures").glob("*.tif.meta")))
textures = list((BASE / "Textures").glob("*.edds"))
check("no empty EDDS", len(textures) == 24 and all(p.stat().st_size > 1024 for p in textures),
      f"{len(textures)} texture resources")
result = {"passed": sum(c["passed"] for c in checks), "total": len(checks), "failed": [c for c in checks if not c["passed"]], "checks": checks}
destination = ROOT / "Integration/RC8/Reports/native_import_audit.json"
destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({k: result[k] for k in ("passed", "total", "failed")}, indent=2))
raise SystemExit(0 if not result["failed"] else 1)
