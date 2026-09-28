from pathlib import Path
import bpy, shutil
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'))
for name in ['Top','Underside']:
    bpy.data.objects['BDL_CAM_'+name].data.ortho_scale=8.4
bpy.data.objects['BDL_CAM_Rear'].data.ortho_scale=2.8
clay=bpy.data.materials.new('BDL_NEUTRAL_CLAY');clay.diffuse_color=(.45,.45,.45,1);clay.use_fake_user=True
bpy.context.scene['revision']='F_v002'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/checkpoints/S8000_Banderol_F_primary_v002.blend'),copy=True)
shutil.copy2(P/'Documentation/F_parameters_v001.json',P/'Documentation/F_parameters_v002.json')
