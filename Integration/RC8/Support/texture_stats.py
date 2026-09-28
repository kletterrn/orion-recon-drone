from PIL import Image,ImageStat
from pathlib import Path
import json
p=Path('Integration/RC8/GameSources/textures');r=[]
for f in sorted(p.glob('*.png')):
 im=Image.open(f).convert('RGB');sm=im.resize((128,128));st=ImageStat.Stat(sm);r.append({'name':f.name,'bytes':f.stat().st_size,'mode':im.mode,'size':im.size,'mean':[round(v,1) for v in st.mean],'stddev':[round(v,1) for v in st.stddev]})
print(json.dumps(r,indent=2))
