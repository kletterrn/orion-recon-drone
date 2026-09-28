from pathlib import Path
import bpy,json,math
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'))
objs=list(bpy.data.collections['10_SOURCE'].objects);meshes=[o for o in objs if o.type=='MESH'];curves=[o for o in objs if o.type=='CURVE']
rep=json.loads((P/'Documentation/G_validation_v002.json').read_text());rep['source_objects']=len(objs);rep['source_meshes']=len(meshes);rep['source_curves']=len(curves)
rep['curve_control_points_finite']=all(math.isfinite(x) for o in curves for sp in o.data.splines for pt in sp.points for x in pt.co)
rep['curve_validation_scope']='Finite editable control points only; base manifold test concerns meshes, curves not converted'
rep['body_height_m']=bpy.data.objects['BDL_BODY'].dimensions.z
rep['visual_review']='All ten G v002 generated images visually inspected'
(P/'Documentation/G_validation_v002.json').write_text(json.dumps(rep,indent=2))
(P/'Documentation/G_parameters_v002.json').write_text(json.dumps(dict(bpy.data.objects['BANDEROL_ROOT'].items()),indent=2))
print('G_FINAL',len(meshes),len(curves),rep['curve_control_points_finite'])
