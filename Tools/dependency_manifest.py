"""Record installed external dependency content; never copy dependency assets."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT / 'local.build.json').read_text())
addons = Path(config['addons'])
items = []
for folder, guid, version in [('Propeller Flight Core', '69A8A34027DA65C5', 'unversioned-local-source'),
                              ('ThermalPostProcessAssets_69623A037A721B91', '69623A037A721B91', '1.0.23')]:
    base = addons / folder
    files = [{'path': p.relative_to(base).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(base.rglob('*')) if p.is_file() and p.suffix not in ('.rdb','.log')]
    if not files:
        raise SystemExit(f'Missing dependency {guid}')
    items.append({'id': guid, 'version': version, 'files': files})
(ROOT / 'Docs/dependencies.json').write_text(json.dumps({'gameVersion':'1.8.0.13','dependencies':items},indent=2))
print('Recorded external dependency manifests; no dependency assets copied')
