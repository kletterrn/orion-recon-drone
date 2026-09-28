from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parents[3]
P=W/'AssetProduction/Orion_Banderol_R3_v001'
report={}
for label,path in [('Orion',P/'Orion/Orion_Master.blend'),('Banderol',P/'Banderol/S8000_Banderol_VisualFit_Master.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(1)
 rows=[]
 for o in bpy.data.objects:
  if o.library or not (o.name.startswith(('ORION_','BDLF_','BANDEROL_'))):continue
  if o.type not in {'MESH','EMPTY','ARMATURE','CURVE'}:continue
  bb=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type in {'MESH','CURVE'} else []
  rows.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,location=list(o.matrix_world.translation),bounds=[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)] if bb else [],collections=[c.name for c in o.users_collection],modifiers=[m.type for m in o.modifiers] if o.type=='MESH' else []))
 report[label]={'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':rows}
(W/'Integration/RC8/Reports/source_inventory.json').write_text(json.dumps(report,indent=2))
print('RC8_INVENTORY_COMPLETE',flush=True)
