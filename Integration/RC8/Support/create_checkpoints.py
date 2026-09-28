from pathlib import Path
import bpy,json,hashlib,zipfile,datetime
W=Path(__file__).resolve().parents[3];P=W/'AssetProduction/Orion_Banderol_R3_v001';I=W/'Integration/RC8'
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'motion gate in progress; not accepted for runtime','sources':{}}
specs=[('Orion/Orion_Master.blend','Orion_RC8_Motion_v001.blend'),('Banderol/S8000_Banderol_VisualFit_Master.blend','Banderol_RC8_Motion_v001.blend'),('Assembly/Orion_Banderol_Preview.blend','Assembly_RC8_Motion_v001.blend')]
for src,dest in specs:
 source=P/src;target=I/'Blender'/dest
 if target.exists():raise RuntimeError(f'Refusing overwrite: {target}')
 manifest['sources'][src]={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'integration':dest}
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
 for scene in bpy.data.scenes:
  if not scene.library:scene['RC8_status']='Integration checkpoint; motion gate pending'
 if src.startswith('Assembly'):
  for lib in bpy.data.libraries:
   if Path(bpy.path.abspath(lib.filepath)).name=='Orion_Master.blend':lib.filepath=str(I/'Blender/Orion_RC8_Motion_v001.blend')
   if Path(bpy.path.abspath(lib.filepath)).name=='S8000_Banderol_VisualFit_Master.blend':lib.filepath=str(I/'Blender/Banderol_RC8_Motion_v001.blend')
 bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=True)
 for lib in bpy.data.libraries:
  if lib.filepath.startswith(str(I)):lib.filepath=bpy.path.relpath(lib.filepath)
 bpy.ops.wm.save_as_mainfile(filepath=str(target))
 print('CHECKPOINT_SAVED',dest,flush=True)
backup=I/'Backups/RC7_runtime_before_RC8.zip'
if not backup.exists():
 with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for folder in ['Scripts','Prefabs','Configs','Sounds']:
   for f in (W/folder).rglob('*'):
    if f.is_file():z.write(f,f.relative_to(W))
  for n in ['ReconDrones.gproj','VERSION.txt','README.md','CHANGELOG.md']:
   if (W/n).exists():z.write(W/n,n)
manifest['runtime_backup_sha256']=hashlib.sha256(backup.read_bytes()).hexdigest()
(I/'Reports/baseline_manifest.json').write_text(json.dumps(manifest,indent=2))
print('RC8_CHECKPOINTS_COMPLETE',flush=True)
