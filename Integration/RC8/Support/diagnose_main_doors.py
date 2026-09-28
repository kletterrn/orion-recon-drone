from pathlib import Path
code=Path(__file__).with_name('solve_door_timing.py').read_text().split('fixed=[]',1)[0]
exec(compile(code,'door_diagnostic_setup','exec'))
parts=[]
for o in bpy.data.collections['ORION_GEAR_BAYS'].all_objects:
 if o.type not in {'MESH','CURVE'} or 'MAIN_R_DOOR_' not in o.name or 'FIXED_EAR' in o.name:continue
 parts.append((o.name,geo(o,oi.matrix_world),oi.matrix_world@o.parent.matrix_world.translation))
s.frame_set(50);gt={o.name:union([geo(o,oi.matrix_world)]) for o in bpy.data.collections['ORION_GEAR'].all_objects if o.type in {'MESH','CURVE'} and not o.hide_render}
rows=[]
for angle in range(0,211,30):
 hits=[]
 for n,(v,f),p in parts:
  R=Matrix.Translation(p)@Matrix.Rotation(math.radians(-angle),4,'Y')@Matrix.Translation(-p);tree=union([([R@x for x in v],f)])
  hits.extend([n,gn] for gn,t in gt.items() if tree.overlap(t))
 rows.append({'angle':angle,'hits':hits})
(I/'Reports/main_door_frame50.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
