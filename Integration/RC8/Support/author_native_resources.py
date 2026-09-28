from pathlib import Path
import hashlib,json,re
W=Path('C:/Users/david/Desktop/RECON DRONES');base=W/'Assets/ORD/Models/RC8';I=W/'Integration/RC8';records=[]
def guid(path):return '{'+hashlib.sha256(('RC8:'+path).encode()).hexdigest()[:16].upper()+'}'
def relative(p):return p.relative_to(W).as_posix()
def meta(p,resource,body=''):
 rel=relative(p);(p.parent/(p.name+'.meta')).write_text('MetaFileClass {\n Name "'+guid(rel)+rel+'"\n Configurations {\n  '+resource+' PC {\n'+body+'  }\n  '+resource+' HEADLESS : PC {}\n  '+resource+' XBOX_ONE : PC {}\n  '+resource+' XBOX_SERIES : PC {}\n  '+resource+' PS4 : PC {}\n  '+resource+' PS5 : PC {}\n }\n}\n');return guid(rel)+rel
for label in ['Orion','Banderol']:
 report=json.loads((I/'Reports'/(label.lower()+'_final_fbx.json')).read_text());groups=[m.removeprefix('RC8_') for m in report['materials']]
 assigns=[]
 for group in groups:
  tex={suffix:base/'Textures'/(group+'_'+suffix+'.tif') for suffix in ['BCR','NMO']}
  for suffix,p in tex.items():
   if not p.exists():raise RuntimeError('Missing '+str(p))
   edds=p.with_suffix('.edds')
   body='   SourceFile "'+p.name+'"\n   Conversion ColorHQCompression\n'
   if suffix=='BCR':body+='   ColorSpace ToSRGB\n'
   if not (edds.parent/(edds.name+'.meta')).exists():meta(edds,'TIFFResourceClass',body)
  mat=base/'Data'/('RC8_'+group+'.emat');mat.parent.mkdir(parents=True,exist_ok=True)
  texres={suffix:guid(relative(p.with_suffix('.edds')))+relative(p.with_suffix('.edds')) for suffix,p in tex.items()}
  # Measured against the rendered RC8 daylight capture: the default multiplier
  # washed the grey airframe and wing paint almost white in Enfusion.
  grade={'Orion_Airframe':('0.3','1'), 'Orion_Bay_Skin':('0.55','1'), 'Orion_Wing_L':('0.25','1.7'),
         'Orion_Wing_R':('0.25','1.7'), 'Orion_Tail_Rear':('0.25','1.7')}
  color,roughness=grade.get(group,('1','1'))
  mat.write_text('MatPBRBasic {\n SurfaceProperties "{5EAA7FB0A83F90CF}Common/Materials/Game/plastic.gamemat"\n Color '+color+' '+color+' '+color+' 1\n MetalnessScale 1\n RoughnessScale '+roughness+'\n BCRMap "'+texres['BCR']+'"\n NMOMap "'+texres['NMO']+'"\n}\n')
  matres=meta(mat,'EMATResourceClass');source='RC8_'+group;assigns.append('    MaterialAssignClass "'+guid(relative(mat)+'::assign')+'" {\n     SourceMaterial "'+source+'"\n     AssignedMaterial "'+matres+'"\n    }')
  records.append({'material':source,'emat':matres,'textures':texres})
 xob=base/('ORD_'+label+'_RC8.xob')
 if not xob.exists():xob.touch()
 body='   ExportSkinning 1\n   ExportSceneHierarchy 1\n   MaterialAssigns {\n'+'\n'.join(assigns)+'\n   }\n   GeometryParams {\n'
 for name in report['colliders']:body+='    GeometryParam "'+name+'" {\n     LayerPreset "Vehicle"\n     Mass 0\n     Margin 0\n    }\n'
 body+='   }\n'
 xobres=meta(xob,'FBXResourceClass',body)
 records.append({'asset':label,'model':xobres,'source':relative(base/('ORD_'+label+'_RC8.fbx'))})
(I/'Reports/native_resource_manifest.json').write_text(json.dumps(records,indent=2));print('NATIVE_RESOURCES_PREPARED',len(records))
