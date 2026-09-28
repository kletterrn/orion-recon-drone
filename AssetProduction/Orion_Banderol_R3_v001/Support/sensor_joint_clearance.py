from pathlib import Path
import bpy,json
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1);root=bpy.data.objects['ORION_ROOT']
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);ev.to_mesh_clear();return t
hits=[]
for p in [-10,-5,0,5,10]:
 root['sensor_pitch_degrees']=p;root.update_tag();bpy.context.view_layer.update();t=tree(bpy.data.objects['ORION_SENSOR_PITCH_HOUSING'])
 for n in ['ORION_SENSOR_YOKE_-1','ORION_SENSOR_YOKE_1','ORION_SENSOR_YOKE_TOP_BRIDGE','ORION_SENSOR_YAW_COLLAR','ORION_SENSOR_FIXED_CONFORMAL_SADDLE']:
  h=t.overlap(tree(bpy.data.objects[n]))
  if h:hits.append({'pitch':p,'object':n,'pairs':len(h)})
(P/'Documentation/SENSOR_joint_validation_v007.json').write_text(json.dumps(hits,indent=2));print('SENSOR_JOINT',hits)
