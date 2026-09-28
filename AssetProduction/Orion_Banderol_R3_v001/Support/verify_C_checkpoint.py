"""Inspect saved stage C source meshes without resaving them."""
import bpy,bmesh,json,math,hashlib,tempfile,shutil,subprocess,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
REV=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v002'
report={'stage':'C primary geometry','status':'pending','files':[],'scope':'Technical integrity, not reference authenticity or final rig clearance'}
manifest=json.loads((ROOT/'Documentation/source_manifest.json').read_text())
for p,h in manifest['existing_asset_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
report['original_asset_hashes']='unchanged'
for relative in ['Orion/Orion_Master.blend',f'Orion/checkpoints/Orion_C_primary_geometry_{REV}.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/relative))
    s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];assert s.unit_settings.scale_length==1
    root=bpy.data.objects['ORION_ROOT'];assert all(abs(root.matrix_world[i][j]-(i==j))<1e-6 for i in range(4) for j in range(4))
    objects=[o for o in bpy.data.collections['10_SOURCE'].all_objects if o.type=='MESH'];assert len(objects)>=20
    meshes=[];points=[];dg=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
        bm=bmesh.new();bm.from_mesh(o.data)
        bad_edges=sum(not e.is_manifold for e in bm.edges)
        tiny_faces=sum(f.calc_area()<1e-10 for f in bm.faces)
        volume=bm.calc_volume(signed=True)
        meshes.append({'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':bad_edges,'degenerate_faces':tiny_faces,'signed_volume_m3':volume})
        bm.free()
        assert bad_edges==0,(o.name,bad_edges)
        assert tiny_faces==0,(o.name,tiny_faces)
        assert volume>0,(o.name,volume)
        ev=o.evaluated_get(dg);points.extend(ev.matrix_world@Vector(c) for c in ev.bound_box)
    span=max(p.x for p in points)-min(p.x for p in points);length=max(p.y for p in points)-min(p.y for p in points)
    assert abs(span-16)<.08 and abs(length-8)<.04,(span,length)
    assert len(bpy.data.collections['40_EXPORT'].all_objects)==0
    assert all(not o.name.endswith('ENVELOPE') and 'NOT_FINAL' not in o.name for o in objects)
    assert all(o.type!='CAMERA' and 'REVIEW_FLOOR' not in o.name for o in bpy.data.collections['ORION_ASSET'].all_objects)
    refs=[i for i in bpy.data.images if i.source=='FILE'];assert len(refs)==5
    assert all(i.filepath.startswith('//') and Path(bpy.path.abspath(i.filepath)).is_file() for i in refs)
    report['files'].append({'file':relative,'source_meshes':len(objects),'span_m':span,'length_m':length,'mesh_checks':meshes,'relative_references':'passed'})
with tempfile.TemporaryDirectory(prefix='orion_C_relocation_') as tmp:
    relocated=Path(tmp)/ROOT.name;shutil.copytree(ROOT,relocated)
    expr='import bpy; from pathlib import Path; assert all(Path(bpy.path.abspath(i.filepath)).is_file() for i in bpy.data.images if i.source=="FILE"); assert "ORION_FUSELAGE" in bpy.data.objects; print("C_RELOCATION_PASS")'
    result=subprocess.run([bpy.app.binary_path,'--background','--disable-autoexec',str(relocated/'Orion/Orion_Master.blend'),'--python-exit-code','1','--python-expr',expr],capture_output=True,text=True,timeout=60)
    assert result.returncode==0 and 'C_RELOCATION_PASS' in result.stdout,result.stdout+result.stderr
report['relocated_fresh_process_reopen']='passed';report['status']='passed'
(ROOT/f'Documentation/C_validation_{REV}.json').write_text(json.dumps(report,indent=2))
print('C_VALIDATION_PASS',[(f['span_m'],f['length_m'],f['source_meshes']) for f in report['files']])
