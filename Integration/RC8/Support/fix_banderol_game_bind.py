"""Align Banderol game geometry to the folded source pose before native export."""
from pathlib import Path
import bpy,json
W=Path('C:/Users/david/Desktop/RECON DRONES');I=W/'Integration/RC8'
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Banderol_RC8_Motion_v004.blend'));arm=bpy.data.objects['BDL_RC8_EXPORT_RIG'];source={name:arm.pose.bones[name].matrix.copy()@arm.data.bones[name].matrix_local.inverted() for name in ['BDL_Wing_L','BDL_Wing_R']}
bpy.ops.wm.open_mainfile(filepath=str(I/'GameSources/Banderol_RC8_Game.blend'));s=bpy.context.scene
counts={name:0 for name in source};examples={}
for o in s.objects:
 if o.type!='MESH' or not (o.name.endswith('_HIGH') or any(o.name.endswith('_LOD'+str(i)) for i in range(4))):continue
 groups={name:o.vertex_groups.get(name) for name in source}
 for v in o.data.vertices:
  for name,g in groups.items():
   if not g:continue
   try:w=g.weight(v.index)
   except RuntimeError:continue
   if w<.99:raise RuntimeError('Nonrigid wing weight '+o.name+' '+name)
   if name not in examples:examples[name]={'before':list(v.co)}
   v.co=source[name]@v.co;counts[name]+=1;examples[name]['after']=list(v.co)
 o.data.update()
bpy.context.preferences.filepaths.save_version=0
out=I/'GameSources/Banderol_RC8_Game_v003.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),relative_remap=True)
report={'input':'Banderol_RC8_Game.blend','output':str(out),'source':'Banderol_RC8_Motion_v004.blend','changed_vertices':counts,'example':examples,'rest_bones':'already folded in v002','status':'folded bind geometry; engine import pending'}
(I/'Reports/banderol_fold_bind_fix.json').write_text(json.dumps(report,indent=2));print('BDL_FOLD_FIXED',counts,flush=True)
