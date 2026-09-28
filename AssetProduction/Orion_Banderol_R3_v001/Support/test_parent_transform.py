import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
p=bpy.data.objects.new('p',None);bpy.context.scene.collection.objects.link(p);p.location=(0,2,-.8)
bpy.ops.mesh.primitive_cylinder_add(radius=.1,depth=.1,location=(0,2.3,-.8));o=bpy.context.object;o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector((0,1,0)).to_track_quat('Z','Y')
bpy.context.view_layer.update();world=o.matrix_world.copy();print('BEFORE',o.rotation_quaternion[:],world)
o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted();o.matrix_world=world
print('AFTER',o.rotation_quaternion[:],o.matrix_world)
bpy.context.view_layer.update();print('UPD',o.rotation_quaternion[:],o.matrix_world)
