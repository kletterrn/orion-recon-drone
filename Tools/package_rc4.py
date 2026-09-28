from pathlib import Path
import zipfile, hashlib
ROOT=Path(__file__).resolve().parents[1]
PACK=Path((ROOT/'RC4FinalPacked.txt').read_text().strip())
OUT=ROOT/'ReleaseCandidates';OUT.mkdir(exist_ok=True)
docs=['README.md','VERSION.txt','CHANGELOG.md','ASSET_PROVENANCE.md','VALIDATION_RC4.md']
for kind in ['source','packed']:
 path=OUT/f'Orion-E-v1.0.0-rc4-{kind}.zip'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as archive:
  for name in docs: archive.write(ROOT/name,name)
  for p in (ROOT/'ValidationEvidence/RC4').glob('*'):
   if p.is_file(): archive.write(p,p.relative_to(ROOT))
  if kind=='packed':
   for p in PACK.iterdir():
    if p.is_file():archive.write(p,Path('OrionE_RC4')/p.name)
  else:
   archive.write(ROOT/'ReconDrones.gproj','ReconDrones.gproj')
   allowed={'.blend','.fbx','.xob','.meta','.emat','.edds','.et','.c','.layout','.imageset','.conf','.ent','.layer','.wav','.py','.ps1','.mjs','.txt','.json','.md','.ct','.pp'}
   for folder in ['Assets','Configs','Prefabs','Scripts','Sounds','UI','Worlds','Missions','Tools']:
    for p in (ROOT/folder).rglob('*'):
     if not p.is_file() or p.suffix not in allowed:continue
     if 'WorkbenchGame' in p.parts or 'OrionE_Reference' in p.parts or p.name.endswith('.reference.txt'):continue
     if p.suffix=='.meta' and not p.with_suffix('').is_file():continue
     archive.write(p,p.relative_to(ROOT))
 with zipfile.ZipFile(path) as archive:
  bad=archive.testzip()
  if bad:raise RuntimeError(bad)
 print(path.name,path.stat().st_size,hashlib.sha256(path.read_bytes()).hexdigest())
