"""Stage user-supplied synthetic sources and author original presentation cues."""
from pathlib import Path
import zipfile,hashlib,json,wave,struct,math,random,shutil
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';A=I/'Audio'
for n in ['SourceArchives','SourceFiles','Authored']: (A/n).mkdir(parents=True,exist_ok=True)
manifest={'status':'source preparation only; engine playback and listening tests not performed','synthetic':True,'archives':[],'wav_analysis':[],'authored':[]}
for name in ['S8000_Banderol_SYNTHETIC_sound_pack.zip','Orion_SYNTHETIC_audio_illustration.zip']:
 source=Path('C:/Users/david/Downloads')/name;copy=A/'SourceArchives'/name
 if not copy.exists():shutil.copy2(source,copy)
 manifest['archives'].append({'file':name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
 with zipfile.ZipFile(source) as z:
  for item in z.infolist():
   dest=(A/'SourceFiles'/item.filename).resolve()
   if not dest.is_relative_to((A/'SourceFiles').resolve()):raise RuntimeError('Unsafe archive path')
   if item.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
   dest.parent.mkdir(parents=True,exist_ok=True)
   if not dest.exists():dest.write_bytes(z.read(item))
for p in (A/'SourceFiles').rglob('*.wav'):
 with wave.open(str(p),'rb') as f:
  channels=f.getnchannels();rate=f.getframerate();width=f.getsampwidth();count=f.getnframes();data=f.readframes(count)
  if width!=2:raise RuntimeError(f'Unsupported source PCM: {p}')
  samples=struct.unpack('<'+'h'*(len(data)//2),data);peak=max(abs(v) for v in samples)/32768;rms=math.sqrt(sum((v/32768)**2 for v in samples)/len(samples))
  manifest['wav_analysis'].append({'file':str(p.relative_to(A)),'channels':channels,'sample_rate':rate,'bits':width*8,'seconds':count/rate,'peak_dbfs':20*math.log10(max(1e-12,peak)),'rms_dbfs':20*math.log10(max(1e-12,rms)),'samples_at_full_scale':sum(abs(v)>=32767 for v in samples),'runtime_candidate':channels==1 and not any(x in p.name.lower() for x in ['preview','incoming','flyby'])})
def write(name,duration,kind):
 rate=48000;rng=random.Random(8051);values=[];filtered=0
 for i in range(round(duration*rate)):
  t=i/rate;u=t/duration;noise=rng.uniform(-1,1);filtered=.87*filtered+.13*noise
  if kind=='motor':
   envelope=min(1,t/.04,(duration-t)/.07);v=envelope*(.10*math.sin(2*math.pi*180*t)+.035*math.sin(2*math.pi*540*t)+.055*filtered)
  elif kind=='latch':v=math.exp(-t*55)*(.16*filtered+.11*math.sin(2*math.pi*950*t))*(min(1,t/.002))
  else:v=math.sin(math.pi*u)**2*(.11*filtered+.025*math.sin(2*math.pi*(420*t-170*t*t)))
  values.append(round(max(-.95,min(.95,v))*32767))
 p=A/'Authored'/name
 with wave.open(str(p),'wb') as f:f.setparams((1,2,rate,0,'NONE','not compressed'));f.writeframes(struct.pack('<'+'h'*len(values),*values))
 manifest['authored'].append({'file':str(p.relative_to(A)),'seconds':duration,'description':'Original synthetic game presentation cue; not an authentic recording','peak_dbfs':20*math.log10(max(abs(v) for v in values)/32768)})
write('ORD_GearMotor_SYNTHETIC.wav',1.0,'motor');write('ORD_DoorLatch_SYNTHETIC.wav',.15,'latch');write('BDL_WingDeployment_SYNTHETIC.wav',.38,'deploy')
(A/'AUDIO_PROVENANCE.md').write_text('# RC8 synthetic audio sources\n\nThe two source archives were supplied by the user and are preserved byte-for-byte. Their bundled scripts are retained as source material, not executed. No supplied sound is represented as an authentic aircraft or missile recording. Stereo flybys, montages and combined incoming/impact demonstrations are preview material and excluded from live emitter candidates.\n\nGear motor, door latch and wing deployment cues are original procedural game sounds authored for this integration. Numerical PCM checks are not listening tests. ACP routing, spatial attenuation, operator-feed mixing and in-engine validation remain pending.\n')
(I/'Reports/audio_source_inventory.json').write_text(json.dumps(manifest,indent=2));print('RC8_AUDIO_SOURCES_PREPARED',len(manifest['wav_analysis']),flush=True)
