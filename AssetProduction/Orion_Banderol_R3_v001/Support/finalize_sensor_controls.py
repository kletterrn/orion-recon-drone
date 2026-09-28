from pathlib import Path
import bpy
P=Path(__file__).resolve().parents[1];check=P/'Orion/checkpoints/Orion_E_sensor_fix_v007.blend';assert not check.exists()
bpy.ops.wm.open_mainfile(filepath=str(P/'Orion/checkpoints/Orion_E_sensor_fix_v006.blend'))
root=bpy.data.objects['ORION_ROOT'];root.id_properties_ui('sensor_pitch_degrees').update(min=-10,max=10,soft_min=-10,soft_max=10,description='Visual pitch limited to tested +/-10 degrees; not sensor specifications')
pitch=bpy.data.objects['ORION_SENSOR_PITCH'];pitch.animation_data.drivers[0].driver.expression='radians(max(-10,min(10,v)))';pitch['visual_range_degrees']='-10 to +10; clearance-limited illustrative presentation'
s=bpy.data.scenes['ORION_GEOMETRY_REVIEW'];s['revision']='E_sensor_v007';s.frame_set(1);root['sensor_pitch_degrees']=0.;root['sensor_yaw_degrees']=0.;root.update_tag();bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Orion/Orion_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(check),copy=True);print('SENSOR_V007_SAVED')
