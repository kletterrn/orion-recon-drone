"""Refine the new checkpoint after visual QA; never touch prior project assets."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
master=ROOT/'Orion/Orion_Master.blend'
bpy.ops.wm.open_mainfile(filepath=str(master))
s=bpy.data.scenes['ORION_SCALE_REVIEW']
cam=bpy.data.objects['ORION_CAM_TOP'];cam.location=(0,-0.3,30);cam.data.ortho_scale=27
bpy.context.window.scene=s
bpy.context.preferences.filepaths.save_version=0
s.render.filepath=str(ROOT/'Previews/Orion_AB_Scale_Setup.png')
bpy.ops.wm.save_as_mainfile(filepath=str(master))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Orion/checkpoints/Orion_B_reference_scale_v001.blend'),copy=True)
bpy.ops.render.render(write_still=True,scene=s.name)
