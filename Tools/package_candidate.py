"""Package a verified runtime directory and its editable source, without publishing."""
from pathlib import Path
import argparse
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('packed', type=Path)
parser.add_argument('--candidate', default='rc5')
args = parser.parse_args()
candidate = args.candidate
if not candidate.startswith('rc') or not candidate[2:].isdigit():
    parser.error('candidate must be rc followed by digits')
if not (args.packed / 'data.pak').is_file():
    parser.error('packed directory has no data.pak')
out = ROOT / 'ReleaseCandidates'
out.mkdir(exist_ok=True)
docs = ['README.md', 'VERSION.txt', 'CHANGELOG.md', 'ASSET_PROVENANCE.md',
        f'VALIDATION_{candidate.upper()}.md']
docs += [p.name for p in ROOT.glob('VALIDATION_RC*.md') if p.name not in docs]
allowed = {'.blend', '.fbx', '.xob', '.meta', '.emat', '.edds', '.tif', '.et', '.c',
           '.layout', '.imageset', '.conf', '.ent', '.layer', '.wav', '.acp', '.sig', '.py',
           '.ps1', '.mjs', '.txt', '.json', '.md', '.ct', '.pp'}
rc8_extra = [
    'AssetProduction/Orion_Banderol_R3_v001/Orion/Orion_Master.blend',
    'AssetProduction/Orion_Banderol_R3_v001/Banderol/S8000_Banderol_Master.blend',
    'Integration/RC8/Blender/Orion_RC8_Motion_v017.blend',
    'Integration/RC8/Blender/Orion_RC8_Motion_v020.blend',
    'Integration/RC8/Blender/Orion_RC8_Motion_v022.blend',
    'Integration/RC8/Blender/Orion_RC8_Skinned_v003.blend',
    'Integration/RC8/Blender/Orion_RC8_Skinned_v004.blend',
    'Integration/RC8/Blender/Orion_RC8_Skinned_v006.blend',
    'Integration/RC8/Blender/Banderol_RC8_Motion_v004.blend',
    'Integration/RC8/Blender/Assembly_RC8_Motion_v017.blend',
    'Integration/RC8/GameSources/Orion_RC8_Game.blend',
    'Integration/RC8/GameSources/Orion_RC8_Game_v002.blend',
    'Integration/RC8/GameSources/Orion_RC8_Game_v004.blend',
    'Integration/RC8/GameSources/Orion_RC8_Game_v010.blend',
    'Integration/RC8/GameSources/Banderol_RC8_Game_v003.blend',
    'Integration/RC8/Audio/SourceArchives/Orion_SYNTHETIC_audio_illustration.zip',
    'Integration/RC8/Audio/SourceArchives/S8000_Banderol_SYNTHETIC_sound_pack.zip',
    'Integration/RC8/Reports/native_import_audit.json',
    'Integration/RC8/Reports/native_resource_manifest.json',
    'Integration/RC8/Reports/packed_integrity_rc8.json',
    'Integration/RC8/Reports/runtime_stage_manifest.json',
    'Integration/RC8/Reports/orion_uv_order_fix.json',
    'Integration/RC8/Reports/bay_skin_clearance_v020.json',
    'Integration/RC8/Reports/orion_skin_v004.json',
    'Integration/RC8/Reports/orion_game_build_v003.json',
    'Integration/RC8/Reports/orion_uv_order_fix_v004.json',
    'Integration/RC8/Support/author_native_resources.py',
    'Integration/RC8/Support/export_final_fbx.py',
    'Integration/RC8/Support/fix_export_uv_order.py',
    'Integration/RC8/Support/audit_native_import.py',
    'Integration/RC8/Support/check_packed_rc8.mjs',
    'Integration/RC8/Support/stage_rc8_runtime.py',
    'Integration/RC8/Support/build_audio_projects.py',
    'Integration/RC8/Support/build_game_assets_v002.py',
    'Integration/RC8/Support/build_orion_skin_v003.py',
    'Integration/RC8/Support/trim_exposed_main_bay_liners_v018.py',
    'Integration/RC8/Support/restore_main_bay_side_skin_v019.py',
    'Integration/RC8/Support/validate_bay_skin_clearance.py',
    'Integration/RC8/Support/isolate_bay_skin_material_v022.py',
    'Integration/RC8/Support/rebake_bay_skin_paint_v009.py',
    'Integration/RC8/Support/rebake_bay_skin_normal_v010.py',
    'Integration/RC8/Support/build_motion_v017.py',
    'Integration/RC8/Support/build_banderol_motion_v003.py',
    'Integration/RC8/Support/validate_motion_full.py',
    'Integration/RC8/Support/validate_sensor_v017.py',
    'Integration/RC8/Previews/Orion_Game_LOD0_Review.png',
    'Integration/RC8/Previews/Banderol_Game_LOD0_Review.png',
    'Integration/RC8/Reports/marked_bay_v020_id.png',
]
results = []
for kind in ['source', 'packed']:
    path = out / f'Orion-E-v1.0.0-{candidate}-{kind}.zip'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
        for name in docs:
            archive.write(ROOT / name, name)
        for p in (ROOT / 'ValidationEvidence' / candidate.upper()).rglob('*'):
            if p.is_file():
                archive.write(p, p.relative_to(ROOT))
        if kind == 'packed':
            for p in args.packed.iterdir():
                if p.is_file():
                    archive.write(p, Path(f'OrionE_{candidate.upper()}') / p.name)
        else:
            archive.write(ROOT / 'ReconDrones.gproj', 'ReconDrones.gproj')
            if candidate == 'rc8':
                for relative in rc8_extra:
                    file = ROOT / relative
                    if not file.is_file():
                        raise FileNotFoundError(file)
                    archive.write(file, relative)
                for file in (ROOT / 'Integration/RC8/GameSources/textures').glob('*.png'):
                    archive.write(file, file.relative_to(ROOT))
                for file in (ROOT / 'Integration/RC8/GameSources/textures_v003').glob('*.png'):
                    archive.write(file, file.relative_to(ROOT))
                for file in (ROOT / 'Integration/RC8/GameSources/textures_v010').glob('*.png'):
                    archive.write(file, file.relative_to(ROOT))
            for folder in ['Assets', 'Configs', 'Prefabs', 'Scripts', 'Sounds', 'UI', 'Worlds', 'Missions', 'Tools']:
                for p in (ROOT / folder).rglob('*'):
                    if not p.is_file() or p.suffix not in allowed:
                        continue
                    if 'WorkbenchGame' in p.parts or 'OrionE_Reference' in p.parts or p.name.endswith('.reference.txt'):
                        continue
                    if p.suffix == '.meta' and not p.with_suffix('').is_file():
                        continue
                    archive.write(p, p.relative_to(ROOT))
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(bad)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    results.append(f'{digest}  {path.name}')
    print(path.name, path.stat().st_size, digest)
(out / f'SHA256-{candidate}.txt').write_text('\n'.join(results) + '\n', encoding='utf-8')
