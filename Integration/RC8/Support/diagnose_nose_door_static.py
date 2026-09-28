from pathlib import Path
code=Path(__file__).with_name('solve_door_timing.py').read_text().split('fixed=[]',1)[0];exec(compile(code,'setup','exec'))
fixed={}
for col in ['ORION_AIRFRAME','ORION_GEAR_BAYS','ORION_SENSOR_R3']:
 for o in bpy.data.collections[col].all_objects:
  if o.type in {'MESH','CURVE'} and not o.hide_render and 'DOOR_' not in o.name:fixed[o.name]=union([geo(o,oi.matrix_world)])
for o in bi.instance_collection.all_objects:
 if o.type=='MESH' and not o.hide_render:fixed[o.name]=union([geo(o,bi.matrix_world)])
door=bpy.data.objects['ORION_NOSE_DOOR_SHELL_1'];v,f=geo(door,oi.matrix_world);p=oi.matrix_world@door.parent.matrix_world.translation
for a in [15,30,60,90,120,150,180]:
 R=Matrix.Translation(p)@Matrix.Rotation(math.radians(-a),4,'Y')@Matrix.Translation(-p);tree=union([([R@x for x in v],f)])
 print(a,[n for n,t in fixed.items() if tree.overlap(t)],flush=True)
