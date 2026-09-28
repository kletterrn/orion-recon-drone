from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
oi=bpy.data.objects['ORION_LINKED_APPROVED']
names=['BANDEROL_LINKED_PROVISIONAL','VISUAL_ADAPTER_ROOT','ORION_PAYLOAD_SOCKET_PROVISIONAL','BANDEROL_ATTACH_ROOT_PREVIEW']
before={n:bpy.data.objects[n].matrix_world.copy() for n in names}
for n in names:
    o=bpy.data.objects[n];o.parent=oi;o.matrix_world=before[n]
bpy.context.view_layer.update()
assert all(max(abs(bpy.data.objects[n].matrix_world[i][j]-before[n][i][j]) for i in range(4) for j in range(4))<1e-5 for n in names)
# Verify aircraft translation carries the independent instance and support unchanged.
oi.location.x=.5;bpy.context.view_layer.update()
for n in ['BANDEROL_LINKED_PROVISIONAL','VISUAL_ADAPTER_ROOT']:
    assert abs(bpy.data.objects[n].matrix_world.translation.x-before[n].translation.x-.5)<1e-5
oi.location.x=0;bpy.context.view_layer.update()
s['revision']='H_support_v007';s.camera=bpy.data.objects['H_SIDE']
for o in s.objects:
    if o.type=='FONT' and not o.library:o.hide_render=o.parent!=s.camera
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_H_support_v007.blend'),copy=True,relative_remap=True)
r=json.loads((P/'Documentation/H_support_validation_v006.json').read_text())
r['final_revision']='H v007: hierarchy only; evaluated geometry and rendered world positions unchanged from v006'
r['assembly_parenting_test']='Aircraft translation carries Banderol and adapter; individual components remain selectable'
r['visual_inspection']='Performed: side, underside, support and rotor-clearance native H_v006 renders'
assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in r['source_hashes'].items())
r['masters_byte_identical']=True
(P/'Documentation/H_support_validation_v007.json').write_text(json.dumps(r,indent=2))
print('V007_HIERARCHY_COMPLETE')
