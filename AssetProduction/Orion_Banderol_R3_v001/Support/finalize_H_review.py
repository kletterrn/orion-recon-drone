from pathlib import Path
import bpy
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
m=bpy.data.materials['REVIEW_LABEL_WHITE'];nt=m.node_tree;nt.nodes.clear()
e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(.78,.84,.91,1);e.inputs[1].default_value=1
out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface'])
diag=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC'];bpy.context.window.scene=diag
for o in diag.objects:
    if o.type=='FONT' and o.library is None:
        o.data.body='FAILED PROVISIONAL FIT - NOT DOCUMENTED CARRIAGE\nGear intersections found | amber guide is not a rack | source dimensions preserved'
diag.camera=bpy.data.objects['H_SIDE'];diag.frame_set(1)
for o in diag.objects:
    if o.type=='FONT' and o.library is None:o.hide_render=o.parent!=diag.camera
diag['fit_status']='FAILED: nose gear / main wheel intersections; additional gear-motion contacts'
diag['review']='H_REVIEW.md; diagnostic only. Do not treat as approved carriage.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/Orion_Banderol_Preview.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Assembly/checkpoints/Orion_Banderol_H_review_v003.blend'),copy=True,relative_remap=True)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
for label,cam,frame in [('Side','H_SIDE',1),('Underside','H_UNDERSIDE',1),('Conflict','H_FORWARD_FIT',1),('Retracted','H_RETRACTED',120),('MotionConflict','H_SIDE',80)]:
    bpy.context.window.scene=diag;diag.camera=bpy.data.objects[cam];diag.frame_set(frame)
    for o in diag.objects:
        if o.type=='FONT' and o.library is None:o.hide_render=o.parent!=diag.camera
    diag.render.filepath=str(P/f'Previews/H_v003_{label}.png');bpy.ops.render.render(write_still=True)
scale=bpy.data.scenes['H_SEPARATE_SCALE_REVIEW'];bpy.context.window.scene=scale
scale.render.filepath=str(P/'Previews/H_v003_Scale.png');bpy.ops.render.render(write_still=True)
print('H_FINAL_REVIEW_COMPLETE')
