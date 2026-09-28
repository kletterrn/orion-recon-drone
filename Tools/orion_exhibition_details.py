"""Photo-led exterior details and hand-drawn ORiON-e wordmark.
Executed in build_orion_e_detailed.py's Blender context.
No downloaded model, font replacement or photograph texture is used.
"""

def surface_point(side,y,z,lift=.001):
 w,t,b=profile(y);v=(z-(t+b)/2)/((t-b)/2)
 vv=math.copysign(abs(v)**(1/(SECTION_UPPER_POWER if v>=0 else SECTION_LOWER_POWER)),v)
 return (side*(w*max(.0001,1-vv*vv)**(SECTION_X_POWER/2)+lift),y,z)

def path_resample(points,step=.009,closed=False):
 out=[]
 pairs=list(zip(points,points[1:]+([points[0]] if closed else [])))
 for a,b in pairs:
  n=max(1,int(math.dist(a,b)/step))
  out.extend([tuple(a[k]+(b[k]-a[k])*i/n for k in range(2)) for i in range(n)])
 if not closed:out.append(points[-1])
 return out

def rounded_rect(x,y,w,h,r,n=16):
 pts=[]
 for cx,cy,a0 in [(x+w-r,y+h-r,0),(x+r,y+h-r,90),(x+r,y+r,180),(x+w-r,y+r,270)]:
  for j in range(n+1):
   a=math.radians(a0+90*j/n);pts.append((cx+r*cos(a),cy+r*sin(a)))
 return pts

def ribbon_on_skin(name,coords,width,material,side=1,closed=False,lift=.0015):
 pts=path_resample(coords,.006,closed);verts=[]
 for j,p in enumerate(pts):
  prev=pts[(j-1)%len(pts)] if (closed or j) else pts[j]
  nxt=pts[(j+1)%len(pts)] if (closed or j<len(pts)-1) else pts[j]
  dy=nxt[0]-prev[0];dz=nxt[1]-prev[1];length=max(.000001,math.hypot(dy,dz))
  for sign in [-1,1]:verts.append(surface_point(side,p[0]-sign*dz/length*width/2,p[1]+sign*dy/length*width/2,lift))
 faces=[(2*j,2*j+1,2*((j+1)%len(pts))+1,2*((j+1)%len(pts))) for j in range(len(pts) if closed else len(pts)-1)]
 return mesh(name,verts,faces,MARK,material)

# Remove the inaccurate mechanical detail families that were overly prominent.
for o in list(bpy.data.objects):
 if o.name.startswith(('Airframe service stencil','Flush fastener','Engine cooling louver','Engine intake shadow','Exhaust surround','Exhaust dark interior','Control surface hinge fairing','Rudder hinge cover','Rear ventral antenna','Dorsal communications radome')):
  bpy.data.objects.remove(o,do_unlink=True)

sealmat=mat('Fine graphite panel seal',(.09,.105,.12),.62)
flushmat=mat('Painted fastener faces',(.215,.235,.25),.5,.22)
ochre=mat('Maintenance warning yellow',(.72,.55,.06),.58)
amber=mat('Amber rear beacon',(.86,.19,.012),.21,.08)

def flush_bolt(side,y,z,r=.0031):
 p=Vector(surface_point(side,y,z,.0007));delta=.0003
 dy=Vector(surface_point(side,y+delta,z))-Vector(surface_point(side,y-delta,z))
 dz=Vector(surface_point(side,y,z+delta))-Vector(surface_point(side,y,z-delta))
 normal=dy.cross(dz).normalized()*side
 rod('Recessed flush screw',p,p+normal*.0007,r,DETAIL,flushmat,12)
 # Actual cross recess, fine enough to remain a close-up detail.
 line('Screw cross slot',[p+normal*.001+dy.normalized()*r*.48,p+normal*.001-dy.normalized()*r*.48],.00028,sealmat)

for side in [-1,1]:
 # Rounded access doors: a fine painted seal, without protruding hatch slabs.
 for y,z,w,h,r in [(-.20,1.455,1.31,.492,.15),(-1.04,1.425,.43,.225,.067),(-3.19,1.42,.37,.41,.06)]:
  pts=rounded_rect(y,z,w,h,r)
  ribbon_on_skin('Rounded access panel seal',pts,.0019,sealmat,side,True,.0008)
  for yy in [y+r,y+w-r]:
   for zz in [z+.023,z+h-.023]:flush_bolt(side,yy,zz)
 # Four small flush quarter-turn fasteners around the forward cover.
 for yy,zz in [(-.16,1.59),(.99,1.91),(.01,1.94),(.99,1.51)]:flush_bolt(side,yy,zz,.0035)
 for yy in [-.955,-.685]:
  # White/red pull-tab indicators shown either side of the equipment label.
  ribbon_on_skin('White equipment latch',[(yy,1.535),(yy+.048,1.535)],.020,ink,side)
  ribbon_on_skin('Red equipment latch end',[(yy,1.535),(yy+.014,1.535)],.019,red,side,lift=.002)
 for yy in [1.145,-3.43]:
  for a in [.11,.38,.67,.94]:
   p=skin(yy,a if side==1 else pi-a);flush_bolt(side,p[1],p[2],.0028)

# Custom geometric wordmark, traced as outlined paths rather than a substitute font.
# The lower-case i and e, broad squared O's and doubled strokes are intentional.
logo_paths=[]
def add_logo_path(points,closed=False,width=.020):logo_paths.append((points,closed,width))
def rect_logo(x,y,w,h,r):add_logo_path(rounded_rect(x,y,w,h,r,18),True,.023)
for off in [0,2.24]:
 rect_logo(off,0,.98,1,.17);rect_logo(off+.075,.075,.83,.85,.105)
# R: full outside silhouette, internal upper counter, and the diagonal split leg.
add_logo_path([(1.075,0),(1.075,1),(1.76,1),(1.90,.96),(1.97,.85),(1.97,.66),(1.93,.56),(1.80,.51),(2.02,0),(1.916,0),(1.706,.49),(1.17,.49),(1.17,0)],True,.023)
rect_logo(1.17,.58,.705,.325,.072)
add_logo_path([(1.10,.035),(1.10,.97)],False,.013)
# Small i, with a separate outlined square dot.
rect_logo(2.075,0,.085,.69,.008);rect_logo(2.067,.80,.103,.20,.018)
# N consists of narrow outlined uprights and an outlined diagonal band.
add_logo_path([(3.32,0),(3.32,1),(3.415,1),(4.105,.145),(4.105,1),(4.185,1),(4.185,0),(4.087,0),(3.4,.855),(3.4,0)],True,.022)
add_logo_path([(3.367,.955),(4.135,.035)],False,.014)
# Hyphen is narrow, sitting slightly below mid-height.
rect_logo(4.28,.43,.30,.055,.009)
# e, a rounded open lower loop with an outlined rectangular upper counter.
add_logo_path([(5.56,.145),(5.52,.04),(5.40,0),(4.87,0),(4.73,.04),(4.66,.16),(4.66,.83),(4.71,.95),(4.85,1),(5.39,1),(5.52,.96),(5.58,.84),(5.58,.59),(5.53,.51),(5.42,.48),(4.75,.48),(4.75,.195),(4.79,.11),(4.9,.08),(5.35,.08),(5.43,.10),(5.46,.145)],False,.023)
rect_logo(4.75,.57,.735,.34,.065)
add_logo_path([(4.695,.17),(4.745,.08),(4.875,.04),(5.38,.04),(5.475,.075),(5.505,.145)],False,.018)

# Preserve a clean scalable vector master alongside the Blender asset.
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.2 -0.12 6.05 1.25"><g transform="translate(0 1) scale(1 -1)" fill="none" stroke="#f0f2ef" stroke-linejoin="round" stroke-linecap="round">']
for pts,closed,width in logo_paths:
 d='M '+' L '.join(f'{x:.5f} {z:.5f}' for x,z in pts)+(' Z' if closed else '')
 svg.append(f'<path d="{d}" stroke-width="{width}"/>')
svg.append('</g></svg>');(OUT/'ORION-e_vector_wordmark.svg').write_text('\n'.join(svg),encoding='utf-8')
for side in [-1,1]:
 for i,(pts,closed,width) in enumerate(logo_paths):
  # A subtle backwards slant reproduces the lettering visible in the photograph.
  coords=[]
  for u,v in pts:
   along=(u-.15*v)*.205
   yy=1.045-along if side==-1 else -.10+along
   coords.append((yy,1.63+v*.205))
  o=ribbon_on_skin(f'ORiON-e custom outline | {side} | {i:02d}',coords,width*.205,ink,side,closed,.0016)
  o['reference']='Hand-traced geometric double-outline lettering from user photograph'

def marking_disc(name,side,y,z,r,material):
 coords=[surface_point(side,y,z,.0018)]+[surface_point(side,y+r*cos(i*2*pi/48),z+r*sin(i*2*pi/48),.0018) for i in range(48)]
 return mesh(name,coords,[(0,i+1,(i+1)%48+1) for i in range(48)],MARK,material)
def nose_accent_geometry(side):
 outline=[(3.55,1.245),(3.52,1.46),(3.43,1.465),(3.30,1.385),(3.12,1.30),(2.94,1.252),(2.65,1.242)]
 pp=path_resample(outline,.008,True);cy=sum(p[0] for p in pp)/len(pp);cz=sum(p[1] for p in pp)/len(pp)
 # Dense concentric rings keep the filled marking on the curved lower skin.
 n=len(pp);verts=[surface_point(side,cy,cz,.003)];faces=[]
 for ring in range(1,49):
  t=ring/48
  verts.extend(surface_point(side,cy+(y-cy)*t,cz+(z-cz)*t,.003) for y,z in pp)
  start=1+(ring-1)*n
  for j in range(n):
   a=start+j;b=start+(j+1)%n
   faces.append((0,a,b) if ring==1 else (a-n,a,b,b-n))
 return verts,faces

for side in [-1,1]:
 verts,faces=nose_accent_geometry(side)
 mesh('Curved graphite nose underside accent',verts,faces,MARK,paint)
for side in [-1,1]:
 for yy,zz in [(3.52,1.42),(3.37,1.29),(-1.35,1.365),(-.21,1.77)]:
  marking_disc('Yellow service and caution decal',side,yy,zz,.024,ochre)
  ribbon_on_skin('Service symbol line',[(yy-.010,zz),(yy+.010,zz)],.004,sealmat,side,lift=.0025)
  ribbon_on_skin('Service symbol stem',[(yy,zz-.012),(yy,zz+.012)],.003,sealmat,side,lift=.0025)
 # Forward underside servicing line with short dashed sections.
 for j in range(10):
  yy=1.12+j*.042;ribbon_on_skin('Ochre underside servicing boundary',[(yy,1.253),(yy+.032,1.253)],.005,ochre,side)
 # Small outlined equipment E inside the secondary access door.
 for pts in [[(-.81,1.555),(-.81,1.602),(-.842,1.602)],[(-.81,1.579),(-.837,1.579)],[(-.81,1.555),(-.842,1.555)]]:
  ribbon_on_skin('Equipment E stencil',pts,.003,ink,side)
 # Reference's datum, grounding and lifting marks rather than generic pluses.
 ribbon_on_skin('Grounding stem',[(.86,1.325),(.86,1.375)],.004,ink,side)
 for z,w in [(1.335,.06),(1.325,.04),(1.315,.02)]:ribbon_on_skin('Grounding bars',[(.86-w/2,z),(.86+w/2,z)],.0035,ink,side)
 ring=[(.76+.022*cos(j*2*pi/48),1.344+.025*sin(j*2*pi/48)) for j in range(48)]
 ribbon_on_skin('Circular datum',ring,.0035,ink,side,True)
 ribbon_on_skin('Lifting reference',[(.68,1.315),(.68,1.376)],.0035,ochre,side)
 ribbon_on_skin('Lifting arrow',[(.665,1.355),(.68,1.375),(.695,1.355)],.0035,ochre,side)

# Main landing gear in the reference uses long, flat spring legs rather than
# an exposed tubular oleo and torque-link assembly at each main wheel.
for side,label in [(-1,'PORT'),(1,'STARBOARD')]:
 for o in list(GEAR.objects):
  if o.get('assembly')==label and o.name.startswith((label+' swept upper strut',label+' polished oleo','Oleo lower sleeve','Rear drag brace','Torque link','Clevis pivot','Strut retaining','Flexible brake')):
   bpy.data.objects.remove(o,do_unlink=True)
 top=Vector((side*.29,-1.88,1.43));bottom=Vector((side*1.29,-1.28,.27));axis=bottom-top
 o=box(label+' flat swept composite main leg',(top+bottom)/2,(.075,.135,axis.length),GEAR,paint,.013);o.rotation_euler=axis.to_track_quat('Z','Y').to_euler();o['assembly']=label
 rod(label+' axle pivot',(side*1.06,-1.28,.25),(side*1.31,-1.28,.25),.037,GEAR,alloy)
 # Narrow inboard drag stay and hydraulic route follow the flat leg.
 rod(label+' slender gear stay',(side*.27,-2.1,1.24),(side*.79,-1.56,.78),.014,GEAR,paint)
 line(label+' brake line',[top+Vector((0,.075,0)),(top+bottom)/2+Vector((0,.075,0)),bottom+Vector((0,.075,0))],.004,dark,GEAR)
 for frac in [.13,.47,.83]:
  p=top.lerp(bottom,frac);rod('Main leg attachment bolt',p+Vector((0,-.080,0)),p+Vector((0,.080,0)),.009,GEAR,alloy,6)

# Restrained belly fairing and the aft teardrop aerial visible below the wing.
ball('Forward flush ventral fairing',(0,2.12,1.23),(.25,.44,.095),AIR,paint)
rod('Rear antenna support',(0,-2.32,1.25),(0,-2.32,.92),.095,DETAIL,paint,48)
ball('Rear ventral teardrop',(0,-2.32,.85),(.155,.225,.14),AIR,white)
torus('Rear antenna equatorial seal',(0,-2.32,.865),.156,.003,DETAIL,paint)

# High-resolution photograph shows flat dorsals, a hatch, and an orange cap.
ball('Low dorsal circular cover',(0,.03,1.989),(.16,.23,.014),AIR,paint)
line('Dorsal cover perimeter',[(.145*cos(a*2*pi/96),.03+.205*sin(a*2*pi/96),1.997) for a in range(96)],.0007,sealmat,DETAIL,True)
ball('Aft dorsal beacon fairing',(0,-3.28,1.95),(.115,.22,.055),TAIL,paint)
ball('Amber beacon lens',(0,-3.12,1.976),(.095,.08,.044),TAIL,amber)
for side in [-1,1]:
 for j in range(14):
  yy=-3.54+j*.030;pp=surface_point(side,yy,1.65,.001)
  line('Fine aft cooling slot',[Vector(pp)+Vector((0,0,-.035)),Vector(pp)+Vector((0,0,.035))],.0025,dark)
 # Small NACA-style intake, a shallow triangular recess.
 coords=[surface_point(side,-3.14,1.49,.002),surface_point(side,-3.31,1.43,.002),surface_point(side,-3.31,1.54,.002)]
 mesh('Engine flush inlet',coords,[(0,1,2)],DETAIL,dark)
 # Subtle tail hinge screws rather than oversized hinge bubbles.
 for j in range(5):
  t=.1+j*.19;x=side*(.22+1.5*t);z=1.78+1.63*t;yy=-2.89-.5*t-(.85-.34*t)*.74
  ball('Tail hinge pin',(x,yy,z),(.006,.014,.012),DETAIL,paint)

# Add the latest high-resolution source as a packed, hidden viewport reference.
path=Path('C:/Users/david/AppData/Local/Temp/codex-clipboard-f478ca94-778a-4f60-a687-0ae98c72a97d.png')
if path.exists():
 im=bpy.data.images.load(str(path));im.pack();o=bpy.data.objects.new('Revision 04 high resolution master reference',None);REF.objects.link(o);o.empty_display_type='IMAGE';o.data=im;o.hide_render=True;o.hide_viewport=True
scene['Wordmark']='Custom outlined ORiON-e geometry; master SVG included'
scene['Configuration note']='Forward optical turret retained at user request; differs from reference exhibition underbody layout.'

# Additional close-up detail in the nose undercarriage, based on the photograph.
gearwhite=mat('Wheel rim pale aluminium',(.53,.57,.57),.41,.38)
for side in [-1,1]:
 x=side*.073;y=NOSE_GEAR_Y;z=.215
 rod('Nose pale wheel dish',(x,y,z),(x+side*.005,y,z),.104,GEAR,gearwhite,64)
 torus('Nose wheel dish bead',(x+side*.006,y,z),.099,.004,GEAR,alloy,(1,0,0))
 for j in range(5):
  a=j*2*pi/5;yy=y+.067*cos(a);zz=z+.067*sin(a)
  rod('Nose rim ventilation recess',(x+side*.005,yy,zz),(x+side*.007,yy,zz),.017,GEAR,dark,32)
  torus('Nose rim recess chamfer',(x+side*.008,yy,zz),.017,.0016,GEAR,alloy,(1,0,0))
 # Flattened fork casting with rounded front contour.
 coords=[(y-.075,z+.29),(y+.045,z+.27),(y+.077,z+.18),(y+.035,z+.06),(y+.018,z-.018),(y-.045,z-.03),(y-.07,z+.015),(y-.065,z+.14)]
 verts=[(side*.112+ss*.012,yy,zz) for ss in [-1,1] for yy,zz in coords];n=len(coords)
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh('Cast nose wheel fork',verts,faces,GEAR,alloy);bevel(o,.007,3);o['assembly']='NOSE'
rod('Nose suspension damper',(0.075,NOSE_GEAR_Y-.075,.63),(.075,NOSE_GEAR_Y-.075,.78),.025,GEAR,ochre,40)
rod('Damper polished pin',(0.075,NOSE_GEAR_Y-.075,.78),(.075,NOSE_GEAR_Y-.075,.88),.012,GEAR,chrome)
for p in [(0.075,NOSE_GEAR_Y-.075,.64),(.075,NOSE_GEAR_Y-.075,.86)]:
 rod('Damper mounting lug',Vector(p)-Vector((.024,0,0)),Vector(p)+Vector((.024,0,0)),.017,GEAR,alloy,20)
# Safety pin and a small cloth streamer, independently editable.
rod('Nose gear safety pin',(-.07,NOSE_GEAR_Y-.18,.90),(.09,NOSE_GEAR_Y-.18,.90),.006,GEAR,alloy,16)
mesh('Gear safety streamer',[(.07,NOSE_GEAR_Y-.20,.91),(.07,NOSE_GEAR_Y-.23,.94),(.07,NOSE_GEAR_Y-.52,.90),(.07,NOSE_GEAR_Y-.55,.875)],[(0,1,2,3)],GEAR,red)

# Fasteners along only the actual joints and removable covers, not the entire skin.
for side in [-1,1]:
 for yy in [-3.40,-2.70]:
  for z in [1.38,1.53,1.70,1.84]:flush_bolt(side,yy,z,.0027)
 for span in [1.05,3.4,5.7,7.65]:
  for u in [.73,.77]:
   front,chord,z,h,cam=foil(side,span,u);p=(side*span,front-chord*u,z+h+cam+.001)
   rod('Flush wing hinge attachment',p,Vector(p)+Vector((0,0,.0008)),.0027,WINGS,flushmat,12)
