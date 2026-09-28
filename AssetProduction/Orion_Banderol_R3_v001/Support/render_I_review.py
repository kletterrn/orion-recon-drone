from pathlib import Path
import bpy,json
from mathutils import Vector
P=Path(__file__).resolve().parents[1];renders=[]
def setup():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=32;s.cycles.use_denoising=True
 s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 return s
def capture(s,label,cam):
 s.camera=cam
 for o in s.objects:
  if o.type=='FONT' and not o.library:o.hide_render=o.parent!=cam
 path=P/f'Previews/I_v001_{label}.png';s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 renders.append({'view':label,'file':str(path),'frame':s.frame_current});print('I_RENDER',label,flush=True)
def camera(s,name,pos,target,scale):
 d=bpy.data.cameras.new('I_'+name);o=bpy.data.objects.new('I_'+name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;return o
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));bpy.context.window.scene=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];s=setup();s.frame_set(1)
floor=bpy.data.objects['ORION_REVIEW_FLOOR'];floor.hide_render=True
specs=[('Sensor',1,(-3,4,0),(0,2.07,-.6),1.9),('NoseGear',1,(2.6,3.5,-.6),(0,1.37,-.86),1.8),('MainGear',1,(3.2,-3.5,-.45),(.7,-1.1,-.86),2.2),('BayInterior',160,(.42,-2.7,-1.5),(.115,-1.65,-.08),1.9)]
ld=bpy.data.lights.new('I_BAY_FILL','AREA');lo=bpy.data.objects.new('I_BAY_FILL',ld);s.collection.objects.link(lo);lo.location=(1,-.8,-3.2);lo.rotation_euler=(Vector((0,-.8,-.1))-lo.location).to_track_quat('-Z','Y').to_euler();ld.energy=90;ld.size=2
for name,fr,pos,target,scale in specs:
 s.frame_set(fr);lo.hide_render=name!='BayInterior';capture(s,'Orion_'+name,camera(s,name,pos,target,scale))
# Render one real checker-material review of the wing/body UVs, then a clean clay view.
s.frame_set(1);lo.hide_render=True
checker=bpy.data.materials.new('I_UV_CHECKER_REVIEW');checker.use_nodes=True;nt=checker.node_tree;p=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');c=nt.nodes.new('ShaderNodeTexChecker');c.inputs['Scale'].default_value=64;nt.links.new(tc.outputs['UV'],c.inputs['Vector']);nt.links.new(c.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.65
s.view_layers[0].material_override=checker;capture(s,'Orion_UVChecker',bpy.data.objects['ORION_CAM_TOP'])
s.view_layers[0].material_override=bpy.data.materials['ORION_NEUTRAL_CLAY'];capture(s,'Orion_Clay',bpy.data.objects['ORION_CAM_RIGHT'])
bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'));bpy.context.window.scene=bpy.data.scenes['BANDEROL_GEOMETRY_REVIEW'];s=setup();s.frame_set(1)
for o in s.objects:
 if o.type=='MESH' and 'FLOOR' in o.name:o.hide_render=True
capture(s,'Banderol_Reference',camera(s,'BDL_HERO',(3,4,2),(0,0,0),5.8))
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'));bpy.context.window.scene=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];s=setup();s.frame_set(1)
for label,cam in [('Assembly','H_COMPACT_HERO'),('Pylon','H_SUPPORT_CLOSEUP'),('Side','H_SIDE')]:capture(s,label,bpy.data.objects[cam])
(P/'Documentation/I_renders_v001.json').write_text(json.dumps(renders,indent=2));print('I_RENDERS_COMPLETE',flush=True)
