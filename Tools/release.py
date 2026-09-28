"""Portable runtime staging, resource checks and native Workbench packaging."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ('Assets', 'Sounds', 'Configs', 'Prefabs', 'Scripts', 'UI', 'Worlds', 'Missions')
EXTENSIONS = {'.xob', '.emat', '.edds', '.et', '.ent', '.layer', '.conf', '.layout',
              '.imageset', '.c', '.wav', '.acp', '.sig', '.ct', '.pp'}


def resources():
    yield ROOT / 'ReconDrones.gproj'
    for folder in FOLDERS:
        for path in sorted((ROOT / folder).rglob('*')):
            if not path.is_file() or 'WorkbenchGame' in path.parts:
                continue
            underlying = path.with_suffix('') if path.suffix == '.meta' else path
            if underlying.suffix in EXTENSIONS and underlying.is_file():
                yield path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    paths = list(resources())
    required = ['Worlds/ORD/ORD_Runway_Layers/default.layer',
                'Scripts/Game/ORD/ORD_OpticalCamera.c',
                'Sounds/ORD/RC8/ORD_Orion_RC8.acp',
                'Assets/ORD/Models/RC8/ORD_Orion_RC8.xob']
    for name in required:
        assert ROOT / name in paths, f'Missing runtime resource: {name}'
    for path in paths:
        head = path.open('rb').read(128)
        assert head, f'Empty resource: {path}'
        assert not head.startswith(b'version https://git-lfs.github.com/spec/'), f'Run git lfs pull: {path}'
        assert 'references_private' not in path.parts
    assert len(list(ROOT.glob('*.gproj'))) == 1
    print(f'PASS: {len(paths)} nonempty runtime resources; LFS materialized; required scenario/audio/camera resources present')


def build(output):
    out = Path(output).resolve()
    if out == ROOT or ROOT in out.parents or (out.exists() and any(out.iterdir())):
        raise SystemExit('Use a new empty build directory outside the addon tree')
    config = json.loads((ROOT / 'local.build.json').read_text())
    out.mkdir(parents=True, exist_ok=True)
    stage = out / 'stage'
    manifest = []
    for source in resources():
        name = source.relative_to(ROOT)
        dest = stage / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        manifest.append({'path': name.as_posix(), 'sha256': digest(source)})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    command = [config['workbench'], '-gproj', (stage / 'ReconDrones.gproj').as_posix(),
               '-addonsDir', config['addons'], '-profile', (out / 'profile').as_posix(),
               '-wbModule=ResourceManager', '-packAddon', '-packAddonDir', (out / 'packed').as_posix()]
    content = ''
    with (out / 'process.log').open('w') as log:
        startup = None
        if hasattr(subprocess, 'STARTUPINFO'):
            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = 0
        process = subprocess.Popen(command, cwd=config['game'], stdout=log, stderr=subprocess.STDOUT, startupinfo=startup)
        deadline = time.monotonic() + 180
        try:
            while time.monotonic() < deadline:
                logs = list((out / 'profile').rglob('console.log'))
                content = '\n'.join(p.read_text(errors='replace') for p in logs)
                if 'Packaging project successful' in content or 'SCRIPT    (E)' in content or process.poll() is not None:
                    break
                time.sleep(1)
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=15)
    (out / 'build.log').write_text(content, encoding='utf-8')
    if 'Packaging project successful' not in content or not (out / 'packed/data.pak').is_file() or 'SCRIPT    (E)' in content:
        raise SystemExit(f'Build did not pass; inspect {out / "build.log"}')
    print(f'Native package produced: {out / "packed"}; gameplay acceptance remains separate')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['check', 'build'])
    parser.add_argument('--output')
    args = parser.parse_args()
    check()
    if args.action == 'build':
        if not args.output:
            parser.error('build requires --output')
        build(args.output)
