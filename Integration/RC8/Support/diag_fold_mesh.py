import bpy
from pathlib import Path
from mathutils import Vector
p='C:/Users/david/Desktop/RECON DRONES/Integration/RC8/Blender/Banderol_RC8_Motion_v004.blend';bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene;s.frame_set(1);r=bpy.data.objects['BANDEROL_VISUALFIT_ROOT'];print('DEP',r.get('deployment'));arm=bpy.data.objects['BDL_RC8_EXPORT_RIG'];print('ROOTPOSE',[(x.name,list(x.matrix.translation)) for x in arm.pose.bones]);c=bpy.data.collections['BDL_RC8_SKINNED_SOURCE']
for o in c.objects:
 if o.type!='MESH':continue
 bones=[g.name for g in o.vertex_groups if g.name.startswith('BDL_Wing')]
 if not bones:continue
 raw=[o.matrix_world@v.co for v in o.data.vertices];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();ev=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
 if not raw or len(raw)!=len(ev):continue
 print('OBJECT',o.name,'bone',bones,'parent',o.parent.name if o.parent else None,'hide',o.hide_get(),o.hide_render,'raw',list(raw[0]),'eval',list(ev[0]),'maxdiff',max((a-b).length for a,b in zip(raw,ev)))
