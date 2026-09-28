from pathlib import Path
p=Path('Integration/RC8/Support/build_orion_skin.py');s=p.read_text(encoding='utf-8-sig').replace('v002','v003')
s=s.replace("helpers['ORD_SensorView']=bpy.data.objects['ORION_SENSOR_PITCH'].matrix_world.copy()", "helpers['ORD_SensorView']=bpy.data.objects['ORION_SENSOR_PITCH'].matrix_world.copy();helpers['ORD_SensorView'].translation+=Vector((0,.37,0))\nhelpers['ORD_PilotView']=Matrix.Translation((0,-9,2.2))")
s=s.replace('mapping=[];copies=[]','mapping=[];copies=[]\noperands={m.object for o in source.all_objects for m in o.modifiers if m.type==\'BOOLEAN\' and m.object}')
s=s.replace("if o.type not in {'MESH','CURVE'} or o.hide_render:continue", "if o.type not in {'MESH','CURVE'} or o.hide_render or o in operands:continue")
p=Path('Integration/RC8/Support/build_orion_skin_v003.py');p.write_text(s)
