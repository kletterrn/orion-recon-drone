enum ORD_TargetMode { SENSOR_POINT, VEHICLE, MAP_POINT }
// Server-owned aircraft and mission state. Client commands arrive via ORD_Gateway.
enum ORD_Command { CLAIM, RELEASE, HEARTBEAT, SENSOR, PILOT, LOITER, PATROL, RETURN_HOME, HOLD, ENGINE, TRACK, CLEAR_TRACK, QUEUE_POINT, CLEAR_ROUTE, SERVICE, ALT_UP, ALT_DOWN, SPEED_UP, SPEED_DOWN, RADIUS_UP, RADIUS_DOWN, GROUP_TRACK, ARM, FIRE, RESUME_ROUTE }
enum ORD_ContactState { NONE, POINT, ENTITY, TEMP_LOSS, LOST, GROUP, ACQUIRING }
enum ORD_FireStatus { READY, SAFED, EMPTY, NO_SENSOR, GROUND, NO_TARGET, RANGE, COOLDOWN, RESOURCE, FIRED }

class ORD_GroupMember
{
 IEntity Entity;
 vector Observed;
 float LastSeen;
 ref ORD_ObservationEvidence Evidence = new ORD_ObservationEvidence();
}

class ORD_AircraftComponentClass : ScriptComponentClass {}
class ORD_AircraftComponent : ScriptComponent
{
 static ref array<ORD_AircraftComponent> Aircraft = {};
 [Attribute("USSR")] protected string m_sFaction;
 [Attribute("20000")] protected float m_fLinkRange;
 [Attribute("450")] protected float m_fAltitude;
 [Attribute("55.56")] protected float m_fCruiseSpeed;
 [Attribute("450")] protected float m_fLoiterRadius;
 [Attribute("90")] protected float m_fClearance;
 [Attribute("5000")] protected float m_fSensorRange;
 [Attribute("1")] protected float m_fFuelMultiplier;
 [Attribute("0")] protected bool m_bDiagnostics;
 [Attribute("{A223BDDFF049C2B1}Prefabs/ORD/ORD_Banderol.et", UIWidgets.ResourceNamePicker, "Banderol projectile", "et")] protected ResourceName m_rBanderol;
 [Attribute("{641FAD527420C378}Prefabs/ORD/ORD_BanderolStore.et", UIWidgets.ResourceNamePicker, "Banderol store", "et")] protected ResourceName m_rBanderolStore;
 [Attribute(desc: "Optional initial route positions")] protected ref array<vector> m_aPatrol;
 [RplProp()] protected int m_iOperator;
 [RplProp()] protected bool m_bAuto;
 [RplProp()] protected bool m_bSensorMode;
 [RplProp()] protected bool m_bDesignated;
 [RplProp()] protected bool m_bTracking;
 [RplProp()] protected int m_iContactState;
 [RplProp()] protected float m_fGroupSpan;
 [RplProp()] protected bool m_bEngineOn;
 [RplProp()] protected bool m_bReturnHome;
 [RplProp()] protected bool m_bArmed;
 [RplProp()] protected int m_iAmmo = 1;
 [RplProp()] protected int m_iFireStatus;
 [RplProp()] protected vector m_vTarget;
 [RplProp()] protected vector m_vSensorDirection = "0 0 1";
 vector SensorDirection() { return m_vSensorDirection; }
 [RplProp()] protected float m_fFuel = 1;
 [RplProp()] protected float m_fTargetAltitude = 450;
 [RplProp()] protected float m_fTargetSpeed = 55.56;
 [RplProp()] protected float m_fTargetRadius = 450;
 [RplProp()] protected int m_iRouteCount;
 protected IEntity m_Terminal, m_TrackedEntity;
 protected ref ORD_ObservationEvidence m_TrackEvidence = new ORD_ObservationEvidence();
 protected bool m_bTrackRequested;
 protected float m_fSensorZoom = 1, m_fSensorAspect = 1.77778, m_fOpticsTime = -100, m_fObservationNext, m_fAcquireStart;
 protected int m_iSensorChannel, m_iOpticsSequence = -1;
 [RplProp()] protected int m_iClassification;
 [RplProp()] protected float m_fObservedTime;
 int Classification() { return m_iClassification; }
 float ObservedTime() { return m_fObservedTime; }
 // Presentation binding only: never used to accept targeting or flight commands.
 [RplProp()] protected RplId m_HUDTrackedId = RplId.Invalid();
 IEntity HUDTrackedEntity()
 {
  if (Replication.IsServer()) return m_TrackedEntity;
  return SCR_PlayerController.ORD_Entity(m_HUDTrackedId);
 }
 protected IEntity m_StoreLeft, m_StoreRight;
 protected bool m_bStoresInitialized;
 protected bool m_bGroupTracking;
 protected ref array<ref ORD_GroupMember> m_aGroup = {};
 protected ref array<IEntity> m_aGroupCandidates = {};
 [RplProp()] protected vector m_vHome;
 [RplProp()] protected vector m_vOrbit;
 protected ref array<vector> m_aRoute = {};
 protected float m_ConnectionGrace;
 protected float m_fHeartbeat, m_fInputTime, m_fLastObserved, m_fClock, m_fNextLog = 5, m_fNextReplication, m_fNextGroupScan;
 protected float m_fLastLaunch = -100;
 protected float m_fAltitudeTrim, m_fThrottleTrim = 0.6;
 [RplProp()] protected int m_iWaypoint;
 [RplProp()] protected bool m_bPatrol;
 [RplProp()] protected int m_iMissionRevision;
 [RplProp()] protected string m_sMissionStatus = "Ready";
 protected float m_fLastMissionRequest = -100;
 [RplProp()] protected vector m_vRoute0;
 [RplProp()] protected vector m_vRoute1;
 [RplProp()] protected vector m_vRoute2;
 [RplProp()] protected vector m_vRoute3;
 [RplProp()] protected vector m_vRoute4;
 [RplProp()] protected vector m_vRoute5;
 [RplProp()] protected vector m_vRoute6;
 [RplProp()] protected vector m_vRoute7;
 float Pitch, Roll, Yaw, Throttle, Brake = 1;

 override void OnPostInit(IEntity owner)
 {
  super.OnPostInit(owner);
  if (!Aircraft.Contains(this)) Aircraft.Insert(this);
  if (Replication.IsServer())
  {
   m_vHome = owner.GetOrigin(); m_vOrbit = m_vHome; m_iFireStatus = ORD_FireStatus.SAFED;
   m_fTargetAltitude = m_fAltitude; m_fTargetSpeed = m_fCruiseSpeed; m_fTargetRadius = m_fLoiterRadius;
  }
 }
 override void OnDelete(IEntity owner)
 {
  if(Replication.IsServer()) RestoreOperatorObserver();
  if (Replication.IsServer())
  {
   if (m_StoreLeft) SCR_EntityHelper.DeleteEntityAndChildren(m_StoreLeft);
   if (m_StoreRight) SCR_EntityHelper.DeleteEntityAndChildren(m_StoreRight);
  }
  Aircraft.RemoveItem(this);
  super.OnDelete(owner);
 }
 int MissionRevision() { return m_iMissionRevision; }
 string FlightModeText()
 {
  if (m_bReturnHome) return "RETURN HOME";
  if (m_bPatrol) return "ROUTE";
  if (m_bAuto) return "LOITER / HOLD";
  return "MANUAL";
 }
 string MissionStatus() { return m_sMissionStatus; }
 int ActiveWaypoint() { return m_iWaypoint; }
 bool FlyingRoute() { return m_bPatrol && m_bAuto; }
 vector Home() { return m_vHome; }
 vector Orbit() { return m_vOrbit; }
 vector RoutePoint(int index)
 {
  switch (index)
  {
   case 0: return m_vRoute0;
   case 1: return m_vRoute1;
   case 2: return m_vRoute2;
   case 3: return m_vRoute3;
   case 4: return m_vRoute4;
   case 5: return m_vRoute5;
   case 6: return m_vRoute6;
   case 7: return m_vRoute7;
  }
  return vector.Zero;
 }
 protected void PublishRoute()
 {
  m_iRouteCount = m_aRoute.Count();
  m_vRoute0 = vector.Zero; if (m_iRouteCount > 0) m_vRoute0 = m_aRoute[0];
  m_vRoute1 = vector.Zero; if (m_iRouteCount > 1) m_vRoute1 = m_aRoute[1];
  m_vRoute2 = vector.Zero; if (m_iRouteCount > 2) m_vRoute2 = m_aRoute[2];
  m_vRoute3 = vector.Zero; if (m_iRouteCount > 3) m_vRoute3 = m_aRoute[3];
  m_vRoute4 = vector.Zero; if (m_iRouteCount > 4) m_vRoute4 = m_aRoute[4];
  m_vRoute5 = vector.Zero; if (m_iRouteCount > 5) m_vRoute5 = m_aRoute[5];
  m_vRoute6 = vector.Zero; if (m_iRouteCount > 6) m_vRoute6 = m_aRoute[6];
  m_vRoute7 = vector.Zero; if (m_iRouteCount > 7) m_vRoute7 = m_aRoute[7];
  m_iMissionRevision++;
  Replication.BumpMe();
 }
 protected void MissionResult(string message)
 {
  m_sMissionStatus = message; Replication.BumpMe();
 }
 bool ValidMapPoint(vector point)
 {
  vector minimum, maximum; GetOwner().GetWorld().GetBoundBox(minimum, maximum);
  if (!(point[0] >= minimum[0] && point[0] <= maximum[0] && point[2] >= minimum[2] && point[2] <= maximum[2])) return false;
  vector delta = point - GetOwner().GetOrigin(); delta[1] = 0;
  return delta.Length() <= m_fLinkRange;
 }
 void ApplyMission(int id, array<vector> points, float altitude, float speed, float radius, int revision)
 {
  if (!Replication.IsServer() || !ValidLink(id)) return;
  if (m_fClock - m_fLastMissionRequest < 0.25) { MissionResult("Please wait before applying again"); return; }
  m_fLastMissionRequest = m_fClock;
  if (revision != m_iMissionRevision) { MissionResult("Route changed: reload the accepted route"); return; }
  if (!points || points.Count() > 8 || !(altitude >= 150 && altitude <= 2000 && speed >= 30 && speed <= 65 && radius >= 250 && radius <= 1500))
  { MissionResult("Invalid mission settings"); return; }
  foreach (vector point : points) if (!ValidMapPoint(point)) { MissionResult("Point outside terrain or link range"); return; }
  m_aRoute.Clear();
  foreach (vector requested : points) m_aRoute.Insert(Vector(requested[0], GetOwner().GetWorld().GetSurfaceY(requested[0], requested[2]), requested[2]));
  m_fAltitude = altitude; m_fCruiseSpeed = speed; m_fLoiterRadius = radius;
  m_fTargetAltitude = altitude; m_fTargetSpeed = speed; m_fTargetRadius = radius;
  m_iWaypoint = 0;
  if (m_aRoute.IsEmpty() || m_bPatrol) Hold();
  PublishRoute(); MissionResult("Route applied - select Fly route");
 }
 void WeaponRequest(int id, int mode, vector point)
 {
  if (!Replication.IsServer() || !ValidLink(id)) return;
  // Sensor requests carry a unit view direction; the server selects the hit.
  if (mode == ORD_TargetMode.SENSOR_POINT) { FireAt(id, point); return; }
  if (mode == ORD_TargetMode.VEHICLE)
  {
   if (!m_bSensorMode || !m_bTracking || !Vehicle.Cast(m_TrackedEntity) || !ContactAlive(m_TrackedEntity) || m_iContactState != ORD_ContactState.ENTITY)
   { SetFireStatus(ORD_FireStatus.NO_TARGET); return; }
   FireBanderol(ORD_TargetMode.VEHICLE); return;
  }
  if (mode != ORD_TargetMode.MAP_POINT || !ValidMapPoint(point)) { SetFireStatus(ORD_FireStatus.NO_TARGET); return; }
  vector target = Vector(point[0], GetOwner().GetWorld().GetSurfaceY(point[0], point[2]), point[2]);
  FireBanderol(ORD_TargetMode.MAP_POINT, target);
 }
 bool PayloadTransform(out vector local[4])
 {
  return ORD_RC8Rig.Socket(GetOwner(),"ORION_PAYLOAD_SOCKET",local);
 }
 int Operator() { return m_iOperator; }
 bool Automatic() { return m_bAuto; }
 bool SensorMode() { return m_bSensorMode; }
 bool Designated() { return m_bDesignated; }
 bool Tracking() { return m_bTracking; }
 int ContactState() { return m_iContactState; }
 float GroupSpan() { return m_fGroupSpan; }
 bool PointLocked() { return m_iContactState == ORD_ContactState.POINT; }
 bool EngineOn() { return m_bEngineOn; }
 bool ReturningHome() { return m_bReturnHome; }
 bool Armed() { return m_bArmed; }
 int Ammo() { return m_iAmmo; }
 int FireStatus() { return m_iFireStatus; }
 string WeaponStatusText()
 {
  switch (m_iFireStatus)
  {
   case ORD_FireStatus.READY: return "Weapon ready";
   case ORD_FireStatus.SAFED: return "Weapon safe";
   case ORD_FireStatus.EMPTY: return "No missiles remaining";
   case ORD_FireStatus.NO_SENSOR: return "Sensor view required";
   case ORD_FireStatus.GROUND: return "Airborne required";
   case ORD_FireStatus.NO_TARGET: return "No valid target";
   case ORD_FireStatus.RANGE: return "Target outside 100-5000 m";
   case ORD_FireStatus.COOLDOWN: return "Launch cooldown";
   case ORD_FireStatus.RESOURCE: return "Missile resource unavailable";
   case ORD_FireStatus.FIRED: return "Missile launched";
  }
  return "";
 }

 float Fuel() { return m_fFuel; }
 float TargetAltitude() { return m_fTargetAltitude; }
 float TargetSpeed() { return m_fTargetSpeed; }
 float LoiterRadius() { return m_fTargetRadius; }
 float Heading()
 {
  vector forward = GetOwner().GetTransformAxis(2);
  return Math.Atan2(forward[0],forward[2])*Math.RAD2DEG;
 }
 int RouteCount() { return m_iRouteCount; }
 vector Target() { return m_vTarget; }
 float SensorRange() { return m_fSensorRange; }
 float LinkRange() { return m_fLinkRange; }
 float Speed()
 {
  Physics physics = GetOwner().GetPhysics();
  if (!physics) return 0;
  return physics.GetVelocity().Length();
 }
 bool Grounded()
 {
  VehicleWheeledSimulation wheels = VehicleWheeledSimulation.Cast(GetOwner().FindComponent(VehicleWheeledSimulation));
  return wheels && wheels.HasAnyGroundContact();
 }
 bool Destroyed()
 {
  SCR_DamageManagerComponent damage = SCR_DamageManagerComponent.Cast(GetOwner().FindComponent(SCR_DamageManagerComponent));
  return damage && damage.IsDestroyed();
 }
 bool ValidLink(int id)
 {
  if (id <= 0 || id != m_iOperator || !m_Terminal || Destroyed()) return false;
  IEntity player = GetGame().GetPlayerManager().GetPlayerControlledEntity(id);
  if (!player || vector.Distance(player.GetOrigin(), m_Terminal.GetOrigin()) > 4) return false;
  SCR_CharacterControllerComponent controller = SCR_CharacterControllerComponent.Cast(player.FindComponent(SCR_CharacterControllerComponent));
  if (!controller || controller.IsDead()) return false;
  if (m_sFaction != "")
  {
   FactionAffiliationComponent affiliation = FactionAffiliationComponent.Cast(player.FindComponent(FactionAffiliationComponent));
   if (!affiliation || !affiliation.GetAffiliatedFaction() || affiliation.GetAffiliatedFaction().GetFactionKey() != m_sFaction) return false;
  }
  return vector.Distance(GetOwner().GetOrigin(), m_Terminal.GetOrigin()) <= m_fLinkRange;
 }
 void Command(int id, int command, IEntity terminal)
 {
  if (!Replication.IsServer()) return;
  if (command == ORD_Command.CLAIM)
  {
   if (m_iOperator != 0 || !terminal || !terminal.FindComponent(ORD_TerminalComponent)) return;
   m_iOperator = id; m_Terminal = terminal;
   if (!ValidLink(id)) { m_iOperator = 0; m_Terminal = null; return; }
   m_iOpticsSequence=-1; m_fOpticsTime=-100; m_fHeartbeat = m_fClock; m_ConnectionGrace=m_fClock+15; m_fInputTime = m_fClock; Replication.BumpMe(); return;
  }
  if (id != m_iOperator || id <= 0) return;
  if (command == ORD_Command.RELEASE) { LoseLink(); return; }
  if (!ValidLink(id)) { LoseLink(); return; }
  m_fHeartbeat = m_fClock; m_ConnectionGrace=0;
  switch (command)
  {
   case ORD_Command.SENSOR: m_bSensorMode = true; if (!m_bAuto) Hold(); break;
   case ORD_Command.PILOT: m_bSensorMode = false; m_fInputTime = m_fClock; break;
   case ORD_Command.LOITER:
    if (Grounded()) MissionResult("Airborne required for loiter");
    else { Hold(); if (m_bDesignated) m_vOrbit = m_vTarget; MissionResult("Loiter active - Resume route to continue"); }
    break;
   case ORD_Command.PATROL:
    if (Grounded()) MissionResult("Airborne required - take off manually");
    else if (m_aRoute.IsEmpty()) MissionResult("Apply a route first");
    if (!Grounded())
    {
     if (!m_aRoute.IsEmpty())
     {
      m_bAuto = true; m_bPatrol = true; m_bReturnHome = false; m_iWaypoint = 0; MissionResult("Repeating route");
     }
    }
    break;
   case ORD_Command.RESUME_ROUTE:
    if (Grounded()) MissionResult("Airborne required - take off manually");
    else if (m_aRoute.IsEmpty()) MissionResult("Apply a route first");
    else { m_bAuto = true; m_bPatrol = true; m_bReturnHome = false; MissionResult("Route resumed"); }
    break;
   case ORD_Command.RETURN_HOME: ReturnHome(); break;
   case ORD_Command.HOLD: Hold(); break;
   case ORD_Command.ENGINE: if (m_fFuel > 0 && !Destroyed()) m_bEngineOn = !m_bEngineOn; break;
   case ORD_Command.ARM: m_bArmed = !m_bArmed; if (m_bArmed) m_iFireStatus = ORD_FireStatus.READY; else m_iFireStatus = ORD_FireStatus.SAFED; break;
   case ORD_Command.FIRE: FireBanderol(); break;
   case ORD_Command.TRACK:
    if (m_bSensorMode && m_TrackedEntity && m_bDesignated && m_iContactState == ORD_ContactState.POINT)
    { m_bTrackRequested=true; m_fAcquireStart=m_fClock; m_iContactState=ORD_ContactState.ACQUIRING; m_fLastObserved=m_fClock; }
    break;
   case ORD_Command.GROUP_TRACK: if (m_bSensorMode) StartGroupTrack(); break;
   case ORD_Command.CLEAR_TRACK: ClearContact(); break;
   case ORD_Command.QUEUE_POINT:
    if (m_bDesignated && m_aRoute.Count() < 8)
    {
     m_aRoute.Insert(m_vTarget); m_iRouteCount = m_aRoute.Count();
     MissionResult("Point added - select Fly route");
    }
    break;
   case ORD_Command.CLEAR_ROUTE: m_aRoute.Clear(); m_iWaypoint = 0; Hold(); PublishRoute(); MissionResult("Route cleared - holding"); break;
   case ORD_Command.SERVICE: Service(); break;
   case ORD_Command.ALT_UP: m_fAltitude = Math.Min(2000, m_fAltitude + 50); break;
   case ORD_Command.ALT_DOWN: m_fAltitude = Math.Max(150, m_fAltitude - 50); break;
   case ORD_Command.SPEED_UP: m_fCruiseSpeed = Math.Min(65, m_fCruiseSpeed + 2.78); break;
   case ORD_Command.SPEED_DOWN: m_fCruiseSpeed = Math.Max(30, m_fCruiseSpeed - 2.78); break;
   case ORD_Command.RADIUS_UP: m_fLoiterRadius = Math.Min(1500, m_fLoiterRadius + 50); break;
   case ORD_Command.RADIUS_DOWN: m_fLoiterRadius = Math.Max(250, m_fLoiterRadius - 50); break;
  }
  m_fTargetAltitude = m_fAltitude; m_fTargetSpeed = m_fCruiseSpeed; m_fTargetRadius = m_fLoiterRadius;
  if (command == ORD_Command.QUEUE_POINT || command == ORD_Command.ALT_UP || command == ORD_Command.ALT_DOWN || command == ORD_Command.SPEED_UP || command == ORD_Command.SPEED_DOWN || command == ORD_Command.RADIUS_UP || command == ORD_Command.RADIUS_DOWN) PublishRoute();
  Replication.BumpMe();
 }
 void Input(int id, float pitch, float roll, float yaw, float throttle, float brake)
 {
  if (!Replication.IsServer() || !ValidLink(id) || m_bSensorMode) return;
  if (!(pitch >= -1 && pitch <= 1 && roll >= -1 && roll <= 1 && yaw >= -1 && yaw <= 1 && throttle >= 0 && throttle <= 1 && brake >= 0 && brake <= 1)) return;
  if (m_bAuto) { m_bAuto = false; m_bReturnHome = false; Replication.BumpMe(); }
  Pitch = pitch * 0.7; Roll = roll; Yaw = yaw; Throttle = throttle; Brake = brake;
  m_fInputTime = m_fClock;
 }
 void Optics(int id, vector direction, float zoom, float aspect, int channel, int sequence, bool designate)
 {
  if(!Replication.IsServer() || !ValidLink(id) || !m_bSensorMode || sequence<=m_iOpticsSequence)return;
  if(!(zoom>=1 && zoom<=40 && aspect>=0.5 && aspect<=4 && channel>=0 && channel<=2))return;
  float length=direction.Length(); if(!(length>0.99 && length<1.01))return;
  m_iOpticsSequence=sequence; m_fOpticsTime=m_fClock; m_fSensorZoom=zoom; m_fSensorAspect=aspect; m_iSensorChannel=channel;
  Aim(id,direction,designate);
 }
 void Aim(int id, vector direction, bool designate)
 {
  if (!Replication.IsServer() || !ValidLink(id) || !m_bSensorMode) return;
  float length = direction.Length();
  if (!(length > 0.99 && length < 1.01)) return;
  direction = ORD_CameraMounts.Constrain(GetOwner(),direction);
  m_vSensorDirection = direction;
  if (!designate) { Replication.BumpMe(); return; }
  TraceParam trace = new TraceParam();
  trace.Start = ORD_CameraMounts.SensorOrigin(GetOwner(),direction);
  trace.End = trace.Start + direction * m_fSensorRange;
  trace.Flags = TraceFlags.WORLD | TraceFlags.ENTS;
  trace.Exclude = GetOwner();
  float hit = GetOwner().GetWorld().TraceMove(trace, null);
  if (hit < 1)
  {
   ClearContact();
   m_bDesignated = true; m_iContactState = ORD_ContactState.POINT;
   m_vTarget = trace.Start + (trace.End - trace.Start) * hit;
   m_TrackedEntity = null;
   IEntity candidate = trace.TraceEnt;
   for (int i = 0; i < 4 && candidate; i++)
   {
    if (ChimeraCharacter.Cast(candidate) || Vehicle.Cast(candidate)) { m_TrackedEntity = candidate; break; }
    candidate = candidate.GetParent();
   }
   m_HUDTrackedId = SCR_PlayerController.ORD_Id(m_TrackedEntity);
   m_fLastObserved = m_fClock;
   Replication.BumpMe();
  }
 }
 void FireAt(int id, vector direction)
 {
  if (!Replication.IsServer() || !ValidLink(id)) return;
  if (!m_bArmed) { SetFireStatus(ORD_FireStatus.SAFED); return; }
  if (m_iAmmo <= 0) { SetFireStatus(ORD_FireStatus.EMPTY); return; }
  if (!m_bSensorMode) { SetFireStatus(ORD_FireStatus.NO_SENSOR); return; }
  if (Grounded()) { SetFireStatus(ORD_FireStatus.GROUND); return; }
  float length = direction.Length();
  if (!(length > 0.99 && length < 1.01)) { SetFireStatus(ORD_FireStatus.NO_TARGET); return; }
  direction = ORD_CameraMounts.Constrain(GetOwner(),direction);
  TraceParam trace = new TraceParam();
  trace.Start = ORD_CameraMounts.SensorOrigin(GetOwner(),direction);
  trace.End = trace.Start + direction * m_fSensorRange;
  trace.Flags = TraceFlags.WORLD | TraceFlags.ENTS;
  trace.Exclude = GetOwner();
  float fraction = GetOwner().GetWorld().TraceMove(trace, null);
  if (fraction >= 1) { SetFireStatus(ORD_FireStatus.NO_TARGET); return; }
  ClearContact();
  m_bDesignated = true; m_iContactState = ORD_ContactState.POINT;
  m_vTarget = trace.Start + (trace.End - trace.Start) * fraction;
  m_fLastObserved = m_fClock;
  FireBanderol();
 }
 void MapPoint(int id, vector requested, bool orbit, float radius = -1)
 {
  if (!Replication.IsServer() || !ValidLink(id)) return;
  vector here = GetOwner().GetOrigin();
  vector flat = requested - here; flat[1] = 0;
  if (!ValidMapPoint(requested) || (!orbit && m_aRoute.Count() >= 8)) { MissionResult("Invalid map point"); return; }
  if (orbit && Grounded()) { MissionResult("Airborne required for loiter"); return; }
  if (orbit && radius != -1 && !(radius >= 250 && radius <= 1500)) { MissionResult("Invalid loiter radius"); return; }
  bool radiusChanged = orbit && radius != -1 && radius != m_fLoiterRadius;
  if (radiusChanged) { m_fLoiterRadius = radius; m_fTargetRadius = radius; }
  float terrain = GetOwner().GetWorld().GetSurfaceY(requested[0], requested[2]);
  vector point = Vector(requested[0], terrain, requested[2]);
  if (orbit) { Hold(); m_vOrbit = point; MissionResult("Loiter active - Resume route to continue"); }
  else
  {
   m_aRoute.Insert(point); m_iRouteCount = m_aRoute.Count();
  }
  if (!orbit || radiusChanged) PublishRoute();
  else Replication.BumpMe();
 }
 protected void Hold()
 {
  m_bPatrol = false; m_bReturnHome = false; m_bAuto = !Grounded(); m_vOrbit = GetOwner().GetOrigin();
  if (!m_bAuto) { Throttle = 0; Brake = 1; Pitch = 0; Roll = 0; Yaw = 0; }
 }
 protected void ReturnHome()
 {
  if (Grounded()) { Hold(); return; }
  m_bPatrol = false; m_bAuto = true; m_bReturnHome = true; m_vOrbit = m_vHome;
 }
 protected void RestoreOperatorObserver()
 {
  if(m_iOperator<=0) return;
  SCR_PlayerController controller=SCR_PlayerController.Cast(GetGame().GetPlayerManager().GetPlayerController(m_iOperator));
  if(controller) controller.ORD_RestoreObserver();
 }
 protected void LoseLink()
 {
  RestoreOperatorObserver();
  m_iOperator = 0; m_Terminal = null; m_bArmed = false; m_iFireStatus = ORD_FireStatus.SAFED; ClearContact();
  ReturnHome(); m_bSensorMode = m_bAuto; Replication.BumpMe();
 }
 protected void ClearContact()
 {
  m_bDesignated = false; m_bTracking = false; m_bTrackRequested=false; m_bGroupTracking = false; m_TrackedEntity = null; m_iContactState = ORD_ContactState.NONE;
  m_TrackEvidence=new ORD_ObservationEvidence(); m_iClassification=0;
  m_HUDTrackedId = RplId.Invalid();
  m_aGroup.Clear(); m_aGroupCandidates.Clear(); m_fGroupSpan = 0;
 }
 protected bool CollectGroupCandidate(IEntity entity)
 {
  if (entity && ChimeraCharacter.Cast(entity) && ContactAlive(entity)) m_aGroupCandidates.Insert(entity);
  return m_aGroupCandidates.Count() < 24;
 }
 protected bool ContactAlive(IEntity entity)
 {
  if (!entity) return false;
  SCR_CharacterControllerComponent character = SCR_CharacterControllerComponent.Cast(entity.FindComponent(SCR_CharacterControllerComponent));
  if (character && character.IsDead()) return false;
  SCR_DamageManagerComponent damage = SCR_DamageManagerComponent.Cast(entity.FindComponent(SCR_DamageManagerComponent));
  if (damage && damage.IsDestroyed()) return false;
  return true;
 }
 protected void StartGroupTrack()
 {
  if (!m_bDesignated || !m_TrackedEntity || !ChimeraCharacter.Cast(m_TrackedEntity) || !m_TrackEvidence.Classified) return;
  vector start = ORD_CameraMounts.SensorOrigin(GetOwner(),m_vSensorDirection);
  m_aGroupCandidates.Clear();
  GetOwner().GetWorld().QueryEntitiesBySphere(m_TrackedEntity.GetOrigin(), 45, CollectGroupCandidate, null, EQueryEntitiesFlags.DYNAMIC);
  m_aGroup.Clear();
  vector center = vector.Zero;
  foreach (IEntity candidate : m_aGroupCandidates)
  {
   if (m_aGroup.Count() >= 12) break;
   if (!ContactAlive(candidate)) continue;
   vector observed = candidate.GetOrigin() + Vector(0, 0.9, 0);
   if (vector.Distance(start, observed) > m_fSensorRange || !ObservationVisible(start, observed, candidate)) continue;
   ref ORD_GroupMember member = new ORD_GroupMember();
   member.Entity = candidate; member.Observed = observed; member.LastSeen = m_fClock;
   m_aGroup.Insert(member); center += observed;
  }
  if (m_aGroup.Count() < 3) { m_aGroup.Clear(); return; }
  center = center / m_aGroup.Count();
  m_fGroupSpan = 1;
  foreach (ORD_GroupMember member : m_aGroup) m_fGroupSpan = Math.Max(m_fGroupSpan, vector.Distance(center, member.Observed));
  m_bGroupTracking = true; m_bTrackRequested=true; m_bTracking = false; m_iContactState = ORD_ContactState.ACQUIRING; m_fAcquireStart=m_fClock;
  m_fLastObserved = m_fClock; m_fNextGroupScan = m_fClock + 0.2;
 }
 protected void UpdateGroupTrack()
 {
  if (m_fClock < m_fNextGroupScan) return;
  m_fNextGroupScan = m_fClock + 0.2;
  vector start = ORD_CameraMounts.SensorOrigin(GetOwner(),m_vSensorDirection);
  vector center = vector.Zero;
  int observedCount;
  foreach (ORD_GroupMember member : m_aGroup)
  {
   if (!member || !ContactAlive(member.Entity)) continue;
   vector point = member.Entity.GetOrigin() + Vector(0, 0.9, 0);
   bool classEligible;
   bool visible=m_fClock-m_fOpticsTime<0.5 && m_bSensorMode && vector.Distance(point,m_vTarget)<=80 && ORD_ObservationPolicy.Observe(GetOwner(),member.Entity,m_vSensorDirection,m_fSensorZoom,m_fSensorAspect,m_iSensorChannel,m_fSensorRange,classEligible);
   member.Evidence.Sample(m_fClock,visible,classEligible,true,ORD_ObservationPolicy.Quality(GetOwner().GetWorld(),m_iSensorChannel));
   if(!visible || !member.Evidence.Acquired)continue;
   member.Observed = point; member.LastSeen = m_fClock;
   center += point; observedCount++;
  }
  if (observedCount >= 2)
  {
   center = center / observedCount;
   m_fGroupSpan = 1;
   foreach (ORD_GroupMember member : m_aGroup)
   {
    if (member && m_fClock - member.LastSeen < 0.5) m_fGroupSpan = Math.Max(m_fGroupSpan, vector.Distance(center, member.Observed));
   }
   m_vTarget = center; m_fLastObserved = m_fClock; m_fObservedTime=m_fClock; m_bDesignated = true; m_bTracking=true;
   if (m_iContactState != ORD_ContactState.GROUP) { m_iContactState = ORD_ContactState.GROUP; Replication.BumpMe(); }
  }
  else if(m_iContactState==ORD_ContactState.ACQUIRING && m_fClock-m_fAcquireStart<15) return;
  else if (m_fClock - m_fLastObserved < 2)
  {
   if (m_iContactState != ORD_ContactState.TEMP_LOSS) { m_iContactState = ORD_ContactState.TEMP_LOSS; Replication.BumpMe(); }
  }
  else
  {
   m_bTracking = false; m_bGroupTracking = false; m_aGroup.Clear(); m_iContactState = ORD_ContactState.LOST;
   Replication.BumpMe();
  }
 }
 protected bool ObservationVisible(vector start, vector goal, IEntity contact)
 {
  return ORD_ObservationPolicy.Visible(GetOwner(),start,goal,contact);
 }
 protected void UpdateTrack()
 {
  if(m_bGroupTracking) { UpdateGroupTrack(); return; }
  if(!m_TrackedEntity || !m_bDesignated || m_fClock<m_fObservationNext)return;
  m_fObservationNext=m_fClock+0.1;
  bool classEligible;
  bool visible=m_bSensorMode && m_fClock-m_fOpticsTime<0.5 && ORD_ObservationPolicy.Observe(GetOwner(),m_TrackedEntity,m_vSensorDirection,m_fSensorZoom,m_fSensorAspect,m_iSensorChannel,m_fSensorRange,classEligible);
  m_TrackEvidence.Sample(m_fClock,visible,classEligible,ChimeraCharacter.Cast(m_TrackedEntity)!=null,ORD_ObservationPolicy.Quality(GetOwner().GetWorld(),m_iSensorChannel));
  int kind=0;
  if(m_TrackEvidence.Classified) { kind=2; if(ChimeraCharacter.Cast(m_TrackedEntity))kind=1; }
  if(kind!=m_iClassification) { m_iClassification=kind; Replication.BumpMe(); }
  if(!m_bTrackRequested)return;
  if(visible && m_TrackEvidence.Acquired)
  {
   m_vTarget=ORD_ObservationPolicy.Point(m_TrackedEntity); m_fLastObserved=m_fClock; m_fObservedTime=m_fClock;
   m_bTracking=true; m_iContactState=ORD_ContactState.ENTITY; m_HUDTrackedId=SCR_PlayerController.ORD_Id(m_TrackedEntity);
   Replication.BumpMe(); return;
  }
  if(m_iContactState==ORD_ContactState.ACQUIRING)
  {
   if(m_fClock-m_fAcquireStart>15)ClearContact();
   return;
  }
  m_iContactState=ORD_ContactState.TEMP_LOSS;
  if(m_fClock-m_fLastObserved>=2) { m_bTracking=false; m_iContactState=ORD_ContactState.LOST; m_HUDTrackedId=RplId.Invalid(); }
  Replication.BumpMe();
 }
 void Simulate(float dt)
 {
  if (!Replication.IsServer()) return;
  if (!m_bStoresInitialized) { m_bStoresInitialized = true; SpawnStores(); }
  m_fClock += dt;
  if (m_bDiagnostics && m_fClock >= m_fNextLog)
  {
   m_fNextLog = m_fClock + 5;
   Print(string.Format("ORD position=%1 speed=%2 grounded=%3 operator=%4 throttle=%5 auto=%6 fuel=%7", GetOwner().GetOrigin(), Speed(), Grounded(), m_iOperator, Throttle, m_bAuto, m_fFuel));
  }
  if (Destroyed()) { Throttle = 0; Brake = 1; m_bEngineOn = false; if (m_iOperator != 0) LoseLink(); return; }
  if (m_bEngineOn && m_fFuel > 0)
  {
   m_fFuel = Math.Max(0, m_fFuel - dt * Math.Max(0, m_fFuelMultiplier) * (0.35 + 0.65 * Math.Max(Throttle, 0)) / 86400);
   if (m_fFuel <= 0) { m_bEngineOn = false; Throttle = 0; Replication.BumpMe(); }
  }
  if (m_fClock >= m_fNextReplication)
  {
   if (m_bTracking) m_fNextReplication = m_fClock + 0.1;
   else m_fNextReplication = m_fClock + 5;
   Replication.BumpMe();
  }
  if (m_iOperator != 0 && (!ValidLink(m_iOperator) || (m_fClock - m_fHeartbeat > 3 && m_fClock>m_ConnectionGrace))) LoseLink();
  UpdateTrack();
  if (m_iContactState == ORD_ContactState.LOST && m_fClock - m_fLastObserved > 7) { ClearContact(); Replication.BumpMe(); }
  if (!m_bAuto && m_fClock - m_fInputTime > 0.5) Hold();
  if (!m_bAuto) { m_fAltitudeTrim = 0; m_fThrottleTrim = Math.Clamp(Throttle,0.2,1); return; }
  vector position = GetOwner().GetOrigin();
  vector target = m_vOrbit;
  if (m_bPatrol && m_aRoute.Count() > 0)
  {
   if (m_iWaypoint >= m_aRoute.Count()) m_iWaypoint = 0;
   target = m_aRoute[m_iWaypoint];
   vector flat = target - position; flat[1] = 0;
   if (flat.Length() < 140) { m_iWaypoint = (m_iWaypoint + 1) % m_aRoute.Count(); Replication.BumpMe(); }
  }
  else
  {
   if (m_bReturnHome)
   {
    vector toHome = m_vHome - position; toHome[1] = 0;
    if (toHome.Length() > m_fLoiterRadius * 1.5) target = m_vHome;
    else m_bReturnHome = false;
   }
   if (!m_bReturnHome)
   {
    vector radial = position - m_vOrbit; radial[1] = 0;
    if (radial.Length() < 1) radial = GetOwner().GetTransformAxis(0) * m_fLoiterRadius;
    float angle = Math.Atan2(radial[0], radial[2]) + 0.4;
    target = m_vOrbit + Vector(Math.Sin(angle) * m_fLoiterRadius, 0, Math.Cos(angle) * m_fLoiterRadius);
   }
  }
  vector ahead = position + GetOwner().GetTransformAxis(2) * 250;
  float ground = GetOwner().GetWorld().GetSurfaceY(target[0], target[2]);
  float aheadGround = GetOwner().GetWorld().GetSurfaceY(ahead[0], ahead[2]);
  float currentGround = GetOwner().GetWorld().GetSurfaceY(position[0],position[2]);
  target[1] = Math.Max(Math.Max(ground,currentGround)+m_fAltitude,aheadGround+m_fClearance);
  vector delta = target - position;
  vector angles = GetOwner().GetAngles();
  float course = Math.Atan2(delta[0], delta[2])*Math.RAD2DEG;
  float bankFeedForward;
  float bankLimit = 45;
  float commandedSpeed = m_fCruiseSpeed;
  if (!m_bPatrol && !m_bReturnHome)
  {
   vector orbitRadial = position-m_vOrbit; orbitRadial[1]=0;
   float orbitDistance = orbitRadial.Length();
   // Fly the tangent, correcting inward/outward for radius error. A point
   // ahead on the circle alone produces an orbit much larger than requested.
   course = (Math.Atan2(orbitRadial[0],orbitRadial[2])+Math.PI*0.5+Math.Atan2((orbitDistance-m_fLoiterRadius)*1.5,m_fLoiterRadius))*Math.RAD2DEG;
   commandedSpeed = Math.Max(50,Math.Min(commandedSpeed,Math.Sqrt(9.81*m_fLoiterRadius*Math.Tan(50*Math.DEG2RAD))));
   bankLimit = 55;
   bankFeedForward = Math.Atan2(Speed()*Speed(),9.81*m_fLoiterRadius)*Math.RAD2DEG;
  }
  float headingError = course - Heading();
  while (headingError > 180) headingError -= 360;
  while (headingError < -180) headingError += 360;
  float desiredBank = Math.Clamp(bankFeedForward + headingError * 1.2, -bankLimit, bankLimit);
  Roll = Math.Clamp((desiredBank - angles[2]) * 0.045, -0.65, 0.65);
  float desiredPitch = Math.Clamp(delta[1] * 0.04, -8, 10);
  Physics flightPhysics = GetOwner().GetPhysics();
  float climbRate; if (flightPhysics) climbRate = flightPhysics.GetVelocity()[1];
  m_fAltitudeTrim = Math.Clamp(m_fAltitudeTrim+Math.Clamp(delta[1],-100,100)*dt*0.00008,-0.2,0.2);
  float turnLift = 0.3*(1/Math.Max(Math.Cos(angles[2]*Math.DEG2RAD),0.5)-1);
  Pitch = Math.Clamp(0.18+turnLift+m_fAltitudeTrim+(desiredPitch-Math.Asin(GetOwner().GetTransformAxis(2)[1])*Math.RAD2DEG)*0.055-climbRate*0.015,-0.45,0.65);
  Yaw = Math.Clamp(headingError * 0.008, -0.25, 0.25);
  if (m_bEngineOn)
  {
   m_fThrottleTrim = Math.Clamp(m_fThrottleTrim+(commandedSpeed-Speed())*dt*0.004,0.2,1);
   Throttle = Math.Clamp(m_fThrottleTrim+(commandedSpeed-Speed())*0.025,0.2,1);
  }
  else Throttle = 0;
  Brake = 0;
 }
 protected void Service()
 {
  if (!Grounded() || Speed() > 0.5 || Throttle > 0.01 || Destroyed()) { MissionResult("Service requires an intact, stopped aircraft on the ground with idle throttle"); return; }
  foreach (ORD_ServiceComponent station : ORD_ServiceComponent.Stations)
  {
   if (station && vector.Distance(station.GetOwner().GetOrigin(), GetOwner().GetOrigin()) <= station.Radius())
   { m_fFuel = 1; m_iAmmo = 1; m_bArmed = false; m_iFireStatus = ORD_FireStatus.SAFED; Brake = 1; SpawnStores(); MissionResult("Service complete - one missile, weapon safe"); return; }
  }
  MissionResult("Move the aircraft within range of a service point");
 }

 protected void FireBanderol(int targetMode = ORD_TargetMode.SENSOR_POINT, vector mapTarget = "0 0 0")
 {
  if (!m_bArmed) { SetFireStatus(ORD_FireStatus.SAFED); return; }
  if (m_iAmmo <= 0) { SetFireStatus(ORD_FireStatus.EMPTY); return; }
  if (targetMode != ORD_TargetMode.MAP_POINT && !m_bSensorMode) { SetFireStatus(ORD_FireStatus.NO_SENSOR); return; }
  if (Grounded()) { SetFireStatus(ORD_FireStatus.GROUND); return; }
  if (targetMode != ORD_TargetMode.MAP_POINT && (!m_bDesignated || m_iContactState == ORD_ContactState.LOST || m_iContactState == ORD_ContactState.TEMP_LOSS)) { SetFireStatus(ORD_FireStatus.NO_TARGET); return; }
  if (m_fClock - m_fLastLaunch < 1.5) { SetFireStatus(ORD_FireStatus.COOLDOWN); return; }
  vector target = m_vTarget;
  if (targetMode == ORD_TargetMode.MAP_POINT) target = mapTarget;
  float distance = vector.Distance(target, GetOwner().GetOrigin());
  if (distance < 100 || distance > m_fSensorRange) { SetFireStatus(ORD_FireStatus.RANGE); return; }
  Resource resource = Resource.Load(m_rBanderol);
  if (!resource || !resource.IsValid()) { SetFireStatus(ORD_FireStatus.RESOURCE); return; }
  EntitySpawnParams spawn = new EntitySpawnParams();
  spawn.TransformMode = ETransformMode.WORLD;
  spawn.Scale = 1;
  vector localSocket[4], aircraftTransform[4];
  if(!PayloadTransform(localSocket)) { SetFireStatus(ORD_FireStatus.RESOURCE); return; }
  GetOwner().GetTransform(aircraftTransform);
  Math3D.MatrixMultiply4(aircraftTransform,localSocket,spawn.Transform);
  IEntity missile = GetGame().SpawnEntityPrefab(resource, GetOwner().GetWorld(), spawn);
  if (!missile) { SetFireStatus(ORD_FireStatus.RESOURCE); return; }
  ORD_GuidedMissile logic = ORD_GuidedMissile.Cast(missile.FindComponent(ORD_GuidedMissile));
  if (!logic) { SCR_EntityHelper.DeleteEntityAndChildren(missile); SetFireStatus(ORD_FireStatus.RESOURCE); return; }
  Physics physics = GetOwner().GetPhysics();
  vector inheritedVelocity = Vector(0, 0, 0);
  if (physics) inheritedVelocity = physics.GetVelocity();
 IEntity tracked; if (targetMode == ORD_TargetMode.VEHICLE) tracked = m_TrackedEntity;
  logic.Launch(GetOwner(), target, inheritedVelocity, tracked, m_iOperator);
  if (m_StoreLeft) { SCR_EntityHelper.DeleteEntityAndChildren(m_StoreLeft); m_StoreLeft = null; }
  if (m_iAmmo == 1 && m_StoreRight) { SCR_EntityHelper.DeleteEntityAndChildren(m_StoreRight); m_StoreRight = null; }
  m_iAmmo--;
  m_fLastLaunch = m_fClock;
  SetFireStatus(ORD_FireStatus.FIRED);
 }
 protected void SetFireStatus(int status)
 {
  m_iFireStatus = status;
  Replication.BumpMe();
 }

 protected IEntity SpawnStore(Resource resource)
 {
  EntitySpawnParams spawn = new EntitySpawnParams();
  spawn.TransformMode = ETransformMode.LOCAL;
  spawn.Parent = GetOwner();
  spawn.Scale = 1;
  if(!PayloadTransform(spawn.Transform)) return null;
  IEntity store = GetGame().SpawnEntityPrefab(resource, GetOwner().GetWorld(), spawn);

  return store;
 }

 protected void SpawnStores()
 {
  Resource resource = Resource.Load(m_rBanderolStore);
  if (!resource || !resource.IsValid()) return;
  if (m_iAmmo >= 1 && !m_StoreLeft) m_StoreLeft = SpawnStore(resource);
  // No second mounted store: capacity is one in every flight and service state.
 }
}


