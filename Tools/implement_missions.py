from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'Scripts/Game/ORD/ORD_AircraftComponent.c';s=p.read_text()
s=s.replace('ARM, FIRE }','ARM, FIRE, RESUME_ROUTE }')
s='enum ORD_TargetMode { SENSOR_POINT, VEHICLE, MAP_POINT }\n'+s
s=s.replace('protected vector m_vHome, m_vOrbit;', '[RplProp()] protected vector m_vHome;\n [RplProp()] protected vector m_vOrbit;')
s=s.replace('protected int m_iWaypoint;', '[RplProp()] protected int m_iWaypoint;')
s=s.replace('protected bool m_bPatrol;', '[RplProp()] protected bool m_bPatrol;')
fields=''' [RplProp()] protected int m_iMissionRevision;
 [RplProp()] protected string m_sMissionStatus = "Ready";
 protected float m_fLastMissionRequest = -100;
'''+''.join(f' [RplProp()] protected vector m_vRoute{i};\n' for i in range(8))
s=s.replace(' float Pitch, Roll, Yaw, Throttle, Brake = 1;',fields+' float Pitch, Roll, Yaw, Throttle, Brake = 1;')
methods=''' int MissionRevision() { return m_iMissionRevision; }
 string MissionStatus() { return m_sMissionStatus; }
 int ActiveWaypoint() { return m_iWaypoint; }
 bool FlyingRoute() { return m_bPatrol && m_bAuto; }
 vector Home() { return m_vHome; }
 vector Orbit() { return m_vOrbit; }
 vector RoutePoint(int index)
 {
  switch (index)
  {
'''+''.join(f'   case {i}: return m_vRoute{i};\n' for i in range(8))+'''  }
  return vector.Zero;
 }
 protected void PublishRoute()
 {
  m_iRouteCount = m_aRoute.Count();
'''+''.join(f'  m_vRoute{i} = vector.Zero; if (m_iRouteCount > {i}) m_vRoute{i} = m_aRoute[{i}];\n' for i in range(8))+'''  m_iMissionRevision++;
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
 static vector Hardpoint(int station)
 {
  if (station == 0) return "-3.2 -0.65 0";
  return "3.2 -0.65 0";
 }
'''
s=s.replace(' int Operator()',methods+' int Operator()')
s=s.replace('case ORD_Command.RETURN_HOME:', '''case ORD_Command.RESUME_ROUTE:
    if (Grounded()) MissionResult("Airborne required - take off manually");
    else if (m_aRoute.IsEmpty()) MissionResult("Apply a route first");
    else { m_bAuto = true; m_bPatrol = true; m_bReturnHome = false; MissionResult("Route resumed"); }
    break;
   case ORD_Command.RETURN_HOME:''')
s=s.replace('case ORD_Command.PATROL:\n    if (!Grounded())','case ORD_Command.PATROL:\n    if (Grounded()) MissionResult("Airborne required - take off manually");\n    else if (m_aRoute.IsEmpty()) MissionResult("Apply a route first");\n    if (!Grounded())')
s=s.replace('m_bReturnHome = false; m_iWaypoint = 0;', 'm_bReturnHome = false; m_iWaypoint = 0; MissionResult("Repeating route");')
s=s.replace('m_iRouteCount = m_aRoute.Count();', 'm_iRouteCount = m_aRoute.Count();')
s=s.replace('case ORD_Command.CLEAR_ROUTE: m_aRoute.Clear(); m_iRouteCount = 0; m_iWaypoint = 0; Hold(); break;', 'case ORD_Command.CLEAR_ROUTE: m_aRoute.Clear(); m_iWaypoint = 0; Hold(); PublishRoute(); MissionResult("Route cleared - holding"); break;')
s=s.replace('  Replication.BumpMe();\n }\n void Input', '  PublishRoute();\n }\n void Input') # existing keyboard route changes also synchronize
s=s.replace('if (flat.Length() > m_fLinkRange || (!orbit && m_aRoute.Count() >= 8)) return;', 'if (!ValidMapPoint(requested) || (!orbit && m_aRoute.Count() >= 8)) { MissionResult("Invalid map point"); return; }\n  if (orbit && Grounded()) { MissionResult("Airborne required for loiter"); return; }')
s=s.replace('if (orbit) { Hold(); m_vOrbit = point; }', 'if (orbit) { Hold(); m_vOrbit = point; MissionResult("Loiter active - Resume route to continue"); }')
s=s.replace('  Replication.BumpMe();\n }\n protected void Hold()', '  PublishRoute();\n }\n protected void Hold()')
s=s.replace('if (flat.Length() < 140) m_iWaypoint = (m_iWaypoint + 1) % m_aRoute.Count();', 'if (flat.Length() < 140) { m_iWaypoint = (m_iWaypoint + 1) % m_aRoute.Count(); Replication.BumpMe(); }')
s=s.replace('protected void FireBanderol()', 'protected void FireBanderol(int targetMode = ORD_TargetMode.SENSOR_POINT, vector mapTarget = "0 0 0")')
# Only the launch method allows map attacks without sensor designation.
start=s.index(' protected void FireBanderol(');part=s[start:]
part=part.replace('if (!m_bSensorMode)', 'if (targetMode != ORD_TargetMode.MAP_POINT && !m_bSensorMode)',1)
part=part.replace('if (!m_bDesignated || m_iContactState == ORD_ContactState.LOST || m_iContactState == ORD_ContactState.TEMP_LOSS)', 'if (targetMode != ORD_TargetMode.MAP_POINT && (!m_bDesignated || m_iContactState == ORD_ContactState.LOST || m_iContactState == ORD_ContactState.TEMP_LOSS))',1)
part=part.replace('vector target = m_vTarget;', 'vector target = m_vTarget;\n  if (targetMode == ORD_TargetMode.MAP_POINT) target = mapTarget;',1)
part=part.replace('spawn.Scale = 2.95;', 'spawn.Scale = 1;')
part=part.replace('float side = -3.2;\n  if (m_iAmmo == 1) side = 3.2;', 'int station = 0;\n  if (m_iAmmo == 1) station = 1;')
part=part.replace('Vector(side, -0.95, 0)', 'Hardpoint(station)')
part=part.replace('missile.SetAngles(GetOwner().GetAngles() + Vector(0, -90, 0));', 'missile.SetAngles(GetOwner().GetAngles());')
part=part.replace('logic.Launch(GetOwner(), target, inheritedVelocity);', 'IEntity tracked; if (targetMode == ORD_TargetMode.VEHICLE) tracked = m_TrackedEntity;\n  logic.Launch(GetOwner(), target, inheritedVelocity, tracked, m_iOperator);')
part=part.replace('spawn.TransformMode = ETransformMode.WORLD;\n  spawn.Parent = GetOwner();', 'spawn.TransformMode = ETransformMode.LOCAL;\n  spawn.Parent = GetOwner();')
part=part.replace('GetOwner().GetTransform(spawn.Transform);\n  spawn.Transform[3] = GetOwner().CoordToParent(Vector(side, -0.2, 0));','Math3D.MatrixIdentity4(spawn.Transform);\n  int station = 0; if (side > 0) station = 1;\n  spawn.Transform[3] = Hardpoint(station);')
part=part.replace('  if (store) store.SetAngles(GetOwner().GetAngles() + Vector(0, -90, 0));','')
s=s[:start]+part;p.write_text(s)

p=R/'Scripts/Game/ORD/ORD_Gateway.c';s=p.read_text();at=s.index(' protected ORD_AircraftComponent ORD_Find')
s=s[:at]+''' void ORD_ApplyMission(IEntity drone, array<vector> points, float altitude, float speed, float radius, int revision)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) ORD_MissionRPC(ORD_Id(drone), points, altitude, speed, radius, revision);
  else Rpc(ORD_MissionRPC, ORD_Id(drone), points, altitude, speed, radius, revision);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_MissionRPC(RplId id, array<vector> points, float altitude, float speed, float radius, int revision)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (aircraft) aircraft.ApplyMission(GetPlayerId(), points, altitude, speed, radius, revision);
 }
 void ORD_Weapon(IEntity drone, int mode, vector point)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) ORD_WeaponRPC(ORD_Id(drone), mode, point);
  else Rpc(ORD_WeaponRPC, ORD_Id(drone), mode, point);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_WeaponRPC(RplId id, int mode, vector point)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft) return;
  float now = GetGame().GetWorld().GetWorldTime();
  if (now - m_fORDLastFire < 100) return;
  m_fORDLastFire = now;
  aircraft.WeaponRequest(GetPlayerId(), mode, point);
 }
'''+s[at:];p.write_text(s)
