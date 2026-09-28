from pathlib import Path
import bpy,json,subprocess,shutil
P=Path(__file__).resolve().parents[1]
paths=['Orion/Orion_Master.blend','Banderol/S8000_Banderol_Master.blend','Banderol/S8000_Banderol_VisualFit_Master.blend','Assembly/Orion_Banderol_Preview.blend']
rel=P/'Support/validation_relocated_I_v001'
for name in paths:
 dest=rel/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,dest)
for folder in ['Orion/textures','Banderol/textures','Assembly/textures','Support/references_private']:
 if (P/folder).exists():shutil.copytree(P/folder,rel/folder,dirs_exist_ok=True)
checks=[]
checkpoints=['Orion/checkpoints/Orion_I_uv_materials_v001.blend','Banderol/checkpoints/BDL_Reference_I_uv_materials_v001.blend','Banderol/checkpoints/BDL_VisualFit_I_uv_materials_v001.blend','Assembly/checkpoints/Orion_Banderol_I_materials_v001.blend']
for path in [P/n for n in paths+checkpoints]+[rel/paths[-1]]:
 r=subprocess.run([bpy.app.binary_path,'--background','--python',str(P/'Support/verify_I_uv.py'),'--',str(path)],capture_output=True,text=True,timeout=180)
 line=next((l for l in r.stdout.splitlines() if l.startswith('I_UV_JSON ')),None)
 checks.append({'success':r.returncode==0 and line is not None,'report':json.loads(line[10:]) if line else (r.stdout+r.stderr)[-3000:]});print('I_REOPEN',path,checks[-1]['success'],flush=True)
report={'fresh_process_checks':checks,'material_validation':'path/UV overlap checks performed; native renders inspected separately','engine_validation':'NOT ATTEMPTED','combined_gear_retraction':'Known intersections unchanged; not accepted as clear','high_to_low_baking':'Deferred to optimized export meshes; current tangent maps are source-surface bakes'}
(P/'Documentation/I_validation_v001.json').write_text(json.dumps(report,indent=2))
assert all(c['success'] and not c['report']['missing_images'] for c in checks)
print('I_PACKAGE_VERIFICATION_COMPLETE',flush=True)
