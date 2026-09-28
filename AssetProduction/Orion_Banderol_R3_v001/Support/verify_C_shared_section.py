"""Confirm the saved body carries the nose section through every station ring."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Orion/Orion_Master.blend'))
body=bpy.data.objects['ORION_FUSELAGE'];nose=bpy.data.objects['ORION_NOSE_WHITE']
def normalized(vertices):
    width=max(abs(v.co.x) for v in vertices)
    top=max(v.co.z for v in vertices);bottom=min(v.co.z for v in vertices)
    return [(v.co.x/width,(v.co.z-bottom)/(top-bottom)) for v in vertices]
reference=normalized(list(nose.data.vertices)[:96]);maximum=0;ring_count=0
assert len(body.data.vertices)%96==0
for start in range(0,len(body.data.vertices),96):
    values=normalized(list(body.data.vertices)[start:start+96])
    error=max(abs(a-b) for p,q in zip(values,reference) for a,b in zip(p,q))
    assert error<2e-6,(start,error)
    maximum=max(maximum,error);ring_count+=1
report={'revision':'v007','body_station_rings':ring_count,'same_normalized_section_as_nose':'passed','maximum_normalized_coordinate_error':maximum,'scope':'Same editable cross-section family; no claim of measured hidden geometry'}
(ROOT/'Documentation/C_shared_section_v007.json').write_text(json.dumps(report,indent=2))
print('BODY_NOSE_SECTION_MATCH',ring_count,maximum)
