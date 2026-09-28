"""Stage runtime resources only; exclude photographs, renders and editable sources."""
import shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=Path(tempfile.mkdtemp(prefix='ORD_DetailedRuntime_'))
extensions={'.xob','.emat','.edds','.et','.ent','.layer','.conf','.layout','.imageset','.c','.wav','.gproj','.ct','.pp'}
for folder in ['Assets','Sounds','Configs','Prefabs','Scripts','UI','Worlds','Missions']:
    for source in (ROOT/folder).rglob('*'):
        if not source.is_file():continue
        if 'WorkbenchGame' in source.parts:continue
        suffix=source.suffix
        if suffix=='.meta':
            target=source.with_suffix('')
            if target.suffix not in extensions or not target.is_file():continue
        elif suffix not in extensions:continue
        dest=STAGE/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
shutil.copy2(ROOT/'ReconDrones.gproj',STAGE/'ReconDrones.gproj')
print(STAGE)
