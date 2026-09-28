from pathlib import Path
import bpy,json
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'))
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];bpy.context.window.scene=s
rev=s['revision'].replace('D_','')
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
floor=bpy.data.objects['ORION_REVIEW_FLOOR'];views=[]
# Fill from below for inspection photographs of the actual enclosed liners.
ld=bpy.data.lights.new('D_INSPECTION_FILL','AREA');lo=bpy.data.objects.new('D_INSPECTION_FILL',ld);s.collection.objects.link(lo);lo.location=(1,-.8,-3.2);lo.rotation_euler=(Vector((0,-.8,-.1))-lo.location).to_track_quat('-Z','Y').to_euler();ld.energy=90;ld.shape='DISK';ld.size=2
specs=[('Hero',1,(12,16,8),(0,0,-.05),None,False),('Forward_Detail',1,(3.6,6.7,.4),(0,1.65,-.65),3.0,True),('Sensor',1,(1.6,4.7,-.50),(0,2.05,-.80),1.15,True),('Nose_Gear',1,(2.6,3.5,-.6),(0,1.37,-.86),1.8,True),('Main_Gear',1,(3.2,-3.5,-.45),(.70,-1.10,-.86),2.2,True),('Bays_Down_Underside',1,(1.8,-1.1,-4.0),(0,-.15,-.35),4.2,True),('Retracted_Underside',120,(2.6,-.6,-4.3),(0,-.5,-.32),4.8,True),('Inspection',160,(1.3,-1.5,-3.5),(0,-.7,-.35),3.4,True),('Inside_Open',100,(1.3,-1.5,-3.5),(0,-.7,-.35),3.4,True),('Nose_Bay_Interior',160,(.38,.15,-1.7),(0,.62,-.13),1.7,True),('Main_Bay_Interior',160,(.42,-2.7,-1.5),(.115,-1.65,-.08),1.9,True)]
for name,fr,pos,target,scale,hidefloor in specs:
 s.frame_set(fr);floor.hide_render=hidefloor;lo.hide_render='Bay' not in name and 'Inside' not in name and name!='Inspection'
 d=bpy.data.cameras.new('D_REVIEW_'+name);o=bpy.data.objects.new('D_REVIEW_'+name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 if scale:d.type='ORTHO';d.ortho_scale=scale
 else:d.lens=46
 s.camera=o;s.render.filepath=str(P/f'Previews/D_{rev}_{name}.png');bpy.ops.render.render(write_still=True)
 views.append({'view':name,'frame':fr,'image':f'Previews/D_{rev}_{name}.png'})
for view in ['FRONT','REAR','LEFT','RIGHT','TOP','UNDERSIDE']:
 s.frame_set(1);floor.hide_render=True;lo.hide_render=True;s.camera=bpy.data.objects['ORION_CAM_'+view];s.view_layers[0].material_override=bpy.data.materials['ORION_NEUTRAL_CLAY'];s.render.resolution_x=1800;s.render.resolution_y=1000
 s.render.filepath=str(P/f'Previews/D_{rev}_Clay_{view}.png');bpy.ops.render.render(write_still=True);views.append({'view':'Clay_'+view,'frame':1,'image':f'Previews/D_{rev}_Clay_{view}.png'})
(P/f'Documentation/D_renders_{rev}.json').write_text(json.dumps(views,indent=2))
print('D_RENDERS_COMPLETE',len(views))
