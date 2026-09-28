from pathlib import Path
import bpy,json
from mathutils import Matrix
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';D=Matrix(((1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
tracks={};r=json.loads((I/'Reports/orion_skin_v002.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Orion_RC8_Skinned_v002.blend'));s=bpy.context.scene
axes={name:list(-(D.to_3x3()@bpy.data.objects[source].rotation_axis_angle[1:])) for source,name in []}
axes={}
for source,name in r['bones'].items():
 o=bpy.data.objects[source]
 if o.rotation_mode=='AXIS_ANGLE':
  from mathutils import Vector
  axes[name]=list(-(D.to_3x3()@Vector(o.rotation_axis_angle[1:])).normalized())
for source,name in r['bones'].items():tracks[name]=[]
for k in range(239):
 f=1+k*.5;s.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update()
 for source,name in r['bones'].items():tracks[name].append(D@bpy.data.objects[source].matrix_world@D)
tracks={n:keys for n,keys in tracks.items() if any(max(abs(a-b) for ra,rb in zip(M,keys[0]) for a,b in zip(ra,rb))>1e-6 for M in keys)}
bpy.ops.wm.open_mainfile(filepath=str(I/'Blender/Banderol_RC8_Motion_v004.blend'));root=bpy.data.objects['BANDEROL_VISUALFIT_ROOT'];arm=bpy.data.objects['BDL_RC8_EXPORT_RIG']
for side in ['L','R']:tracks['BDL_Wing_'+side]=[]
for k in range(121):
 root['deployment']=k/120;root.update_tag();bpy.context.view_layer.update()
 for side in ['L','R']:tracks['BDL_Wing_'+side].append(D@arm.pose.bones['BDL_Wing_'+side].matrix@D)
lines=['// Generated from executed Blender integration checkpoints. Re-run sample_runtime_pose.py after rig edits.','class ORD_RC8PoseData','{',' static void Populate(map<string,ref ORD_RC8Curve> curves)',' {'];data={}
for name,keys in tracks.items():
 rows=[];last=None
 for M in keys:
  q=M.to_quaternion()
  if last:q.make_compatible(last)
  last=q.copy();rows.append([*M.translation,q.x,q.y,q.z,q.w])
 data[name]=rows;text=';'.join(' '.join(f'{v:.8g}' for v in row) for row in rows)
 lines.append('  curves.Insert("'+name+'",new ORD_RC8Curve("'+text+'"));')
lines+=[' }',' static vector Axis(string name)',' {','  switch(name)','  {']
for name,axis in axes.items():lines.append('   case "'+name+'": return "'+' '.join(f'{x:.9g}' for x in axis)+'";')
lines+=['  }','  return "1 0 0";',' }','}'];(W/'Scripts/Game/ORD/ORD_RC8PoseData.c').write_text('\n'.join(lines)+'\n');(I/'Reports/runtime_pose_samples.json').write_text(json.dumps(data));print('RC8_POSE_DATA',len(tracks),'tracks',flush=True)
