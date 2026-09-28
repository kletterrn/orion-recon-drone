import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Users/david/Desktop/RECON DRONES/Integration/RC8/Blender/Orion_RC8_Motion_v016.blend');bpy.context.scene.frame_set(62,subframe=.5)
door=bpy.data.objects['ORION_NOSE_DOOR_SHELL_1'];cut=door.modifiers['RC8_inner_face_tire_clearance'].object
for o in [door,cut,bpy.data.objects['ORION_NOSE_TIRE']]:
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];print(o.name,len(m.vertices),list(e.matrix_world.translation),[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)],flush=True);e.to_mesh_clear()
print([(m.name,m.show_viewport,m.type) for m in door.modifiers]);print('Cut hidden',cut.hide_get(),cut.hide_render)
