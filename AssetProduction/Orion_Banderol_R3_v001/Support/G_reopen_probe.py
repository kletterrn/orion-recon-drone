import bpy
from pathlib import Path
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p/'Banderol/checkpoints/S8000_Banderol_G_wings_v004.blend'))
assert bpy.data.scenes['BANDEROL_GEOMETRY_REVIEW']['revision']=='G_v004'
assert 'BANDEROL_ROOT' in bpy.data.objects
assert 'ORION_ROOT' not in bpy.data.objects
assert len(bpy.data.collections['10_SOURCE'].objects)>11
print('G_STANDALONE_REOPEN_OK')
