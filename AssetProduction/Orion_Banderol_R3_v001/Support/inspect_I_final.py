from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
def shape(o):return hashlib.sha256(str(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
checks=[]
pairs=[('Orion/Orion_Master.blend','Orion/checkpoints/Orion_E_sensor_fix_v007.blend'),('Banderol/S8000_Banderol_Master.blend','Banderol/checkpoints/S8000_Banderol_G_wings_v004.blend'),('Banderol/S8000_Banderol_VisualFit_Master.blend','Banderol/checkpoints/S8000_Banderol_VisualFit_v001.blend'),('Assembly/Orion_Banderol_Preview.blend','Assembly/checkpoints/Orion_Banderol_H_compact_pylon_v009.blend')]
for current,old in pairs:
 states=[]
 for name in [old,current]:
  bpy.ops.wm.open_mainfile(filepath=str(P/name));s=bpy.context.scene;s.frame_set(1)
  col=bpy.data.collections['ASSEMBLY_COMPACT_VISUAL_PYLON' if 'Assembly/' in name else '10_SOURCE']
  states.append({o.name:{'shape':shape(o),'local_matrix':[list(r) for r in o.matrix_basis],'parent':o.parent.name if o.parent else None} for o in col.all_objects if o.type=='MESH'})
 changed=[n for n in states[0] if states[0][n]!=states[1].get(n)]
 checks.append({'file':current,'geometry_and_rest_transforms_preserved':not changed,'changed_components':changed,'material_override':bpy.context.scene.view_layers[0].material_override.name if bpy.context.scene.view_layers[0].material_override else None})
 assert not changed,changed
(P/'Documentation/I_shape_preservation_v001.json').write_text(json.dumps(checks,indent=2))
# Additional direct inspection fill makes the enclosed inner lining visible.
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));bpy.context.window.scene=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];s=bpy.context.scene;s.frame_set(160);bpy.data.objects['ORION_REVIEW_FLOOR'].hide_render=True
d=bpy.data.cameras.new('I_BAY_INSPECTION');cam=bpy.data.objects.new('I_BAY_INSPECTION',d);s.collection.objects.link(cam);cam.location=(.42,-2.7,-1.5);cam.rotation_euler=(Vector((.115,-1.65,-.08))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=1.9;s.camera=cam
ld=bpy.data.lights.new('I_DIRECT_INSPECTION_FILL','AREA');lo=bpy.data.objects.new('I_DIRECT_INSPECTION_FILL',ld);s.collection.objects.link(lo);lo.location=(0,-1.75,-.8);lo.rotation_euler=(Vector((0,-1.7,.05))-lo.location).to_track_quat('-Z','Y').to_euler();ld.energy=80;ld.size=.25
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.view_layers[0].material_override=None;s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type=='OPTIX'
for o in s.objects:
 if o.type=='FONT':o.hide_render=True
s.render.filepath=str(P/'Previews/I_v001_Orion_BayInterior.png');bpy.ops.render.render(write_still=True)
print('I_GEOMETRY_INSPECTION_COMPLETE',flush=True)
