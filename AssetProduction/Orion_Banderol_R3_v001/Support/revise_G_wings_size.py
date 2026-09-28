from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
P=Path(__file__).resolve().parents[1];cp=P/'Banderol/checkpoints/S8000_Banderol_G_wings_v003.blend';assert not cp.exists()
orion=P/'Orion/Orion_Master.blend';before=hashlib.sha256(orion.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'))
root=bpy.data.objects['BANDEROL_ROOT'];src=bpy.data.collections['10_SOURCE'];grey=bpy.data.materials['BDL_LIGHT_GREY_REVIEW']
def wing(n,side):
 M=40;outline=[]
 for i in range(M+1):outline.append(((1-math.cos(math.pi*i/M))/2,1))
 for i in range(M,-1,-1):outline.append(((1-math.cos(math.pi*i/M))/2,-1))
 stations=[(.04,.30,.35,.018),(.15,.30,.35,.014),(.30,.295,.347,.009),(.70,.285,.34,.008),(1.065,.275,.33,.007),(1.10,.267,.31,.005)]
 v=[];f=[];K=len(outline)
 for r,y,c,t in stations:
  for u,sign in outline:
   hh=max(.0006,t*(.2969*math.sqrt(u)-.126*u-.3516*u*u+.2843*u**3-.1015*u**4)/.10003)
   v.append((side*r,y-u*c,-.163+sign*hh))
 for k in range(len(stations)-1):
  for j in range(K):f.append((k*K+j,k*K+(j+1)%K,(k+1)*K+(j+1)%K,(k+1)*K+j))
 f.extend([tuple(reversed(range(K))),tuple((len(stations)-1)*K+j for j in range(K))])
 o=bpy.data.objects[n];d=bpy.data.meshes.new(n+'_G003_MESH');d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o.data=d;d.materials.append(grey)
 for q in d.polygons:q.use_smooth=len(q.vertices)==4
 o['evidence']='R14 photo straight narrow outline; C section/chord/station. 2.2m span inference from GUR Size entry; not measured'
for side,label in [(-1,'L'),(1,'R')]:
 wing('BDL_WING_'+label,side)
 for v in bpy.data.objects['BDL_WING_ROOT_FAIRING_'+label].data.vertices:v.co.y-=.75
 bpy.data.objects['BDL_WING_ROOT_ROUNDED_COVER_'+str(side)].location.y-=.75
root['provisional_wing_span_m']=2.2;root['wing_span_status']='Provisional 2.2m span: inference from GUR ambiguous Size; published secondary descriptions agree; no measured primary span'
root['wing_pose']='Visual extended photo-like pose; authentic folding/stow not established'
root['nose_join_y_m']=1.48;root['main_wing_leading_root_y_m']=.30;root['stage']='G_WING_SIZE_CORRECTION'
s=bpy.context.scene;s['revision']='G_v003';s['stage']='G_WING_SIZE_REVIEW';s['status']='Approximate reported length/width; revised provisional span. No engineering/engine validation.'
bpy.data.objects['BDL_CAM_Front'].data.ortho_scale=2.7;bpy.data.objects['BDL_CAM_Rear'].data.ortho_scale=2.7
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(P/'Banderol/S8000_Banderol_Master.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(cp),copy=True)
shutil.copy2('C:/Users/david/AppData/Local/Temp/codex-clipboard-e72beb45-8fa7-4664-8122-f9e470700cff.png',P/'Support/references_private/R14_Banderol_wings_photo.png')
(P/'Documentation/G_parameters_v003.json').write_text(json.dumps(dict(root.items()),indent=2))
(P/'Documentation/G_Orion_preservation_v003.json').write_text(json.dumps({'orion_master_sha256_before':before,'orion_master_sha256_after':hashlib.sha256(orion.read_bytes()).hexdigest(),'unchanged':before==hashlib.sha256(orion.read_bytes()).hexdigest()},indent=2))
print('G_WINGS_SAVED')
