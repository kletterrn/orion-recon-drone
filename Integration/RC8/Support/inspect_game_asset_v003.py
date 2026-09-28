from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';label=sys.argv[-1] if sys.argv[-1] in ('Orion','Banderol') else 'Orion'
bpy.ops.wm.open_mainfile(filepath=str(I/'GameSources'/(label+'_RC8_Game_v003.blend' if label=='Banderol' else label+'_RC8_Game.blend')));s=bpy.context.scene
arm=next(o for o in s.objects if o.type=='ARMATURE');lod={i:[o for o in s.objects if o.type=='MESH' and o.name.endswith('_LOD'+str(i))] for i in range(4)}
materials=set(m.name for objs in lod.values() for o in objs for m in o.data.materials if m)
all_weights=[];missing=[]
for o in lod[0]:
 ng={v.index for v in o.vertex_groups if v.name in arm.data.bones}
 bad=0
 for v in o.data.vertices:
  val=sum(g.weight for g in v.groups if g.group in ng)
  if abs(val-1)>1e-3:bad+=1
 if bad:missing.append((o.name,bad,len(o.data.vertices)))
for o in lod[0]:o.hide_set(False);o.hide_render=False
for level in (1,2,3):
 for o in lod[level]:o.hide_set(True);o.hide_render=True
camera=bpy.data.cameras.new('Review_Camera');co=bpy.data.objects.new('Review_Camera',camera);s.collection.objects.link(co);s.camera=co
co.location=(11,11,5) if label=='Orion' else (5,5,2.6)
target=Vector((0,0,-.1));co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();camera.type='ORTHO';camera.ortho_scale=19 if label=='Orion' else 6.8
for n,loc,power,size in [('key',(8,5,12),1300,9),('fill',(-8,0,7),950,10),('rim',(0,-10,10),1500,7)]:
 data=bpy.data.lights.new(n,'AREA');data.energy=power;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
s.world=bpy.data.worlds.new("Neutral_Review_World");s.world.color=(.4,.4,.4);s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.device='GPU';p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';out=I/'Previews'/(label+'_Game_LOD0_Review.png');out.parent.mkdir(exist_ok=True);s.render.filepath=str(out);s.view_settings.view_transform='AgX';bpy.ops.render.render(write_still=True)
report={'asset':label,'lod_triangles':[sum(len(p.vertices)-2 for o in lod[i] for p in o.data.polygons) for i in range(4)],'bones':len(arm.data.bones),'bone_weight_errors':missing,'materials':sorted(materials),'render':str(out)}
(I/'Reports'/(label.lower()+'_game_inspection.json')).write_text(json.dumps(report,indent=2));print('GAME_INSPECTED',report['lod_triangles'],len(missing),flush=True)


