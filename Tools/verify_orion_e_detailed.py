"""Reopen the delivered asset and check self-contained scene integrity."""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'Assets/ORD/Models/OrionE_Detailed'
bpy.ops.wm.open_mainfile(filepath=str(out/'OrionE_Detailed.blend'))
s=bpy.context.scene
assert s.camera and s.camera.name=='01 | HERO'
assert len([o for o in s.objects if o.type=='CAMERA'])==9
assert all(math.isfinite(v) for m in bpy.data.meshes for p in m.vertices for v in p.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert all(f.packed_file for f in bpy.data.fonts if f.filepath and f.filepath!='<builtin>')
def world_points(objects):
 return [o.matrix_world@Vector(p) for o in objects if o.type in {'MESH','CURVE'} for p in o.bound_box]
turret=world_points(bpy.data.collections['05 | Optical turret'].objects)
nosegear=world_points([o for o in s.objects if o.get('assembly')=='NOSE'])
clearance=min(p.y for p in turret)-max(p.y for p in nosegear)
assert clearance>.15, f'Turret should be wholly ahead of nose gear: {clearance}'
assert s['Turret center Y']>s['Nose gear axle Y']
assert s['Revision'].startswith('04')
assert s['Wing root reference Z']==1.73
assert s['V-tail tip lateral X']==1.72
body=world_points([bpy.data.objects['Continuous graphite fuselage']])
nose=world_points([bpy.data.objects['Sculpted white radome']])
assert max(p.x for p in nose)>.49
assert max(p.z for p in nose)>2.12
assert s['Radome boundary Y']==1.18
wordmark=[o for o in s.objects if o.name.startswith('ORiON-e custom outline')]
assert len(wordmark)>=24
assert not any(o.name.startswith('Aircraft identity') for o in s.objects)
assert (out/'ORION-e_vector_wordmark.svg').exists()
for name in ['Hero','Nose_Detail','Rear_Detail','Side','Top','Forward_Profile','Reference_Angle','Logo_Detail','Gear_Detail']:
 p=out/(name+'.png');assert p.exists() and p.stat().st_size>100000
 expected=(1920,1280) if name in ['Side','Top','Forward_Profile','Rear_Detail'] else (3840,2560)
 image=bpy.data.images.load(str(p));assert tuple(image.size)==expected;bpy.data.images.remove(image)
result={'status':'passed','checks':['Blend reopened','Nine inspection cameras','Revision 04 silhouette dimensions','Forward camera retained as requested','Custom outlined wordmark geometry and SVG','Finite mesh coordinates','Packed references and font','Five 3840 x 2560 renders and four 1920 x 1280 renders'],'turret_gear_longitudinal_clearance_m':round(clearance,3),'wordmark_outline_meshes':len(wordmark),'mesh_objects':sum(o.type=='MESH' for o in s.objects),'base_polygons':sum(len(o.data.polygons) for o in s.objects if o.type=='MESH')}
(out/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
