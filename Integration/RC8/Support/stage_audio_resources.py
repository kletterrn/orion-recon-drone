from pathlib import Path
import hashlib,json,shutil
W=Path(__file__).resolve().parents[3];I=W/'Integration/RC8';A=I/'Audio';out=W/'Sounds/ORD/RC8';out.mkdir(parents=True,exist_ok=True);(out/'Signals').mkdir(exist_ok=True)
mapping={
 'ORD_Startup':'01_startup_ILLUSTRATION.wav','ORD_Idle':'02_idle_loop_ILLUSTRATION.wav','ORD_Takeoff':'03_takeoff_power_ILLUSTRATION.wav','ORD_Cruise':'04_cruise_loop_ILLUSTRATION.wav','ORD_Shutdown':'06_shutdown_ILLUSTRATION.wav',
 'BDL_Spoolup':'01_turbine_spoolup_mono_SYNTHETIC.wav','BDL_Flight':'02_flight_engine_LOOP_mono_SYNTHETIC.wav','BDL_FlightBright':'03_flight_engine_high_LOOP_mono_SYNTHETIC.wav','BDL_ImpactClose':'07_impact_close_mono_SYNTHETIC.wav','BDL_ImpactDistant':'08_impact_distant_mono_SYNTHETIC.wav','BDL_Debris':'09_debris_tail_mono_SYNTHETIC.wav',
 'ORD_GearMotor':'ORD_GearMotor_SYNTHETIC.wav','ORD_DoorLatch':'ORD_DoorLatch_SYNTHETIC.wav','BDL_WingDeployment':'BDL_WingDeployment_SYNTHETIC.wav'}
rows=[]
for name,filename in mapping.items():
 matches=list((A/'SourceFiles').rglob(filename))+list((A/'Authored').glob(filename));assert len(matches)==1
 source=matches[0];dest=out/(name+'.wav');guid=hashlib.sha256(('ORD_RC8_'+name).encode()).hexdigest()[:16].upper();res=f'{{{guid}}}Sounds/ORD/RC8/{name}.wav'
 if dest.exists() and dest.read_bytes()!=source.read_bytes():raise RuntimeError(f'Refusing overwrite {dest}')
 shutil.copy2(source,dest)
 meta='MetaFileClass {\n Name "'+res+'"\n Configurations {\n  WAVResourceClass PC {\n  }\n'+''.join('  WAVResourceClass '+p+' : PC {\n  }\n' for p in ['HEADLESS','XBOX_ONE','XBOX_SERIES','PS4','PS5'])+' }\n}\n'
 dest.with_suffix('.wav.meta').write_text(meta)
 rows.append({'name':name,'resource':res,'source':str(source.relative_to(A)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
signals=['ORD_IdleWorldDb','ORD_CruiseWorldDb','ORD_IdleFeedDb','ORD_CruiseFeedDb','ORD_WorldGateDb','BDL_FlightDb','BDL_ImpactCloseDb','BDL_ImpactDistantDb','BDL_DebrisDb']
for name in signals:
 text='''AudioSignalResClass {
 Inputs {
  IOPItemInputClass {
   id 303
   name "%s"
   tl 0 0
   children { 160 }
   value -96
  }
 }
 Outputs {
  IOPItemOutputClass {
   id 160
   name "%s"
   tl 256 0
   input 303
  }
 }
 compiled IOPCompiledClass {
  visited { 5 6 }
  ins { IOPCompiledIn { data { 1 2 } } }
  outs { IOPCompiledOut { data { 0 } } }
  processed 2
  version 2
 }
}
'''%(name,name)
 (out/'Signals'/(name+'.sig')).write_text(text)
(I/'Reports/audio_resource_manifest.json').write_text(json.dumps({'status':'staged; not wired to runtime','samples':rows,'signals':signals},indent=2))
print('RC8_AUDIO_RESOURCES_STAGED',len(rows),flush=True)
