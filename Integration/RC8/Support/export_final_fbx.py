"""Export optimized, skinned LOD assets with small convex collision proxies."""
from pathlib import Path
import bpy,json,sys
from mathutils import Matrix
W=Path('C:/Users/david/Desktop/RECON DRONES');I=W/'Integration/RC8';O=W/'Assets/ORD/Models/RC8';args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];label=args[0] if args else 'Orion';revision=args[1] if len(args)>1 else ('v003' if label=='Banderol' else 'v002');file=label+'_RC8_Game_'+revision+'.blend'
bpy.ops.wm.open_mainfile(filepath=str(I/'GameSources'/file));s=bpy.context.scene;arm=next(o for o in s.objects if o.type=='ARMATURE');lods=[o for o in s.objects if o.type=='MESH' and any(o.name.endswith('_LOD'+str(i)) for i in range(4))];bpy.ops.object.select_all(action='DESELECT');arm.hide_set(False);arm.hide_render=False;arm.select_set(True)
for p in arm.pose.bones:
 for c in list(p.constraints):p.constraints.remove(c)
 p.matrix_basis=Matrix.Identity(4)
for o in lods:o.hide_set(False);o.hide_render=False;o.select_set(True)
colliders=[]
if label=='Orion': specs=[('UBX_Fuselage',(0,0,0),(.78,7.55,.80)),('UBX_Wing_L',(-4.15,-.25,.13),(7.6,1.08,.13)),('UBX_Wing_R',(4.15,-.25,.13),(7.6,1.08,.13))]
else:specs=[('UBX_Body',(0,0,0),(.26,4.25,.26))]
for name,pos,dim in specs:
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);colliders.append(o)
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
for o in lods+colliders:
 o.hide_set(False)
 o.select_set(True)
bpy.context.view_layer.objects.active=arm
assert len(bpy.context.selected_objects)==len(lods)+len(colliders)+1
name='ORD_'+label+'_RC8';out=O/(name+'.fbx')
bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False,use_armature_deform_only=False,path_mode='RELATIVE')
report={'source':str(I/'GameSources'/file),'file':str(out),'bones':[b.name for b in arm.data.bones],'lods':{str(i):sum(len(p.vertices)-2 for o in lods if o.name.endswith('_LOD'+str(i)) for p in o.data.polygons) for i in range(4)},'materials':sorted({m.name for o in lods for m in o.data.materials if m}),'colliders':[o.name for o in colliders],'orientation':'Blender +Y forward to Enfusion +Z forward; verify in native import','status':'FBX exported; native import pending'}
(I/'Reports'/(label.lower()+'_final_fbx.json')).write_text(json.dumps(report,indent=2));print('FBX_DONE',name,report['lods'],flush=True)

