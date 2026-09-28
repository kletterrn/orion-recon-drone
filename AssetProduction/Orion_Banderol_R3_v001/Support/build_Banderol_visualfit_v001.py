from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1];src=P/'Banderol/S8000_Banderol_Master.blend'
before=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
def station(y):
    return y-.30 if y>=.8 else y+.30 if y<=-.8 else y*.625
changes=[]
for o in list(bpy.data.collections['10_SOURCE'].all_objects):
    if o.type not in ['MESH','CURVE']:continue
    mw=o.matrix_world.copy()
    if o.name=='BDL_BODY':
        inv=mw.inverted()
        for v in o.data.vertices:
            p=mw@v.co;p.y=station(p.y);v.co=inv@p
        o.data.update();changes.append({'object':o.name,'change':'Shorten central case stations; retain width/height'})
    else:
        pts=[mw@Vector(p) for p in o.bound_box];centre=(min(p.y for p in pts)+max(p.y for p in pts))/2
        delta=station(centre)-centre;o.location.y+=delta
        changes.append({'object':o.name,'translation_y':delta})
    if o.name.startswith('BDL_'):o.name=o.name.replace('BDL_','BDLF_',1)
bpy.data.collections['BDL_ASSET'].name='BDL_ASSET_FIT'
root=bpy.data.objects['BANDEROL_ROOT'];root.name='BANDEROL_VISUALFIT_ROOT'
root['visual_fit_length_m']=4.4;root['nominal_reference_length_m']=5.0
root['evidence']='User-authorized artistic shortening; do not present as measured real S8000 dimensions'
bpy.data.objects['BANDEROL_ATTACH_ROOT'].name='BANDEROL_VISUALFIT_ATTACH_ROOT'
s['variant']='VISUAL_FIT: 4.4 m; original reference-dimension master preserved'
s['revision']='VisualFit_v001'
for o in bpy.data.objects:
    if o.type=='FONT' and not o.library:o.data.body=o.data.body.replace('5.00','4.40').replace('5 m','4.4 m visual fit')
bpy.context.view_layer.update()
pts=[o.matrix_world@Vector(p) for o in bpy.data.collections['10_SOURCE'].all_objects if o.type=='MESH' for p in o.bound_box]
length=max(p.y for p in pts)-min(p.y for p in pts);assert abs(length-4.4)<1e-4,length
assert all(o.scale==Vector((1,1,1)) for o in [root])
out=P/'Banderol/S8000_Banderol_VisualFit_Master.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/checkpoints/S8000_Banderol_VisualFit_v001.blend'),copy=True,relative_remap=True)
assert hashlib.sha256(src.read_bytes()).hexdigest()==before
(P/'Documentation/Banderol_VisualFit_v001.json').write_text(json.dumps({'original_reference_length':5,'actual_variant_length_m':length,'central_case_shortening_m':.6,'nose_tail_wings_shapes_retained':True,'root_scale':[1,1,1],'changes':changes,'original_master_hash_preserved':before,'status':'Artistic visual-fit variant, no real-world dimension claim'},indent=2))
print('VISUALFIT_COMPLETE',length)
