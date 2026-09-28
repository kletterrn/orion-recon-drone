// Illustrative exterior deployment and synthetic sound; no projectile authority.
class ORD_BanderolPresentationClass : ScriptGameComponentClass {}
class ORD_BanderolPresentation : ScriptGameComponent
{
 override event bool OnTicksOnRemoteProxy() { return true; }
 [Attribute("0")] protected bool m_BrightLoop;
 protected ORD_GuidedMissile m_Projectile;
 protected SoundComponent m_Sound;
 protected ref ORD_RC8Rig m_Rig;
 protected bool m_Initialized,m_DeployCue,m_Looping;
 protected int m_LastState;
 protected AudioHandle m_Loop;
 protected float m_Age;
 protected const ResourceName SOUND="{97BA0B2CA879CD12}Sounds/ORD/RC8/ORD_Banderol_RC8.acp";
 override void OnPostInit(IEntity owner) { super.OnPostInit(owner);SetEventMask(owner,EntityEvent.INIT | EntityEvent.FRAME); }
 override void EOnInit(IEntity owner)
 {
  if(System.IsConsoleApp())return;
  m_Rig=new ORD_RC8Rig(owner);m_Projectile=ORD_GuidedMissile.Cast(owner.FindComponent(ORD_GuidedMissile));m_Sound=SoundComponent.Cast(owner.FindComponent(SoundComponent));
 }
 override void EOnFrame(IEntity owner,float timeSlice)
 {
  if(System.IsConsoleApp() || !m_Rig)return;
  int state=0;float start=-1;
  if(m_Projectile) { state=m_Projectile.PresentationState();start=m_Projectile.DeploymentStart(); }
  bool first=!m_Initialized;
  if(first) { m_Initialized=true;if(m_Projectile)m_Age=m_Projectile.FlightAge(); }
  else if(m_Projectile) m_Age=Math.Max(m_Age+timeSlice,m_Projectile.FlightAge());
  float phase=0;if(start>=0)phase=Math.Clamp(m_Age-start,0,1);
  vector p[4];m_Rig.Sample("BDL_Wing_L",phase,p);m_Rig.Apply("BDL_Wing_L",p);m_Rig.Sample("BDL_Wing_R",phase,p);m_Rig.Apply("BDL_Wing_R",p);
  if(m_Sound && state==1)
  {
   if(!m_Looping) { m_Sound.SetSignalValueStr("BDL_FlightDb",-9);string loopEvent="BDL_Flight";if(m_BrightLoop)loopEvent="BDL_FlightBright";m_Loop=m_Sound.SoundEvent(loopEvent);m_Looping=true; }
   if(!first && m_LastState==0)m_Sound.SoundEvent("BDL_Spoolup");
   if(start>=0 && !m_DeployCue) { if(!first && phase<0.2)m_Sound.SoundEvent("BDL_WingDeployment");m_DeployCue=true; }
  }
  if(state!=1 && m_Looping) { AudioSystem.TerminateSoundFadeOut(m_Loop,true,0.12);m_Looping=false; }
  if(!first && state==2 && m_LastState==1)Impact(owner);
  m_LastState=state;
 }
 protected void Impact(IEntity owner)
 {
  vector transform[4];owner.GetTransform(transform);
  // Independent world events retain their tail after the projectile entity is deleted.
  array<string> names={"BDL_ImpactCloseDb","BDL_ImpactDistantDb","BDL_DebrisDb"};array<float> values={-3,-10,-16};
  AudioSystem.PlayEvent(SOUND,"BDL_ImpactClose",transform,names,values);
  AudioSystem.PlayEvent(SOUND,"BDL_ImpactDistant",transform,names,values);
  AudioSystem.PlayEvent(SOUND,"BDL_Debris",transform,names,values);
 }
 override void OnDelete(IEntity owner)
 {
  if(!System.IsConsoleApp()) { if(m_Looping)AudioSystem.TerminateSound(m_Loop);if(m_Sound)m_Sound.TerminateAll(); }
  super.OnDelete(owner);
 }
}


