"""Original Banderol-inspired game mesh; +Y nose exports to Enfusion +Z."""
import bpy, math
from pathlib import Path
R=Path(__file__).resolve().parents[1]; O=R/'Assets/ORD/Models'
bpy.ops.wm.read_factory_settings(use_empty=True)
body=bpy.data.materials.new('ORD_Airframe_Placeholder'); body.diffuse_color=(.42,.46,.40,1)
dark=bpy.data.materials.new('ORD_Dark_Mechanical'); dark.diffuse_color=(.07,.075,.07,1)
def part(name,loc,scale,material=body,kind='cube'):
 if kind=='cube': bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 elif kind=='sphere': bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc)
 else: bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=1,depth=1,location=loc,rotation=(math.pi/2,0,0))
 o=bpy.context.object;o.name=name
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
 o.scale=scale;o.data.materials.append(material)
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);return o
part('BDL_Fuselage',(0,0,0),(.23,3.9,.23),kind='cylinder')
part('BDL_Nose',(0,1.95,0),(.23,.55,.23),kind='sphere')
part('BDL_Exhaust',(0,-2.05,0),(.19,.18,.19),dark,kind='cylinder')
part('BDL_Intake',(0,-.9,-.22),(.23,.65,.16),dark)
for sign in [-1,1]:
 wing=part('BDL_Wing',(sign*.58,-.15,0),(1.05,.32,.035));wing.rotation_euler.z=-sign*.22
 fin=part('BDL_Tail',(sign*.24,-1.67,.1),(.54,.38,.035));fin.rotation_euler.y=-sign*.6
part('BDL_Fin',(0,-1.7,.28),(.035,.45,.48))
for obj in list(bpy.context.scene.objects):
 obj.name += '_LOD0'
 for lod,ratio in [(1,.5),(2,.2)]:
  copy=obj.copy();copy.data=obj.data.copy();bpy.context.collection.objects.link(copy);copy.name=obj.name.replace('LOD0','LOD'+str(lod))
  bpy.context.view_layer.objects.active=copy;mod=copy.modifiers.new('LOD','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name)
part('UBX_Missile',(0,0,0),(.46,4.9,.46))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'ORD_Missile.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'ORD_Missile.fbx'),use_selection=True,object_types={'MESH'},axis_forward='Z',axis_up='Y',apply_unit_scale=True,bake_anim=False)
# Retain the existing resource GUID and materials; import all authored LOD meshes.
p=O/'ORD_Missile.xob.meta';s=p.read_text();a=s.index('   MeshParams {');b=s.index('   GeometryParams {',a);s=s[:a]+s[b:];p.write_text(s)
