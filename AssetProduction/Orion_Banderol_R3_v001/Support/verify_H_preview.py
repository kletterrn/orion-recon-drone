from pathlib import Path
import bpy, json, subprocess, shutil, hashlib
P=Path(__file__).resolve().parents[1]
rel=P/'Support/validation_relocated_H_v003'
for folder in ['Assembly','Orion','Banderol']:(rel/folder).mkdir(parents=True,exist_ok=True)
for name in ['Assembly/Orion_Banderol_Preview.blend','Orion/Orion_Master.blend','Banderol/S8000_Banderol_Master.blend']:shutil.copy2(P/name,rel/name)
shutil.copytree(P/'Support/references_private',rel/'Support/references_private',dirs_exist_ok=True)
probe=P/'Support/H_reopen_probe.py'
probe.write_text('''import bpy,json,sys
from pathlib import Path
target=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(target))
libraries=[{'path':l.filepath,'absolute':bpy.path.abspath(l.filepath),'exists':Path(bpy.path.abspath(l.filepath)).exists()} for l in bpy.data.libraries]
assert all(l['exists'] for l in libraries)
missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath,library=i.library)).exists()]
assert not missing,missing
data={'target':str(target),'libraries':libraries,'missing_images':missing,'scenes':[s.name for s in bpy.data.scenes]}
if 'H_CARRIAGE_DIAGNOSTIC' in bpy.data.scenes:
 s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s
 s.frame_set(1);a=bpy.data.objects['ORION_NOSE_TIRE'].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy()
 s.frame_set(120);b=bpy.data.objects['ORION_NOSE_TIRE'].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy()
 data['linked_gear_motion_metres']=(a-b).length;assert data['linked_gear_motion_metres']>.1
 s.frame_set(1);dg=bpy.context.evaluated_depsgraph_get()
 data['render_mesh_instances']=sum(i.object.type=='MESH' for i in dg.object_instances if i.is_instance)
 assert data['render_mesh_instances']>250
 assert len(libraries)==2
print('H_PROBE_JSON '+json.dumps(data))
''')
targets=[P/'Orion/Orion_Master.blend',P/'Banderol/S8000_Banderol_Master.blend',P/'Assembly/Orion_Banderol_Preview.blend',P/'Assembly/checkpoints/Orion_Banderol_H_review_v003.blend',rel/'Assembly/Orion_Banderol_Preview.blend']
checks=[]
for path in targets:
    r=subprocess.run([bpy.app.binary_path,'--background','--python',str(probe),'--',str(path)],capture_output=True,text=True,timeout=90)
    line=next((l for l in r.stdout.splitlines() if l.startswith('H_PROBE_JSON ')),None)
    checks.append({'success':r.returncode==0 and line is not None,'details':json.loads(line[13:]) if line else (r.stdout+r.stderr)[-4000:]})
    print('H_REOPEN',path.name,checks[-1]['success'],flush=True)
before=json.loads((P/'Documentation/H_source_preservation_v001.json').read_text())
unchanged=all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in before.items())
clearance=json.loads((P/'Documentation/H_clearance_v001.json').read_text())
report={'fresh_process_reopens':checks,'masters_byte_identical':unchanged,'digital_fit':'FAILED','sampled_gear_frames':clearance['frames_sampled'],'sampled_surface_contacts':len(clearance['surface_intersections']),'relative_library_relocation':checks[-1]['success'],'actual_rack_and_carried_wing_configuration':'BLOCKED BY REFERENCE EVIDENCE','engine_validation':'NOT ATTEMPTED','visual_inspection':'pending final six review renders'}
(P/'Documentation/H_validation_v003.json').write_text(json.dumps(report,indent=2))
assert unchanged and all(c['success'] for c in checks)
print('H_VALIDATION_COMPLETE')
