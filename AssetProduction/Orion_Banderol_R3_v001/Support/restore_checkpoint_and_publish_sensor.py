from pathlib import Path
import bpy,shutil
P=Path(__file__).resolve().parents[1]
cached=Path('C:/Users/david/AppData/Local/Temp/Orion_E_reopen_e7575eco/Orion/Orion_Master.blend')
bpy.ops.wm.open_mainfile(filepath=str(cached));s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];assert s['revision']=='E_v005'
assert len(bpy.data.collections['10_SOURCE'].all_objects)==263
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Orion/checkpoints/Orion_E_exterior_rig_v005.blend'))
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_E_sensor_fix_v003.blend'));assert bpy.data.scenes['ORION_GEOMETRY_REVIEW']['revision']=='E_sensor_v003'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
print('APPROVED_E005_CHECKPOINT_RESTORED_FROM_VERIFIED_RELOCATION_COPY_AND_SENSOR_MASTER_PUBLISHED')
