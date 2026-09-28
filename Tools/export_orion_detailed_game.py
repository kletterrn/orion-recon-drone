"""Export a rigged game copy; never save over the supplied exhibition source."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Assets/ORD/Models/OrionE_Game'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Assets/ORD/Models/OrionE_Detailed/OrionE_Detailed.blend'))
# Packed photographs, lights, cameras and studio surfaces are not game assets.
for obj in list(bpy.data.objects):
    if obj.type not in {'MESH','CURVE','FONT'} or any(c.name.startswith(('08','09')) for c in obj.users_collection):
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.convert(target='MESH')
objects = list(bpy.context.scene.objects)
for obj in objects:
    bpy.context.view_layer.objects.active = obj
    for modifier in list(obj.modifiers):
        # Keep the authored base resolution instead of exhibition subdivisions.
        if modifier.type == 'SUBSURF': obj.modifiers.remove(modifier)
        else:
            try: bpy.ops.object.modifier_apply(modifier=modifier.name)
            except RuntimeError: obj.modifiers.remove(modifier)
    obj.location.z -= 1.12
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)

bones = {'ORD_Root':(0,0,0), 'front_wheel':(0,1.45,-.905),
 'rear_wheel_l':(-1.18,-1.28,-.87),'rear_wheel_r':(1.18,-1.28,-.87),
 'ORD_Propeller':(0,-3.96,.48),'ORD_Aileron_L':(-4.62,-1.813,.66),
 'ORD_Aileron_R':(4.62,-1.813,.66),'ORD_Flap_L':(-.42,-1.88,.66),
 'ORD_Flap_R':(.42,-1.88,.66),'ORD_Tail_L':(-.22,-3.52,.66),
 'ORD_Tail_R':(.22,-3.52,.66),'ORD_Sensor':(0,2.52,.03),
 'ORD_Gear_Nose':(0,1.45,.21),'ORD_Gear_L':(-.35,-1.48,.21),'ORD_Gear_R':(.35,-1.48,.21)}
bpy.ops.object.armature_add(enter_editmode=True)
rig=bpy.context.object; rig.name='ORD_DetailedSkeleton'
root=rig.data.edit_bones[0];root.name='ORD_Root';root.head=(0,0,0);root.tail=(0,0,.3)
for name,position in bones.items():
    if name=='ORD_Root':continue
    bone=rig.data.edit_bones.new(name);bone.head=position;bone.tail=Vector(position)+Vector((0,0,.25));bone.parent=root
for name in ['front_wheel','rear_wheel_l','rear_wheel_r']:
    source=rig.data.edit_bones[name]
    contact=rig.data.edit_bones.new(name+'_contact')
    contact.head=source.head;contact.tail=source.tail;contact.parent=root
bpy.ops.object.mode_set(mode='OBJECT')
groups={}
for obj in objects:
    n=obj.name.lower(); bone='ORD_Root'
    if 'propeller blade' in n or 'pusher spinner' in n: bone='ORD_Propeller'
    elif 'aileron' in n: bone='ORD_Aileron_L' if n.startswith('port') else 'ORD_Aileron_R'
    elif 'flap' in n: bone='ORD_Flap_L' if n.startswith('port') else 'ORD_Flap_R'
    elif 'ruddervator' in n: bone='ORD_Tail_L' if n.startswith('port') else 'ORD_Tail_R'
    elif 'rounded tyre' in n or 'wheel core' in n:
        bone={'NOSE':'front_wheel','PORT':'rear_wheel_l','STARBOARD':'rear_wheel_r'}[obj.name.split()[0]]
    elif any(c.name.startswith('04') for c in obj.users_collection):
        center=sum((v.co for v in obj.data.vertices),Vector())/max(1,len(obj.data.vertices))
        bone='ORD_Gear_Nose' if center.y>0 else ('ORD_Gear_L' if center.x<0 else 'ORD_Gear_R')
    elif any(c.name.startswith('05') for c in obj.users_collection) and 'bearing' not in n: bone='ORD_Sensor'
    groups.setdefault(bone,[]).append(obj)
# Join static detail objects; rigid vertex weights retain individual moving parts.
for bone,parts in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:obj.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
    obj=bpy.context.object;obj.name=bone+'_visual'
    group=obj.vertex_groups.new(name=bone);group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    modifier=obj.modifiers.new('Rigid skin','ARMATURE');modifier.object=rig
    obj.parent=rig

# Preserve detailed close view; reduce geometry for medium and distant views.
for obj in list(bpy.context.scene.objects):
    if obj.type != 'MESH': continue
    base=obj.name; obj.name=base+'_LOD0'
    for lod,ratio in [(1,.22),(2,.045)]:
        reduced=obj.copy();reduced.data=obj.data.copy();bpy.context.collection.objects.link(reduced)
        reduced.name=base+'_LOD'+str(lod)
        bpy.context.view_layer.objects.active=reduced
        dec=reduced.modifiers.new('Distance simplification','DECIMATE');dec.ratio=ratio
        bpy.ops.object.modifier_apply(modifier=dec.name)

# Convex hull proxies stay unskinned; never collide with tiny exhibition hardware.
colliders=[('UBX_Fuselage',(0,.05,.48),(.95,7.8,.85)),
 ('UBX_Wing_L',(-4.15,-.55,.68),(7.65,1.15,.13)),
 ('UBX_Wing_R',(4.15,-.55,.68),(7.65,1.15,.13))]
for name,pos,dim in colliders:
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);obj=bpy.context.object;obj.name=name;obj.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

materials=[]
for mat in list(bpy.data.materials):
    if mat.name.startswith('Studio'):continue
    name='ORD_Detailed_'+hashlib.sha1(mat.name.encode()).hexdigest()[:8]
    color=list(mat.diffuse_color);p=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
    rough=float(p.inputs['Roughness'].default_value) if p else .5
    metal=float(p.inputs['Metallic'].default_value) if p else 0
    guid=hashlib.sha1(name.encode()).hexdigest()[:16].upper()
    (OUT/(name+'.emat')).write_text('MatPBRBasic {\n Color '+' '.join(str(round(v,5)) for v in color)+'\n RoughnessScale '+str(rough)+'\n MetalnessScale '+str(metal)+'\n}\n')
    (OUT/(name+'.emat.meta')).write_text('MetaFileClass {\n Name "{'+guid+'}Assets/ORD/Models/OrionE_Game/'+name+'.emat"\n Configurations {\n  EMATResourceClass PC {}\n }\n}\n')
    mat.name=name
    materials.append((name,guid,name))
meta=['MetaFileClass {',' Name "{9E31A4C705ECBD82}Assets/ORD/Models/OrionE_Game/ORD_Orion_Detailed.xob"',' Configurations {','  FBXResourceClass PC {','   ExportSkinning 1','   ExportSceneHierarchy 1','   MaterialAssigns {']
for original,guid,name in materials:meta+=['    MaterialAssignClass "{'+guid+'}" {','     SourceMaterial "'+original+'"','     AssignedMaterial "{'+guid+'}Assets/ORD/Models/OrionE_Game/'+name+'.emat"','    }']
meta+=['   }','   GeometryParams {']
for name,_,_ in colliders:meta+=['    GeometryParam "'+name+'" {','     LayerPreset "Vehicle"','     Mass 0','     Margin 0','    }']
meta+=['   }','  }','  FBXResourceClass HEADLESS : PC {}','  FBXResourceClass XBOX_ONE : PC {}','  FBXResourceClass XBOX_SERIES : PC {}','  FBXResourceClass PS4 : PC {}','  FBXResourceClass PS5 : PC {}',' }','}']
(OUT/'ORD_Orion_Detailed.xob.meta').write_text('\n'.join(meta)+'\n')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ORD_Orion_Detailed.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'ORD_Orion_Detailed.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False,use_armature_deform_only=False)
(OUT/'export_report.json').write_text(json.dumps({'source':'OrionE_Detailed revision 04','bones':bones,'mesh_objects':len([o for o in bpy.context.scene.objects if o.type=='MESH']),'polygons':sum(len(o.data.polygons) for o in bpy.context.scene.objects if o.type=='MESH'),'materials':len(materials),'vertical_offset':-1.12},indent=2))

