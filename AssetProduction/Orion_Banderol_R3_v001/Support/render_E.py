from pathlib import Path
import bpy,json
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s;rev=s['revision'].removeprefix('E_');root=bpy.data.objects['ORION_ROOT'];s.frame_set(1);s.cycles.samples=32;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
views=[('Hero',(12,16,8),(0,0,-.05),None),('Forward_Exterior',(-4,5.5,1.2),(0,1.6,-.15),4.4),('Dorsal_Panel',(-2.1,2.5,1.7),(0,1.35,.10),2.8),('Rear_Propeller',(2.9,-5,1.2),(0,-3.1,.2),3.4),('Left_Tip',(-8.4,.3,.8),(-7.94,-.685,.26),.5),('Rig_Pose',(12,16,8),(0,0,-.05),None),('Clay_Hero',(12,16,8),(0,0,-.05),None),('Underside_Apertures',(-1.5,4.7,-.60),(0,2.95,-.375),.8)]
records=[]
for name,pos,target,scale in views:
 for prop in ['flap_l_degrees','flap_r_degrees','aileron_l_degrees','aileron_r_degrees','ruddervator_l_degrees','ruddervator_r_degrees','propeller_degrees','sensor_yaw_degrees','sensor_pitch_degrees']:root[prop]=0.
 if name=='Rig_Pose':
  for prop,val in {'flap_l_degrees':8,'flap_r_degrees':8,'aileron_l_degrees':-8,'aileron_r_degrees':8,'ruddervator_l_degrees':8,'ruddervator_r_degrees':-8,'propeller_degrees':45,'sensor_yaw_degrees':25,'sensor_pitch_degrees':-10}.items():root[prop]=val
 root.update_tag();bpy.context.view_layer.update()
 d=bpy.data.cameras.new('E_'+name);cam=bpy.data.objects.new('E_'+name,d);s.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 if scale:d.type='ORTHO';d.ortho_scale=scale
 else:d.lens=40
 s.camera=cam;bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=scale is not None;s.view_layers[0].material_override=bpy.data.materials['ORION_NEUTRAL_CLAY'] if name=='Clay_Hero' else None
 s.render.filepath=str(P/f'Previews/E_{rev}_{name}.png');bpy.ops.render.render(write_still=True);records.append({'view':name,'path':f'Previews/E_{rev}_{name}.png'})
(P/f'Documentation/E_renders_{rev}.json').write_text(json.dumps(records,indent=2));print('E_RENDERS',len(records))
