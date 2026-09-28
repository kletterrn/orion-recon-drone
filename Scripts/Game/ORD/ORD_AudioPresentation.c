// Synthetic presentation audio only; no authority over flight, engine state or damage.
class ORD_AudioPresentationClass : ScriptGameComponentClass {}
class ORD_AudioPresentation : ScriptGameComponent
{
 override event bool OnTicksOnRemoteProxy() { return true; }
 protected ORD_AircraftComponent m_Aircraft;
 protected SoundComponent m_Sound;
 protected bool m_Initialized, m_WasRunning, m_Feed, m_Loops, m_GearMotor;
 protected float m_Level, m_Power, m_FeedMix, m_HighPowerTime, m_TransientCooldown;
 protected ref array<AudioHandle> m_EngineLoops = {};
 protected ref array<AudioHandle> m_WorldTransients = {};
 protected AudioHandle m_GearHandle;
 override void OnPostInit(IEntity owner) { super.OnPostInit(owner); SetEventMask(owner,EntityEvent.INIT | EntityEvent.FRAME); }
 override void EOnInit(IEntity owner)
 {
  if (System.IsConsoleApp()) return;
  m_Aircraft=ORD_AircraftComponent.Cast(owner.FindComponent(ORD_AircraftComponent));
  m_Sound=SoundComponent.Cast(owner.FindComponent(SoundComponent));
 }
 void SetOperatorFeed(bool enabled)
 {
  if (System.IsConsoleApp() || m_Feed==enabled) return;
  m_Feed=enabled;
  if (enabled) { foreach(AudioHandle h:m_WorldTransients) AudioSystem.TerminateSoundFadeOut(h,true,0.15); m_WorldTransients.Clear(); }
 }
 protected float Gain(float amplitude,float baseDb=0)
 {
  if(amplitude<=0.000016) return -96;
  return Math.Clamp(baseDb+20*Math.Log10(amplitude),-96,0);
 }
 protected void Event(string part)
 {
  if(!m_Sound) return;
  if(m_Feed) m_Sound.SoundEvent("ORD_"+part+"_FEED");
  else m_WorldTransients.Insert(m_Sound.SoundEventBone("ORD_"+part+"_WORLD","ORD_EngineAudio"));
 }
 protected void StartLoops()
 {
  if(m_Loops || !m_Sound) return;
  m_EngineLoops.Insert(m_Sound.SoundEventBone("ORD_Idle_WORLD","ORD_EngineAudio"));
  m_EngineLoops.Insert(m_Sound.SoundEventBone("ORD_Cruise_WORLD","ORD_EngineAudio"));
  m_EngineLoops.Insert(m_Sound.SoundEvent("ORD_Idle_FEED"));
  m_EngineLoops.Insert(m_Sound.SoundEvent("ORD_Cruise_FEED"));
  m_Loops=true;
 }
 protected void StopLoops()
 {
  foreach(AudioHandle h:m_EngineLoops) AudioSystem.TerminateSoundFadeOut(h,true,0.2);
  m_EngineLoops.Clear();m_Loops=false;
 }
 void GearMotion(bool moving,bool latch)
 {
  if(System.IsConsoleApp() || !m_Sound) return;
  if(moving && !m_GearMotor) { m_GearHandle=m_Sound.SoundEvent("ORD_GearMotor");m_GearMotor=true; }
  if(!moving && m_GearMotor) { AudioSystem.TerminateSoundFadeOut(m_GearHandle,true,0.12);m_GearMotor=false; }
  if(latch) m_Sound.SoundEvent("ORD_DoorLatch");
 }
 override void EOnFrame(IEntity owner,float timeSlice)
 {
  if(System.IsConsoleApp() || !m_Aircraft || !m_Sound) return;
  bool running=m_Aircraft.EngineOn() && !m_Aircraft.Destroyed();
  if(!m_Initialized) { m_Initialized=true;m_WasRunning=running; }
  else if(running!=m_WasRunning)
  {
   if(running) Event("Startup");
   else if(!m_Aircraft.Destroyed()) Event("Shutdown");
   m_WasRunning=running;
  }
  float target=0;if(running) target=1;
  m_Level=Math.Lerp(m_Level,target,Math.Clamp(timeSlice*3,0,1));
  float feedTarget=0;if(m_Feed) feedTarget=1;
  m_FeedMix=Math.Lerp(m_FeedMix,feedTarget,Math.Clamp(timeSlice*8,0,1));
  m_Power=Math.Lerp(m_Power,Math.Clamp(m_Aircraft.Throttle,0,1),Math.Clamp(timeSlice*2,0,1));
  if(running) StartLoops();
  float idle=Math.Sqrt(1-m_Power)*m_Level;
  float cruise=Math.Sqrt(m_Power)*m_Level;
  m_Sound.SetSignalValueStr("ORD_IdleWorldDb",Gain(idle*(1-m_FeedMix),-9));
  m_Sound.SetSignalValueStr("ORD_CruiseWorldDb",Gain(cruise*(1-m_FeedMix),-7));
  m_Sound.SetSignalValueStr("ORD_IdleFeedDb",Gain(idle*m_FeedMix,-27));
  m_Sound.SetSignalValueStr("ORD_CruiseFeedDb",Gain(cruise*m_FeedMix,-25));
  if(!running && m_Level<0.002) StopLoops();
  m_TransientCooldown=Math.Max(0,m_TransientCooldown-timeSlice);
  if(running && m_Power>0.85) m_HighPowerTime+=timeSlice;else m_HighPowerTime=0;
  if(m_HighPowerTime>2 && m_TransientCooldown<=0) { Event("Takeoff");m_TransientCooldown=60;m_HighPowerTime=-1000; }
  for(int i=m_WorldTransients.Count()-1;i>=0;i--) if(!AudioSystem.IsSoundPlayed(m_WorldTransients[i])) m_WorldTransients.Remove(i);
  if(m_Aircraft.Destroyed()) { GearMotion(false,false);StopLoops();foreach(AudioHandle h:m_WorldTransients) AudioSystem.TerminateSound(h);m_WorldTransients.Clear(); }
 }
 override void OnDelete(IEntity owner)
 {
  if(!System.IsConsoleApp()) { StopLoops();GearMotion(false,false);if(m_Sound)m_Sound.TerminateAll(); }
  super.OnDelete(owner);
 }
}

