// RC8 presentation only. Existing flight controls and physics remain authoritative.
class ORD_AircraftVisualsClass : ScriptGameComponentClass {}
class ORD_AircraftVisuals : ScriptGameComponent
{
 override event bool OnTicksOnRemoteProxy() { return true; }
 [RplProp()] protected float m_fPitch;
 [RplProp()] protected float m_fRoll;
 [RplProp()] protected float m_fYaw;
 [RplProp()] protected float m_fPower;
 [RplProp()] protected float m_fGearRep;
 [RplProp()] protected bool m_bGearUp;
 protected ORD_AircraftComponent m_Aircraft;
 protected ORD_AudioPresentation m_Audio;
 protected ref ORD_RC8Rig m_Rig;
 protected float m_fClock, m_fPropeller, m_fWheelNose, m_fWheelMain, m_fGear, m_fSmoothPower;
 protected bool m_bInitialized, m_bMoving;
 protected float m_SensorStamp=-1, m_SensorAge, m_SensorInterval=0.1;
 protected vector m_PreviousSensor, m_CurrentSensor;
 override void OnPostInit(IEntity owner) { super.OnPostInit(owner);SetEventMask(owner,EntityEvent.INIT | EntityEvent.FRAME); }
 override void EOnInit(IEntity owner)
 {
  m_Aircraft=ORD_AircraftComponent.Cast(owner.FindComponent(ORD_AircraftComponent));
  if(System.IsConsoleApp())return;
  m_Rig=new ORD_RC8Rig(owner);m_Audio=ORD_AudioPresentation.Cast(owner.FindComponent(ORD_AudioPresentation));
 }
 override void EOnFrame(IEntity owner,float timeSlice)
 {
  if(!m_Aircraft)return;
  if(Replication.IsServer())
  {
   float ground=owner.GetWorld().GetSurfaceY(owner.GetOrigin()[0],owner.GetOrigin()[2]);
   m_bGearUp=owner.GetOrigin()[1]-ground>60 && m_Aircraft.Speed()>35;
   float target=0;if(m_bGearUp)target=1;
   m_fGearRep=Math.Clamp(m_fGearRep+Math.Clamp(target-m_fGearRep,-timeSlice/3,timeSlice/3),0,1);
   m_fClock+=timeSlice;
   if(m_fClock>=0.1)
   {
    m_fClock=0;m_fPitch=m_Aircraft.Pitch;m_fRoll=m_Aircraft.Roll;m_fYaw=m_Aircraft.Yaw;
    m_fPower=0;if(m_Aircraft.EngineOn() && !m_Aircraft.Destroyed())m_fPower=0.22+0.78*m_Aircraft.Throttle;
    Replication.BumpMe();
   }
  }
  if(System.IsConsoleApp() || !m_Rig)return;
  bool first=!m_bInitialized;
  if(first) { m_fGear=m_fGearRep;m_bInitialized=true; }
  else if(Replication.IsServer())m_fGear=m_fGearRep;
  else m_fGear=Math.Lerp(m_fGear,m_fGearRep,Math.Clamp(timeSlice*18,0,1));
  if(Math.AbsFloat(m_fGear-m_fGearRep)<0.0001)m_fGear=m_fGearRep;
  for(int i=0;i<ORD_RC8Rig.Curves.Count();i++)
  {
   string name=ORD_RC8Rig.Curves.GetKey(i);if(name.StartsWith("BDL_"))continue;
   vector pose[4];m_Rig.Sample(name,m_fGear,pose);m_Rig.Apply(name,pose);
  }
  m_fSmoothPower=Math.Lerp(m_fSmoothPower,m_fPower,Math.Clamp(timeSlice*1.5,0,1));
  m_fPropeller=Math.Mod(m_fPropeller+timeSlice*m_fSmoothPower*7200,360);
  Rotate("ORD_Propeller",m_fPropeller);
  Rotate("ORD_Aileron_L",Math.Clamp(m_fRoll*8,-8,8));Rotate("ORD_Aileron_R",Math.Clamp(m_fRoll*8,-8,8));
  float flap=0;if(m_Aircraft.Speed()<35)flap=8;
  Rotate("ORD_Flap_L",-flap);Rotate("ORD_Flap_R",flap);
  Rotate("ORD_Tail_L",Math.Clamp(-m_fPitch*8+m_fYaw*8,-8,8));
  Rotate("ORD_Tail_R",Math.Clamp(m_fPitch*8+m_fYaw*8,-8,8));
  if(m_Aircraft.Grounded())
  {
   m_fWheelNose=Math.Mod(m_fWheelNose+m_Aircraft.Speed()/0.20*Math.RAD2DEG*timeSlice,360);
   m_fWheelMain=Math.Mod(m_fWheelMain+m_Aircraft.Speed()/0.24*Math.RAD2DEG*timeSlice,360);
  }
  Wheel("front_wheel",m_fWheelNose,true);Wheel("rear_wheel_l",m_fWheelMain,false);Wheel("rear_wheel_r",m_fWheelMain,false);
  vector direction="0 0 1";
  if(m_Aircraft.SensorMode())
  {
   vector worldAim=m_Aircraft.SensorDirection();
   if(!Replication.IsServer())
   {
    float stamp=m_Aircraft.SensorSampleTime();
    if(stamp!=m_SensorStamp)
    {
     m_PreviousSensor=m_CurrentSensor; if(m_SensorStamp<0) m_PreviousSensor=worldAim;
     m_CurrentSensor=worldAim; m_SensorInterval=Math.Clamp(stamp-m_SensorStamp,0.05,0.2);
     m_SensorStamp=stamp; m_SensorAge=0;
    }
    m_SensorAge+=timeSlice;
    worldAim=m_PreviousSensor+(m_CurrentSensor-m_PreviousSensor)*Math.Clamp(m_SensorAge/m_SensorInterval,0,1);
    worldAim.Normalize();
   }
   direction=LocalDirection(worldAim);
  }
  AimLocal(direction);
  bool moving=m_fGear>0.0001 && m_fGear<0.9999;
  if(m_Audio)m_Audio.GearMotion(moving,!first && m_bMoving && !moving);
  m_bMoving=moving;
 }
 protected void Rotate(string name,float angle) { m_Rig.Rotation(name,ORD_RC8PoseData.Axis(name),angle); }
 protected void Wheel(string name,float angle,bool steering)
 {
  vector p[4];if(!m_Rig.Sample(name,m_fGear,p))return;
  ORD_RC8Rig.RotateAround(p,p[3],ORD_RC8PoseData.Axis(name),angle);
  if(steering)ORD_RC8Rig.RotateAround(p,p[3],"0 1 0",m_fYaw*24*(1-m_fGear));
  m_Rig.Apply(name,p);
 }
 protected vector LocalDirection(vector direction)
 {
  vector matrix[4]; GetOwner().GetTransform(matrix);
  return Vector(vector.Dot(direction,matrix[0]),vector.Dot(direction,matrix[1]),vector.Dot(direction,matrix[2]));
 }
 protected void AimLocal(vector direction)
 {
  float yaw=Math.Clamp(Math.Atan2(direction[0],direction[2])*Math.RAD2DEG,-120,120);
  float elevation=Math.Clamp(Math.Atan2(direction[1],Math.Sqrt(direction[0]*direction[0]+direction[2]*direction[2]))*Math.RAD2DEG,-80,35);
  vector y[4],p[4];if(!m_Rig.Rest("ORD_SensorYaw",y) || !m_Rig.Rest("ORD_SensorPitch",p))return;
  ORD_RC8Rig.RotateAround(p,p[3],"-1 0 0",elevation);
  ORD_RC8Rig.RotateAround(p,y[3],"0 1 0",yaw);ORD_RC8Rig.RotateAround(y,y[3],"0 1 0",yaw);
  m_Rig.Apply("ORD_SensorYaw",y);m_Rig.Apply("ORD_SensorPitch",p);
 }
 void SensorAim(float worldYaw,float worldPitch)
 {
  if(!m_Rig)return;
  vector d=Vector(Math.Sin(worldYaw*Math.DEG2RAD)*Math.Cos(worldPitch*Math.DEG2RAD),Math.Sin(worldPitch*Math.DEG2RAD),Math.Cos(worldYaw*Math.DEG2RAD)*Math.Cos(worldPitch*Math.DEG2RAD));
  AimLocal(LocalDirection(d));
 }
}

