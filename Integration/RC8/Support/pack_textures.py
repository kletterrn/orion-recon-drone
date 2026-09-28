from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,sys
W=Path('C:/Users/david/Desktop/RECON DRONES');I=W/'Integration/RC8';args=sys.argv[1:];revision=args[0] if args else ''
src=I/'GameSources'/('textures_'+revision if revision else 'textures');out=W/'Assets/ORD/Models/RC8/Textures';out.mkdir(parents=True,exist_ok=True)
manifest=[]
for f in sorted(src.glob('*_BaseColor.png')):
 group=f.name.removesuffix('_BaseColor.png')
 names={c:src/(group+'_'+c+'.png') for c in ['BaseColor','Roughness','Metallic','Normal','AO']}
 if not all(x.exists() for x in names.values()):raise RuntimeError('Incomplete '+group)
 images={k:Image.open(p).convert('RGB') for k,p in names.items()}
 sizes={k:v.size for k,v in images.items()}
 if len(set(sizes.values()))!=1:raise RuntimeError('Size mismatch '+group)
 base=images['BaseColor'];rough=images['Roughness'].getchannel('R');metal=images['Metallic'].getchannel('R');ao=images['AO'].getchannel('R');normal=images['Normal']
 bcr=Image.merge('RGBA',(*base.split(),rough));nmo=Image.merge('RGBA',(normal.getchannel('R'),ImageChops.invert(normal.getchannel('G')),metal,ao))
 entries={}
 for suffix,img in [('BCR',bcr),('NMO',nmo)]:
  p=out/(group+'_'+suffix+'.tif');img.save(p,compression='tiff_lzw');entries[suffix]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'size':img.size}
 manifest.append({'group':group,**entries,'channels':'BCR: baseRGB roughA (sRGB); NMO: normalX, flippedDirectXnormalY, metallicB, AOA (linear)'})
 print('PACK',group,flush=True)
(I/'Reports'/('texture_pack_'+revision+'.json' if revision else 'texture_pack.json')).write_text(json.dumps(manifest,indent=2))
