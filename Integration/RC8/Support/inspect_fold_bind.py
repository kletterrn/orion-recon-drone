import bpy
from pathlib import Path
from mathutils import Vector
I=Path('C:/Users/david/Desktop/RECON DRONES/Integration/RC8')
for f in ['Blender/Banderol_RC8_Motion_v004.blend','GameSources/Banderol_RC8_Game.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(I/f));s=bpy.context.scene;print('FILE',f)
 for n in ['BDL_RC8_EXPORT_RIG','BANDEROL_VISUALFIT_ROOT']:
  o=bpy.data.objects.get(n);print('OBJ',n,list(o.matrix_world.translation) if o else None)
  if o and o.type=='ARMATURE':
   for b in o.pose.bones:print('BONE',b.name,'rest',list(b.bone.matrix_local.translation),'pose',list(b.matrix.translation),'constraint',len(b.constraints))
 for o in s.objects:
  if o.type=='MESH' and ('Wing_L' in o.name or 'Wing_R' in o.name) and ('SKIN' in o.name or '_LOD0' in o.name):
   v=o.data.vertices[0];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());em=e.to_mesh();print('MESH',o.name,'base',list(o.matrix_world@v.co),'eval',list(e.matrix_world@em.vertices[0].co),'groups',[g.name for g in o.vertex_groups][:4]);e.to_mesh_clear()
