// Shared gameplay observation rules. These are not a real-world image classifier.
class ORD_ObservationEvidence
{
 float GenericSeconds, ClassSeconds;
 float LastSample = -1, InvalidSince = -1, LastEligible = -100;
 bool Visible, Acquired, Classified;

 void Sample(float now, bool eligible, bool classEligible, bool person, float quality = 1)
 {
  float dt;
  if (LastSample >= 0) dt = Math.Clamp(now - LastSample, 0, 0.2);
  LastSample = now;
  Visible = eligible;
  if (!eligible)
  {
   if (InvalidSince < 0) InvalidSince = now;
   if (now - InvalidSince > 0.2) { GenericSeconds = 0; ClassSeconds = 0; Acquired = false; Classified = false; }
   return;
  }
  if (InvalidSince >= 0)
  {
   if (now - InvalidSince > 0.2) { GenericSeconds = 0; ClassSeconds = 0; Acquired = false; Classified = false; }
   dt = 0;
  }
  InvalidSince = -1; LastEligible = now;
  GenericSeconds += dt * Math.Clamp(quality, 0.25, 1);
  if (classEligible) ClassSeconds += dt * Math.Clamp(quality, 0.25, 1);
  else { ClassSeconds = 0; Classified = false; }
  Acquired = GenericSeconds >= 2;
  float duration = 4;
  if (person) duration = 6;
  Classified = Acquired && ClassSeconds >= duration;
 }
}

class ORD_LocalObservation
{
 IEntity Entity;
 ref ORD_ObservationEvidence Evidence = new ORD_ObservationEvidence();
 float LastCandidate;
}

class ORD_ObservationPolicy
{
 static float HorizontalFOV(float zoom)
 {
  return 2 * Math.Atan2(Math.Tan(30 * Math.DEG2RAD) / Math.Clamp(zoom, 1, 40), 1) * Math.RAD2DEG;
 }
 static bool Alive(IEntity entity)
 {
  if (!entity || (!ChimeraCharacter.Cast(entity) && !Vehicle.Cast(entity))) return false;
  if (ChimeraCharacter.Cast(entity))
  {
   IEntity parent = entity.GetParent();
   for (int i = 0; i < 8 && parent; i++) { if (Vehicle.Cast(parent)) return false; parent = parent.GetParent(); }
  }
  SCR_CharacterControllerComponent character = SCR_CharacterControllerComponent.Cast(entity.FindComponent(SCR_CharacterControllerComponent));
  if (character && character.IsDead()) return false;
  SCR_DamageManagerComponent damage = SCR_DamageManagerComponent.Cast(entity.FindComponent(SCR_DamageManagerComponent));
  return !damage || !damage.IsDestroyed();
 }
 static vector Point(IEntity entity)
 {
  vector low, high; entity.GetWorldBounds(low, high);
  return (low + high) * 0.5;
 }
 static bool Visible(IEntity aircraft, vector origin, vector point, IEntity entity)
 {
  TraceParam trace = new TraceParam();
  trace.Start = origin; trace.End = point;
  trace.Flags = TraceFlags.WORLD | TraceFlags.ENTS; trace.Exclude = aircraft;
  float hit = aircraft.GetWorld().TraceMove(trace, null);
  if (hit >= 1) return true;
  IEntity hitEntity = trace.TraceEnt;
  for (int i = 0; i < 8 && hitEntity; i++)
  {
   if (hitEntity == entity) return true;
   hitEntity = hitEntity.GetParent();
  }
  return false;
 }
 static float Quality(BaseWorld world, int channel)
 {
  BaseWeatherManagerEntity weather = BaseWeatherManagerEntity.Cast(WeatherManager.GetRegisteredWeatherManagerEntity(world));
  if (!weather) return 1;
  float quality = 1 - Math.Clamp(weather.GetRainIntensity() * 0.35 + weather.GetFogAmount() * 0.6, 0, 0.75);
  if (channel == 0)
  {
   float sunrise, sunset;
   if (weather.GetSunriseHour(sunrise) && weather.GetSunsetHour(sunset))
   {
    float hour = weather.GetTimeOfTheDay();
    if (hour < sunrise || hour > sunset) quality *= 0.5;
   }
  }
  return Math.Clamp(quality, 0.25, 1);
 }
 // Measure the unpadded world bounds in a virtual optical image, independent of monitor resolution.
 static bool Measure(IEntity entity, vector origin, vector forward, float zoom, float aspect, int channel, out float shortSide, out float longSide)
 {
  vector right = Vector(forward[2], 0, -forward[0]);
  if (right.Length() < 0.0001) return false;
  right.Normalize();
  vector up = Vector(forward[1]*right[2],forward[2]*right[0]-forward[0]*right[2],-forward[1]*right[0]);
  vector low, high; entity.GetWorldBounds(low, high);
  float x0 = 100000, x1 = -100000, y0 = 100000, y1 = -100000;
  for (int i = 0; i < 8; i++)
  {
   vector corner = low;
   if ((i & 1) != 0) corner[0] = high[0];
   if ((i & 2) != 0) corner[1] = high[1];
   if ((i & 4) != 0) corner[2] = high[2];
   vector offset = corner - origin;
   float depth = vector.Dot(offset, forward);
   if (depth <= 0.1) return false;
   float x = vector.Dot(offset, right) / depth;
   float y = vector.Dot(offset, up) / depth;
   x0 = Math.Min(x0, x); x1 = Math.Max(x1, x);
   y0 = Math.Min(y0, y); y1 = Math.Max(y1, y);
  }
  float viewTan = Math.Tan(30 * Math.DEG2RAD) / zoom;
  if (x1 < -viewTan || x0 > viewTan || y1 < -viewTan / aspect || y0 > viewTan / aspect) return false;
  float resolution = 1920;
  if (channel != 0) resolution = 640;
  float focal = resolution * 0.5 * Math.Min(zoom, 20) / Math.Tan(30 * Math.DEG2RAD);
  float width = (x1 - x0) * focal, height = (y1 - y0) * focal;
  shortSide = Math.Min(width, height); longSide = Math.Max(width, height);
  return true;
 }
 static bool Observe(IEntity aircraft, IEntity entity, vector direction, float zoom, float aspect, int channel, float range, out bool classEligible)
 {
  classEligible = false;
  if (!Alive(entity) || entity == aircraft) return false;
  vector origin = ORD_CameraMounts.SensorOrigin(aircraft, direction);
  vector point = Point(entity);
  if (vector.Distance(origin, point) > range) return false;
  float shortSide, longSide;
  if (!Measure(entity, origin, direction, zoom, aspect, channel, shortSide, longSide)) return false;
  if (shortSide < 2 || longSide < 4) return false;
  if (!Visible(aircraft, origin, point, entity)) return false;
  if (ChimeraCharacter.Cast(entity)) classEligible = shortSide >= 6 && longSide >= 24;
  else classEligible = shortSide >= 8 && longSide >= 20;
  return true;
 }
}
