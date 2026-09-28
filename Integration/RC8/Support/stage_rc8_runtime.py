"""Create a clean, separate Workbench project for RC8 runtime packaging."""
from pathlib import Path
import json
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(tempfile.mkdtemp(prefix="ORD_RC8_Stage_"))
FOLDERS = ("Assets", "Sounds", "Configs", "Prefabs", "Scripts", "UI", "Worlds", "Missions")
EXTENSIONS = {".xob", ".emat", ".edds", ".et", ".ent", ".layer", ".conf",
              ".layout", ".imageset", ".c", ".wav", ".acp", ".sig", ".ct", ".pp"}
COPIED = []
for folder in FOLDERS:
    for source in (ROOT / folder).rglob("*"):
        if not source.is_file() or "WorkbenchGame" in source.parts:
            continue
        if source.suffix == ".meta":
            parent_resource = Path(str(source)[:-5])
            if not parent_resource.is_file() or parent_resource.suffix not in EXTENSIONS:
                continue
        elif source.suffix not in EXTENSIONS:
            continue
        destination = OUTPUT / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        COPIED.append(source.relative_to(ROOT).as_posix())
shutil.copy2(ROOT / "ReconDrones.gproj", OUTPUT / "ReconDrones.gproj")
manifest = {"stage": str(OUTPUT), "copied": len(COPIED), "files": COPIED,
            "exclusions": "editor scripts, test handlers, reference images, editable sources"}
(ROOT / "Integration/RC8/Reports/runtime_stage_manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8")
print(OUTPUT)
