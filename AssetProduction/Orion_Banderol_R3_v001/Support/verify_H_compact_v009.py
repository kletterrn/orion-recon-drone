from pathlib import Path
import bpy,bmesh,json,subprocess,shutil,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
v=P/'Banderol/S8000_Banderol_VisualFit_Master.blend'
bpy.ops.wm.open_mainfile(filepath=str(v));bad=[]
source=bpy.data.collections['10_SOURCE'].all_objects
for o in source:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-12 for f in bm.faces) or bm.calc_volume()<=0:bad.append(o.name)
    bm.free()
pts=[o.matrix_world@Vector(p) for o in source if o.type=='MESH' for p in o.bound_box]
length=max(p.y for p in pts)-min(p.y for p in pts);assert abs(length-4.4)<1e-4
body=bpy.data.objects['BDLF_BODY'];width=body.dimensions.x;assert abs(width-.3)<1e-4
assert not bad,bad
def variant_tree(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear();return t
body_tree=variant_tree(body);root_contacts=[]
for n in ['BDLF_WING_L','BDLF_WING_R','BDLF_WING_ROOT_FAIRING_L','BDLF_WING_ROOT_FAIRING_R','BDLF_TAIL_L','BDLF_TAIL_R','BDLF_TAIL_TOP']:
    hit=bool(body_tree.overlap(variant_tree(bpy.data.objects[n])));root_contacts.append({'object':n,'case_contact':hit})
    assert hit,n
rel=P/'Support/validation_relocated_H_v009'
for folder in ['Assembly','Orion','Banderol']:(rel/folder).mkdir(parents=True,exist_ok=True)
names=['Assembly/Orion_Banderol_Preview.blend','Orion/Orion_Master.blend','Banderol/S8000_Banderol_Master.blend','Banderol/S8000_Banderol_VisualFit_Master.blend']
for n in names:shutil.copy2(P/n,rel/n)
shutil.copytree(P/'Support/references_private',rel/'Support/references_private',dirs_exist_ok=True)
probe=P/'Support/H_compact_reopen_probe.py'
text=(P/'Support/H_reopen_probe.py').read_text().replace('assert len(libraries)==2','assert len(libraries)==3')
probe.write_text(text)
targets=[P/'Orion/Orion_Master.blend',P/'Banderol/S8000_Banderol_Master.blend',v,P/'Banderol/checkpoints/S8000_Banderol_VisualFit_v001.blend',P/'Assembly/Orion_Banderol_Preview.blend',P/'Assembly/checkpoints/Orion_Banderol_H_compact_pylon_v009.blend',rel/'Assembly/Orion_Banderol_Preview.blend']
checks=[]
for path in targets:
    r=subprocess.run([bpy.app.binary_path,'--background','--python',str(probe),'--',str(path)],capture_output=True,text=True,timeout=90)
    line=next((l for l in r.stdout.splitlines() if l.startswith('H_PROBE_JSON ')),None)
    checks.append({'success':r.returncode==0 and line is not None,'details':json.loads(line[13:]) if line else (r.stdout+r.stderr)[-3000:]});print('V009_REOPEN',path.name,checks[-1]['success'],flush=True)
report=json.loads((P/'Documentation/H_compact_validation_v009.json').read_text())
report['fresh_process_reopens']=checks;report['relocated_three_libraries']=checks[-1]['success'];report['variant_base_mesh_defects']=bad;report['variant_actual_length_m']=length;report['variant_actual_case_width_m']=width
report['variant_root_contacts']=root_contacts
report['reference_masters_hashes_preserved']=all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in report['source_master_hashes'].items())
(P/'Documentation/H_compact_validation_v009.json').write_text(json.dumps(report,indent=2))
assert report['reference_masters_hashes_preserved'] and all(c['success'] for c in checks)
print('V009_VERIFICATION_COMPLETE')
