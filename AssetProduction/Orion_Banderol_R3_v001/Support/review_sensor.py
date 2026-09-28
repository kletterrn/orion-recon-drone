from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;s.frame_set(1);root=bpy.data.objects['ORION_ROOT']
def tree(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);ev.to_mesh_clear();return t
bad=[]
for o in bpy.data.collections['ORION_SENSOR_R3'].objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m)
 nm=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-10 for f in bm.faces);vol=bm.calc_volume(signed=True)
 if nm or deg or vol<=0:bad.append({'object':o.name,'nonmanifold':nm,'degenerate':deg,'volume':vol})
 bm.free();ev.to_mesh_clear()
collisions=[];housing=bpy.data.objects['ORION_SENSOR_PITCH_HOUSING'];obs=[bpy.data.objects['ORION_FUSELAGE'],bpy.data.objects['ORION_NOSE_WHITE']]+[o for o in bpy.data.collections['ORION_GEAR'].objects if o.type=='MESH']
for fr in [1,65,100,120,160]:
 s.frame_set(fr)
 for y in [-35,0,35]:
  for p in [-10,0,10]:
   root['sensor_yaw_degrees']=y;root['sensor_pitch_degrees']=p;root.update_tag();bpy.context.view_layer.update();t=tree(housing)
   for o in obs:
    hit=t.overlap(tree(o))
    if hit:collisions.append({'frame':fr,'yaw':y,'pitch':p,'obstacle':o.name,'pairs':len(hit)})
root['sensor_yaw_degrees']=0.;root['sensor_pitch_degrees']=0.;root.update_tag();s.frame_set(1);bpy.context.view_layer.update()
mount=bpy.data.objects['ORION_SENSOR_FIXED_CONFORMAL_SADDLE'];connection=bool(tree(mount).overlap(tree(bpy.data.objects['ORION_FUSELAGE'])))
report={'fresh_master_open':True,'evaluated_sensor_mesh_defects':bad,'sensor_to_airframe_gear_sampled_contacts':collisions,'mount_intersects_body_intentionally':connection,'pose_samples':45,'engine_validation':'NOT ATTEMPTED'}
(P/'Documentation/SENSOR_validation_v007.json').write_text(json.dumps(report,indent=2));print('SENSOR_CHECKS',report)
s.cycles.samples=32;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=True
for name,pos,target,scale in [('Photo_Angle',(-3,4,0),(0,2.07,-.60),1.9),('Front',(0,4,-.80),(0,2.05,-.80),.95),('Side',(-3,2.05,-.63),(0,2.05,-.63),1.15),('Connection',(-1.3,3,-.15),(0,2.05,-.46),.95)]:
 d=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,d);s.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;s.camera=cam;s.render.filepath=str(P/f'Previews/Sensor_v007_{name}.png');bpy.ops.render.render(write_still=True)
