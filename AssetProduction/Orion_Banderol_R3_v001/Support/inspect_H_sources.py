from pathlib import Path
import bpy,json
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));s=bpy.context.scene;s.frame_set(1)
def bounds(objects):
 pts=[o.matrix_world@Vector(p) for o in objects if o.type in ['MESH','CURVE'] for p in o.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
r={'scene':s.name,'root':list(bpy.data.objects['ORION_ROOT'].location),'collections':[c.name for c in bpy.data.collections],'source_objects':{n:bounds([bpy.data.objects[n]]) for n in ['ORION_FUSELAGE','ORION_NOSE_WHITE','ORION_SENSOR_PITCH_HOUSING','ORION_PROPELLER_BLADE_A']},'groups':{n:bounds(bpy.data.collections[n].all_objects) for n in ['ORION_GEAR','ORION_GEAR_BAYS','ORION_SENSOR_R3']},'gear_objects':[o.name for o in bpy.data.collections['ORION_GEAR'].all_objects]}
(P/'Documentation/H_source_inventory.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
