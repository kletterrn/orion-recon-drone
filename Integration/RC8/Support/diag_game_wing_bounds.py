import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='C:/Users/david/Desktop/RECON DRONES/Integration/RC8/GameSources/Banderol_RC8_Game.blend')
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.endswith('_LOD0'):continue
 for bone in ['BDL_Wing_L','BDL_Wing_R']:
  g=o.vertex_groups.get(bone)
  if not g:continue
  verts=[]
  for v in o.data.vertices:
   try:g.weight(v.index);verts.append(o.matrix_world@v.co)
   except RuntimeError:pass
  print(o.name,bone,'count',len(verts),'min',[min(v[k] for v in verts) for k in range(3)],'max',[max(v[k] for v in verts) for k in range(3)])
