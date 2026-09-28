// Native display simulation, not a temperature measurement or pixel classifier.
class ORD_ThermalController
{
 protected ref Material m_Material;
 protected World m_World;
 protected int m_Camera = -1, m_Channel = -1;
 protected float m_NextEnvironment;
 protected static bool s_Initialized;
 bool Fallback;
 void Clear()
 {
  if(m_World && m_Camera>=0)
  {
   m_World.SetCameraPostProcessEffect(m_Camera,11,PostProcessEffectType.ThermalImaging,string.Empty);
   m_World.SetCameraPostProcessEffect(m_Camera,5,PostProcessEffectType.Colors,string.Empty);
  }
  m_Material=null; m_World=null; m_Camera=-1; m_Channel=-1;
 }
 int Update(World world,int camera,int channel,ResourceName white,ResourceName black,float zoom)
 {
  if(world!=m_World || camera!=m_Camera || channel!=m_Channel)
  {
   Clear(); m_World=world; m_Camera=camera; m_Channel=channel; Fallback=false;
   if(channel>0)
   {
    ResourceName resource=white; if(channel==2) resource=black;
    if(resource!=string.Empty) m_Material=Material.GetOrLoadMaterial(resource,0);
    if(!m_Material)
    {
     Fallback=true; Print("ORD thermal resource unavailable: daylight fallback active"); return 0;
    }
    if(!s_Initialized) { TPP_ThermalMaterials.Initialize(); s_Initialized=true; }
    m_Material.SetParam("DegradeFPS",30);
    world.SetCameraPostProcessEffect(camera,5,PostProcessEffectType.Colors,"{661B5884EF0760FE}UI/Materials/ScreenEffects_ColorPP_Thermal.emat");
    world.SetCameraPostProcessEffect(camera,11,PostProcessEffectType.ThermalImaging,resource);
    m_NextEnvironment=0;
   }
  }
  if(!m_Material) return 0;
  float width,height; GetGame().GetWorkspace().GetScreenSize(width,height);
  // Above 20x, the camera crops the same optical information into fewer samples.
  float digital=Math.Max(zoom/20,1);
  m_Material.SetParam("DownsizePercent",Math.Clamp(64000/Math.Max(width*digital,1),1,100));
  float now=world.GetWorldTime()*0.001;
  if(now>=m_NextEnvironment)
  {
   m_NextEnvironment=now+1;
   BaseWeatherManagerEntity weather=BaseWeatherManagerEntity.Cast(WeatherManager.GetRegisteredWeatherManagerEntity(world));
   float day=0.5, degradation;
   if(weather)
   {
    degradation=Math.Clamp(weather.GetRainIntensity()+weather.GetFogAmount()*0.5,0,1);
    float rise,sunset;
    if(weather.GetSunriseHour(rise) && weather.GetSunsetHour(sunset))
    {
     float length=sunset-rise; if(length<=0) length+=24;
     float elapsed=weather.GetTimeOfTheDay()-rise; if(elapsed<0) elapsed+=24;
     day=0; if(elapsed<length) day=Math.Sin(elapsed/length*Math.PI);
    }
   }
   m_Material.SetParam("FogRelStart",0.75-degradation*0.25);
   m_Material.SetParam("FogRelEnd",0.95-degradation*0.1);
   m_Material.SetParam("TemperatureDisplayMin",Math.Lerp(-10,10,day));
   m_Material.SetParam("TemperatureDisplayMax",Math.Lerp(45,65,day));
  }
  return channel;
 }
}

