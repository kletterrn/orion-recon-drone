from pathlib import Path
import bpy,json
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
s=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1)
shape=[(-.393,-.648),(-.202,-.648),(-.140,-.441),(-.393,-.441),(-.410,-.454)]
for sign in [-1,1]:
    o=bpy.data.objects[f'PYLON_REMOVABLE_SIDE_COVER_{sign}']
    for v in o.data.vertices:v.co.y,v.co.z=shape[v.index%5]
    o.data.update()
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath))
s['revision']='H_compact_pylon_v009';s.camera=bpy.data.objects['H_SIDE']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_H_compact_pylon_v009.blend'),copy=True,relative_remap=True)
r=json.loads((P/'Documentation/H_compact_validation_v008.json').read_text());r['final_revision']='v009: narrower cosmetic cover seams and relative library links; exterior collision envelope unchanged'
r['library_paths']=[lib.filepath for lib in bpy.data.libraries];r['visual_inspection']='pending v009 captures'
(P/'Documentation/H_compact_validation_v009.json').write_text(json.dumps(r,indent=2))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
for label,cam in [('Side','H_SIDE'),('Hero','H_COMPACT_HERO'),('Pylon','H_SUPPORT_CLOSEUP'),('Underside','H_UNDERSIDE'),('RotorClearance','H_ROTOR_CLEARANCE')]:
    s.camera=bpy.data.objects[cam]
    for o in s.objects:
        if o.type=='FONT' and not o.library:o.hide_render=o.parent!=s.camera
    s.render.filepath=str(P/f'Previews/H_v009_{label}.png');bpy.ops.render.render(write_still=True)
print('V009_FINAL_COMPLETE')
