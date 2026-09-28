import bpy,json,sys
from pathlib import Path
target=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(target))
libraries=[{'path':l.filepath,'absolute':bpy.path.abspath(l.filepath),'exists':Path(bpy.path.abspath(l.filepath)).exists()} for l in bpy.data.libraries]
assert all(l['exists'] for l in libraries)
missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath,library=i.library)).exists()]
assert not missing,missing
data={'target':str(target),'libraries':libraries,'missing_images':missing,'scenes':[s.name for s in bpy.data.scenes]}
if 'H_CARRIAGE_DIAGNOSTIC' in bpy.data.scenes:
 s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s
 s.frame_set(1);a=bpy.data.objects['ORION_NOSE_TIRE'].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy()
 s.frame_set(120);b=bpy.data.objects['ORION_NOSE_TIRE'].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy()
 data['linked_gear_motion_metres']=(a-b).length;assert data['linked_gear_motion_metres']>.1
 s.frame_set(1);dg=bpy.context.evaluated_depsgraph_get()
 data['render_mesh_instances']=sum(i.object.type=='MESH' for i in dg.object_instances if i.is_instance)
 assert data['render_mesh_instances']>250
 assert len(libraries)==2
print('H_PROBE_JSON '+json.dumps(data))
