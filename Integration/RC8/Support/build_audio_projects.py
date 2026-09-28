"""Author native ACP graphs using documented Enfusion node connections."""
from pathlib import Path
import hashlib,json,re
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';O=W/'Sounds/ORD/RC8'
manifest=json.loads((I/'Reports/audio_resource_manifest.json').read_text());samples={v['name']:v['resource'] for v in manifest['samples']};signals={}
platforms=['XBOX_ONE','XBOX_SERIES','PS4','PS5','HEADLESS']
def meta(path,kind):
 p=path.with_suffix(path.suffix+'.meta')
 if not p.exists():
  guid=hashlib.sha256(('ORD_RC8_'+str(path.relative_to(W))).encode()).hexdigest()[:16].upper();res='{'+guid+'}'+path.relative_to(W).as_posix()
  p.write_text('MetaFileClass {\n Name "'+res+'"\n Configurations {\n  '+kind+' PC {\n  }\n'+''.join('  '+kind+' '+x+' : PC {\n  }\n' for x in platforms)+' }\n}\n')
 return re.search(r'Name\s+"([^"]+)"',p.read_text()).group(1)
for name in manifest['signals']:signals[name]=meta(O/'Signals'/(name+'.sig'),'AudioSignalResourceClass')
inputs=['WPN_Handling','WPN_Shots','WPN_Explosions','WNP_BulletHits','CHAR','ENV_AMB_2D','VEH_Animations','Impacts','Dialog','Music','ENV_Doors','VEH_Engine','VEH_Tires','VON','SFX','SFX_Reverb','VON_Reverb','Dialog_Reverb','Impacts_EXT','ENV_AMB_3D','WPN_SonicCracks','CHAR_Gear','PA','SFX_Reverb_Exterior','UI','ENV_AMB_3D_Reverb_Exterior','SFX_Direct','SFX_Reverb_Small','SFX_Reverb_Medium','SFX_Reverb_Large','WPN_Shots_Player','Dialog_Reverb_Small','Dialog_Reverb_Medium','Dialog_Reverb_Large','WPN_TravelingProjectile','Dialog_Delay_Exterior']
def conn(port,node,out=65):return f'ConnectionsClass {{ id {port} links {{ ConnectionClass {{ id {node} port {out} }} }} }}'
def project(name,events):
 nodes={'signals':[],'sounds':[],'shaders':[],'amplitudes':[],'banks_local':[]};mix={};rows=[]
 for index,(event,sample,loop,gain,base,spatial,range_m,bus) in enumerate(events):
  sid=100+index*10;bank=sid+1;shader=sid+2;amp=sid+3;signal=sid+4
  if gain:
   nodes['signals'].append(f'SignalClass {{ id {signal} name "{gain}" tl -768 {index*192} res "{signals[gain]}" inputsport {{ 303 }} outputsport {{ 160 }} inputvalues {{ -96 }} inputvaluesmin {{ -96 }} inputvaluesmax {{ 6 }} }}')
  bank_ins=' ins { '+conn(0,signal,160)+' } pi { 1 0 } pu { 1 0 }' if gain else ''
  looping=' "Loop count" 255 "Infinite loop" 1' if loop else ''
  nodes['banks_local'].append(f'BankLocalClass {{ id {bank} name "{event}_Sample" version 7 tl -512 {index*192}{bank_ins} Volume {base}{looping} "Termination Fade Out" 250 "Fade in time" {200 if loop else 10} Samples {{ AudioBankSampleClass {{ Filename "{samples[sample]}" Probability 100 Index 0 }} }} }}')
  source=bank
  if spatial:
   nodes['amplitudes'].append(f'AmplitudeClass {{ id {amp} name "{event}_Distance" version 5 curve Linear outerRange {range_m} tl -512 {index*192+80} }}')
   nodes['shaders'].append(f'ShaderClass {{ id {shader} name "{event}_Spatial" version 5 tl -256 {index*192} ins {{ {conn(1,amp)} {conn(64,bank)} }} pi {{ 2 0 }} }}');source=shader
  nodes['sounds'].append(f'SoundClass {{ id {sid} name "{event}" version 5 tl 0 {index*192} ins {{ {conn(64,source)} }} outState 9000 outStatePort {bus} }}')
  mix.setdefault(bus,[]).append(sid);rows.append({'event':event,'sample':sample,'loop':loop,'gain_signal':gain,'base_db':base,'spatial':spatial,'outer_range_m':range_m,'mix_port':bus})
 connections=' '.join('ConnectionsClass { id '+str(port)+' links { '+' '.join(f'ConnectionClass {{ id {sid} port 65 }}' for sid in ids)+' } }' for port,ids in mix.items())
 bits=sum(1<<({'70663':11,'17415':6,'342023':34,'8199':2}[str(port)]) for port in mix)
 mixer=f'MixerClass {{ id 9000 name "ORD_RC8_Output" version 4 tl 256 0 res "{{B764D803219C775E}}Sounds/FinalMix.afm" path "{{B764D803219C775E}}Sounds/FinalMix.afm" ins {{ {connections} }} pi {{ {bits & 0xffffffff} {bits >> 32} }} inputs {{ '+ ' '.join('"'+v+'"' for v in inputs)+' } }'
 text='AudioClass {\n'+''.join(' '+key+' {\n  '+'\n  '.join(value)+'\n }\n' for key,value in nodes.items() if value)+' mixers {\n  '+mixer+'\n }\n version 1\n}\n'
 path=O/(name+'.acp');path.write_text(text);return rows
orion=[]
for layer,spatial in [('WORLD',True),('FEED',False)]:
 for part,gain in [('Idle','Idle'),('Cruise','Cruise')]:orion.append((f'ORD_{part}_{layer}','ORD_'+part,True,f'ORD_{gain}{"World" if spatial else "Feed"}Db',-96,spatial,1500,70663))
 for part,db in [('Startup',-6),('Shutdown',-7),('Takeoff',-15)]:orion.append((f'ORD_{part}_{layer}','ORD_'+part,False,None,db-(0 if spatial else 18),spatial,1500,70663))
orion += [('ORD_GearMotor','ORD_GearMotor',True,None,-16,True,80,17415),('ORD_DoorLatch','ORD_DoorLatch',False,None,-13,True,60,17415)]
bdl=[('BDL_Flight','BDL_Flight',True,'BDL_FlightDb',-96,True,1800,342023),('BDL_FlightBright','BDL_FlightBright',True,'BDL_FlightDb',-96,True,1800,342023),('BDL_Spoolup','BDL_Spoolup',False,None,-9,True,1200,342023),('BDL_WingDeployment','BDL_WingDeployment',False,None,-14,True,100,17415),('BDL_ImpactClose','BDL_ImpactClose',False,'BDL_ImpactCloseDb',-96,True,800,8199),('BDL_ImpactDistant','BDL_ImpactDistant',False,'BDL_ImpactDistantDb',-96,True,3000,8199),('BDL_Debris','BDL_Debris',False,'BDL_DebrisDb',-96,True,400,8199)]
report={'status':'ACP source graphs authored; import, event routing and listening tests pending','gain_note':'Gain signals drive bank volume in dB; runtime supplies base gain and the feed attenuation','Orion':project('ORD_Orion_RC8',orion),'Banderol':project('ORD_Banderol_RC8',bdl),'signals':signals}
(I/'Reports/audio_projects.json').write_text(json.dumps(report,indent=2));print('RC8_ACP_SOURCES_WRITTEN',flush=True)
