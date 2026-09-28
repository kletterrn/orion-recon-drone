from pathlib import Path
import bpy,math
P=Path(__file__).resolve().parents[1];cp=P/'Banderol/checkpoints/S8000_Banderol_G_shape_v002.blend';assert not cp.exists()
bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'))
for side in [-1,1]:
 for k,x in enumerate([.08,.12]):
  bpy.data.objects['BDL_CROWN_FASTENER_'+str(side)+'_'+str(k)].location.z=.005+.165*(1-(x/.15)**3.8)**(1/3.8)+.0015
for label,side in [('L',-1),('R',1)]:
 for v in bpy.data.objects['BDL_WING_ROOT_FAIRING_'+label].data.vertices:v.co.x=side*.085+(v.co.x-side*.085)*.6;v.co.z+=.01
 for v in bpy.data.objects['BDL_TAIL_'+label].data.vertices:v.co.z-=.15
for v in bpy.data.objects['BDL_NOSE'].data.vertices:
 if v.co.y>2.28:v.co.z+=(v.co.y-2.28)/.22*.019
bpy.data.objects['BDL_CAM_Front'].data.ortho_scale=1.55
bpy.context.scene['revision']='G_v002';bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(cp),copy=True)
