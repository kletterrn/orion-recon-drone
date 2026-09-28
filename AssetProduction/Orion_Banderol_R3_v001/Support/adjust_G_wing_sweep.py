from pathlib import Path
import bpy,math,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];cp=P/'Banderol/checkpoints/S8000_Banderol_G_wings_v004.blend';assert not cp.exists()
bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'))
src=bpy.data.collections['10_SOURCE'];before={o.name:hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'utf8') for v in o.data.vertices)).hexdigest() for o in src.objects if o.type=='MESH'}
stations=[(.04,.30),(.15,.30),(.30,.295),(.70,.285),(1.065,.275),(1.10,.267)]
for label in ['L','R']:
 o=bpy.data.objects['BDL_WING_'+label]
 for v in o.data.vertices:
  r=abs(v.co.x)
  for (a,ya),(b,yb) in zip(stations,stations[1:]):
   if r<=b+1e-6:
    old=ya+(yb-ya)*max(0,min(1,(r-a)/(b-a)));break
  new=.30-math.tan(math.radians(12))*max(0,r-.15)
  v.co.y+=new-old
 o.data.update();o['visual_leading_edge_sweep_degrees']=12;o['evidence']='User R15 illustration supports modest rearward sweep; 12 degrees visual estimate, not measured'
root=bpy.data.objects['BANDEROL_ROOT'];root['main_wing_sweep_estimated_degrees']=12
s=bpy.context.scene;s['revision']='G_v004';s['status']='Main wing rearward sweep correction; 2.2m provisional span retained'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(cp),copy=True)
unchanged=all(before[o.name]==hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'utf8') for v in o.data.vertices)).hexdigest() for o in src.objects if o.type=='MESH' and o.name not in ['BDL_WING_L','BDL_WING_R'])
(P/'Documentation/G_sweep_change_v004.json').write_text(json.dumps({'other_base_meshes_unchanged':unchanged,'estimated_leading_sweep_degrees':12,'span_retained_m':2.2},indent=2))
shutil.copy2('C:/Users/david/AppData/Local/Temp/codex-clipboard-a810d03d-e8ad-4d6f-a2ea-457548f0a73e.png',P/'Support/references_private/R15_Banderol_swept_wings.png')
(P/'Documentation/G_parameters_v004.json').write_text(json.dumps(dict(root.items()),indent=2))
print('SWEEP_SAVED',unchanged)
