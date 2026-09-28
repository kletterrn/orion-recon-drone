"""Fresh-process setup inspection. Does not save or alter the .blend files."""
from pathlib import Path
import bpy
import hashlib
import json
import math
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'Documentation/source_manifest.json').read_text(encoding='utf-8'))
report={'stage':'A/B setup only','blender_version':bpy.app.version_string,'files':[],'checks':[]}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
for path,expected in manifest['existing_asset_sha256'].items():
    assert sha(Path(path))==expected, f'Existing asset changed: {path}'
report['checks'].append('Three existing Blender assets retain recorded SHA-256 hashes')
for ref in manifest['references']:
    assert sha(ROOT/ref['local'])==ref['sha256'], ref['id']
report['checks'].append('All five supplied image copies match their original hashes')
for relative in ['Orion/Orion_Master.blend','Orion/checkpoints/Orion_B_reference_scale_v001.blend']:
    path=ROOT/relative
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene=bpy.data.scenes['ORION_SCALE_REVIEW']
    assert scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1
    root=bpy.data.objects['ORION_ROOT']
    assert all(abs(root.matrix_world[i][j]-(1 if i==j else 0))<1e-7 for i in range(4) for j in range(4))
    assert len(bpy.data.collections['10_SOURCE'].objects)==0
    assert len(bpy.data.collections['40_EXPORT'].objects)==0
    assert bpy.data.objects['ORION_PAYLOAD_SOCKET']['status'].startswith('UNPLACED')
    assert scene.camera.name=='ORION_CAM_TOP'
    assert len([o for o in scene.objects if o.type=='CAMERA'])==7
    assert len(bpy.data.objects['ORION_CAM_R3_INITIAL'].data.background_images)==1
    assert bpy.data.objects['ORION_CAM_R3_INITIAL']['match_status'].startswith('INITIAL_ONLY')
    for name,expected in [('ORION_NOMINAL_LENGTH_8M',8),('ORION_NOMINAL_SPAN_16M',16)]:
        spline=bpy.data.objects[name].data.splines[0]
        actual=(spline.points[0].co.xyz-spline.points[-1].co.xyz).length
        assert abs(actual-expected)<1e-6,(name,actual)
    images=[]
    for image in bpy.data.images:
        if image.source!='FILE': continue
        absolute=Path(bpy.path.abspath(image.filepath))
        assert image.filepath.startswith('//'),image.filepath
        assert absolute.is_file(),absolute
        assert not image.packed_file
        images.append({'name':image.name,'path':image.filepath,'width':image.size[0],'height':image.size[1]})
    assert len(images)==5
    publishing=bpy.data.collections['ORION_ASSET']
    assert all(o.type!='MESH' and o.type!='CAMERA' for o in publishing.all_objects)
    assert all(math.isfinite(v) for o in bpy.data.objects for v in o.matrix_world.translation)
    report['files'].append({'file':relative,'status':'passed','reference_images':images,
        'authoritative_aircraft_meshes':0,'export_meshes':0,'review_cameras':7})
report['checks']+=['Both files reopened without resaving','Metric scale and identity root',
    'Eight-metre and sixteen-metre guide endpoints','Seven review cameras and explicitly unsolved R3 backdrop',
    'Five relative image paths resolve from both master and numbered checkpoint',
    'No reference/audit meshes in future assembly-link collection',
    'No source or export meshes mislabeled as completed aircraft']
for name in ['Orion_AB_Scale_Setup.png','AB_Reference_Audit_PRIVATE.png']:
    path=ROOT/'Previews'/name
    assert path.is_file() and path.stat().st_size>10000
    image=bpy.data.images.load(str(path))
    assert tuple(image.size)==(2400,1200),(name,tuple(image.size))
report['checks'].append('Two 2400x1200 setup renders exist and decode in Blender')
with tempfile.TemporaryDirectory(prefix='orion_AB_relocation_') as tmp:
    relocated=Path(tmp)/'Orion_Banderol_R3_v001'
    shutil.copytree(ROOT,relocated)
    expression='import bpy; from pathlib import Path; files=[i for i in bpy.data.images if i.source=="FILE"]; assert len(files)==5; assert all(i.filepath.startswith("//") and Path(bpy.path.abspath(i.filepath)).is_file() for i in files); print("RELOCATED_REFERENCE_PATHS_PASS")'
    for relative in ['Orion/Orion_Master.blend','Orion/checkpoints/Orion_B_reference_scale_v001.blend']:
        result=subprocess.run([bpy.app.binary_path,'--background','--disable-autoexec',str(relocated/relative),
            '--python-exit-code','1','--python-expr',expression],capture_output=True,text=True,timeout=60)
        assert result.returncode==0 and 'RELOCATED_REFERENCE_PATHS_PASS' in result.stdout,result.stdout+result.stderr
report['checks'].append('Both files reopen from a temporary relocated package and resolve all five private images')
report['status']='passed'
(ROOT/'Documentation/AB_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
