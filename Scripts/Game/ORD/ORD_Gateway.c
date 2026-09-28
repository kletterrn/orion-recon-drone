// Commands travel on the sender-owned player controller. Never trust a supplied player id.
modded class SCR_PlayerController
{
 protected ORD_AircraftComponent m_ORDClaimed;
 protected int m_ORDClaimRequest, m_ORDClaimResponse;
 protected RplId m_ORDClaimId = RplId.Invalid();
 int ORD_ClaimResponse() { return m_ORDClaimResponse; }
 RplId ORD_ClaimId() { return m_ORDClaimId; }
 int ORD_RequestAircraft(IEntity terminal)
 {
  m_ORDClaimRequest++; m_ORDClaimId=RplId.Invalid();
  Rpc(ORD_ClaimRPC,ORD_Id(terminal),m_ORDClaimRequest); return m_ORDClaimRequest;
 }
 void ORD_CancelAircraft(int request) { Rpc(ORD_CancelClaimRPC,request); }
 [RplRpc(RplChannel.Reliable,RplRcver.Server)]
 protected void ORD_ClaimRPC(RplId terminalId,int request)
 {
  if(!Replication.IsServer() || request<=m_ORDClaimResponse) return;
  m_ORDClaimResponse=request;
  IEntity terminal=ORD_Entity(terminalId);
  IEntity character=GetControlledEntity();
  ORD_AircraftComponent selected;
  if(terminal && character && terminal.FindComponent(ORD_TerminalComponent) && vector.Distance(character.GetOrigin(),terminal.GetOrigin())<=4 && !m_ORDClaimed)
  {
   float nearest=20000;
   foreach(ORD_AircraftComponent aircraft:ORD_AircraftComponent.Aircraft)
   {
    if(!aircraft || aircraft.Operator()!=0 || aircraft.Destroyed()) continue;
    float distance=vector.Distance(terminal.GetOrigin(),aircraft.GetOwner().GetOrigin());
    if(distance<nearest) { nearest=distance; selected=aircraft; }
   }
   if(selected)
   {
    selected.Command(GetPlayerId(),ORD_Command.CLAIM,terminal);
    if(selected.Operator()!=GetPlayerId()) selected=null;
   }
  }
  RplId result=RplId.Invalid();
  if(selected)
  {
   m_ORDClaimed=selected; result=ORD_Id(selected.GetOwner());
   ObserversSystem observers=ObserversSystem.Cast(GetGame().GetWorld().FindSystem(ObserversSystem));
   if(observers) observers.InsertObserverMP(GetRplIdentity(),0,0,selected.GetOwner());
  }
  Rpc(ORD_ClaimReplyRPC,result,request);
 }
 [RplRpc(RplChannel.Reliable,RplRcver.Owner)]
 protected void ORD_ClaimReplyRPC(RplId aircraft,int request)
 {
  if(request!=m_ORDClaimRequest) return;
  m_ORDClaimResponse=request; m_ORDClaimId=aircraft;
 }
 [RplRpc(RplChannel.Reliable,RplRcver.Server)]
 protected void ORD_CancelClaimRPC(int request)
 {
  if(request!=m_ORDClaimResponse) return;
  if(m_ORDClaimed) m_ORDClaimed.Command(GetPlayerId(),ORD_Command.RELEASE,null);
  ORD_RestoreObserver();
 }
 void ORD_RestoreObserver()
 {
  if(!Replication.IsServer() || !m_ORDClaimed) return;
  m_ORDClaimed=null;
  ObserversSystem observers=ObserversSystem.Cast(GetGame().GetWorld().FindSystem(ObserversSystem));
  if(!observers) return;
  IEntity character=GetControlledEntity();
  if(character) observers.InsertObserverMP(GetRplIdentity(),0,0,character);
  else observers.RemoveObserverMP(GetRplIdentity());
 }
 protected string m_sORDFeedback;
 protected int m_iORDMissionResponse, m_iORDAcceptedRevision;
 protected int m_iORDMissionRequest, m_iORDResponseRequest;
 int ORD_MissionRequest() { return m_iORDMissionRequest; }
 int ORD_ResponseRequest() { return m_iORDResponseRequest; }
 protected bool m_bORDMissionAccepted;
 int ORD_MissionResponse() { return m_iORDMissionResponse; }
 int ORD_AcceptedRevision() { return m_iORDAcceptedRevision; }
 bool ORD_MissionAccepted() { return m_bORDMissionAccepted; }
 [RplRpc(RplChannel.Reliable, RplRcver.Owner)]
 protected void ORD_MissionReplyRPC(bool accepted, int revision, string message, int request)
 {
  m_iORDMissionResponse++; m_bORDMissionAccepted = accepted;
  m_iORDAcceptedRevision = revision; m_sORDFeedback = message;
  m_iORDResponseRequest = request;
 }
 protected void ORD_MissionReply(bool accepted, int revision, string message, int request)
 {
  if (this == GetGame().GetPlayerController()) ORD_MissionReplyRPC(accepted, revision, message, request);
  else Rpc(ORD_MissionReplyRPC, accepted, revision, message, request);
 }
 string ORD_Feedback() { return m_sORDFeedback; }
 protected void ORD_Reply(string message)
 {
  if (this == GetGame().GetPlayerController()) ORD_FeedbackRPC(message);
  else Rpc(ORD_FeedbackRPC, message);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Owner)]
 protected void ORD_FeedbackRPC(string message) { m_sORDFeedback = message; }
 protected float m_fORDLastInput = -1000, m_fORDLastCommand = -1000, m_fORDLastAim = -1000, m_fORDLastFire = -1000;
 protected float m_fORDLastLock = -1000;
 static RplId ORD_Id(IEntity entity)
 {
  if (!entity) return RplId.Invalid();
  RplComponent rpl = RplComponent.Cast(entity.FindComponent(RplComponent));
  if (rpl) return rpl.Id();
  return RplId.Invalid();
 }
 static IEntity ORD_Entity(RplId id)
 {
  RplComponent rpl = RplComponent.Cast(Replication.FindItem(id));
  if (rpl) return rpl.GetEntity();
  return null;
 }
 void ORD_Send(IEntity drone, int command, IEntity terminal = null)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft = ORD_Local(drone); if (aircraft) aircraft.Command(GetPlayerId(), command, terminal); }
  else Rpc(ORD_CommandRPC, ORD_Id(drone), command, ORD_Id(terminal));
 }
 void ORD_Controls(IEntity drone, float pitch, float roll, float yaw, float throttle, float brake)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft = ORD_Local(drone); if (aircraft) aircraft.Input(GetPlayerId(), pitch, roll, yaw, throttle, brake); }
  else Rpc(ORD_InputRPC, ORD_Id(drone), pitch, roll, yaw, throttle, brake);
 }
 void ORD_Sensor(IEntity drone, vector direction, bool designated)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft = ORD_Local(drone); if (aircraft) aircraft.Aim(GetPlayerId(), direction, designated); }
  else Rpc(ORD_AimRPC, ORD_Id(drone), direction, designated);
 }
 void ORD_Optics(IEntity drone, vector direction, float zoom, float aspect, int channel, int sequence, bool designate = false)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft=ORD_Local(drone); if(aircraft) aircraft.Optics(GetPlayerId(),direction,zoom,aspect,channel,sequence,designate); }
  else if(designate) Rpc(ORD_LockOpticsRPC,ORD_Id(drone),direction,zoom,aspect,channel,sequence);
  else Rpc(ORD_OpticsRPC,ORD_Id(drone),direction,zoom,aspect,channel,sequence);
 }
 [RplRpc(RplChannel.Unreliable, RplRcver.Server)]
 protected void ORD_OpticsRPC(RplId id, vector direction, float zoom, float aspect, int channel, int sequence)
 {
  ORD_AircraftComponent aircraft=ORD_Find(id); if(!aircraft)return;
  float now=GetGame().GetWorld().GetWorldTime(); if(now-m_fORDLastAim<80)return; m_fORDLastAim=now;
  aircraft.Optics(GetPlayerId(),direction,zoom,aspect,channel,sequence,false);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_LockOpticsRPC(RplId id, vector direction, float zoom, float aspect, int channel, int sequence)
 {
  ORD_AircraftComponent aircraft=ORD_Find(id); if(!aircraft)return;
  float now=GetGame().GetWorld().GetWorldTime(); if(now-m_fORDLastLock<80)return; m_fORDLastLock=now;
  aircraft.Optics(GetPlayerId(),direction,zoom,aspect,channel,sequence,true);
 }
 void ORD_LockPoint(IEntity drone, vector direction)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft = ORD_Local(drone); if (aircraft) aircraft.Aim(GetPlayerId(), direction, true); }
  else Rpc(ORD_LockPointRPC, ORD_Id(drone), direction);
 }
 void ORD_FireAt(IEntity drone, vector direction)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft = ORD_Local(drone); if (aircraft) aircraft.FireAt(GetPlayerId(), direction); }
  else Rpc(ORD_FireAtRPC, ORD_Id(drone), direction);
 }
 void ORD_MapPoint(IEntity drone, vector point, bool orbit, float radius = -1)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft = ORD_Local(drone); if (aircraft) { aircraft.MapPoint(GetPlayerId(), point, orbit, radius); ORD_Reply(aircraft.MissionStatus()); } }
  else Rpc(ORD_MapRPC, ORD_Id(drone), point, orbit, radius);
 }
 void ORD_ApplyMission(IEntity drone, array<vector> points, float altitude, float speed, float radius, int revision)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  m_iORDMissionRequest++;
  if (Replication.IsServer())
  {
   ORD_AircraftComponent aircraft = ORD_Local(drone);
   if (!aircraft || !aircraft.ValidLink(GetPlayerId())) { ORD_MissionReply(false,-1,"Route rejected: you do not control this aircraft",m_iORDMissionRequest); return; }
   int previous = aircraft.MissionRevision(); aircraft.ApplyMission(GetPlayerId(),points,altitude,speed,radius,revision);
   ORD_MissionReply(aircraft.MissionRevision()!=previous,aircraft.MissionRevision(),aircraft.MissionStatus(),m_iORDMissionRequest);
  }
  else Rpc(ORD_MissionRPC, ORD_Id(drone), points, altitude, speed, radius, revision, m_iORDMissionRequest);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_MissionRPC(RplId id, array<vector> points, float altitude, float speed, float radius, int revision, int request)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft || !aircraft.ValidLink(GetPlayerId())) { ORD_MissionReply(false, -1, "Route rejected: you do not control this aircraft",request); return; }
  int previous = aircraft.MissionRevision();
  aircraft.ApplyMission(GetPlayerId(), points, altitude, speed, radius, revision);
  ORD_MissionReply(aircraft.MissionRevision() != previous, aircraft.MissionRevision(), aircraft.MissionStatus(),request);
 }
 void ORD_Weapon(IEntity drone, int mode, vector point)
 {
  if (this != SCR_PlayerController.Cast(GetGame().GetPlayerController())) return;
  if (Replication.IsServer()) { ORD_AircraftComponent aircraft = ORD_Local(drone); if (aircraft) { aircraft.WeaponRequest(GetPlayerId(),mode,point); ORD_Reply(aircraft.WeaponStatusText()); } }
  else Rpc(ORD_WeaponRPC, ORD_Id(drone), mode, point);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_WeaponRPC(RplId id, int mode, vector point)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft || !aircraft.ValidLink(GetPlayerId())) { ORD_Reply("Launch rejected: you do not control this aircraft"); return; }
  float now = GetGame().GetWorld().GetWorldTime();
  if (now - m_fORDLastFire < 100) return;
  m_fORDLastFire = now;
  aircraft.WeaponRequest(GetPlayerId(), mode, point);
  ORD_Reply(aircraft.WeaponStatusText());
 }
 protected ORD_AircraftComponent ORD_Find(RplId id)
 {
  if (!Replication.IsServer() || GetPlayerId() <= 0 || !GetControlledEntity()) return null;
  IEntity entity = ORD_Entity(id);
  if (!entity) return null;
  return ORD_AircraftComponent.Cast(entity.FindComponent(ORD_AircraftComponent));
 }
 // Offline worlds may not assign replication IDs to placed entities. The local
 // authority can use the object directly; remote requests still resolve RplIds.
 protected ORD_AircraftComponent ORD_Local(IEntity entity)
 {
  if (!Replication.IsServer() || this != GetGame().GetPlayerController() || GetPlayerId() <= 0 || !GetControlledEntity() || !entity) return null;
  return ORD_AircraftComponent.Cast(entity.FindComponent(ORD_AircraftComponent));
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_CommandRPC(RplId id, int command, RplId terminal)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft) return;
  float now = GetGame().GetWorld().GetWorldTime();
  if (command != ORD_Command.RELEASE && command != ORD_Command.HEARTBEAT && command != ORD_Command.CLEAR_TRACK)
  {
   if (now - m_fORDLastCommand < 100) return;
   m_fORDLastCommand = now;
  }
  aircraft.Command(GetPlayerId(), command, ORD_Entity(terminal));
 }
 [RplRpc(RplChannel.Unreliable, RplRcver.Server)]
 protected void ORD_InputRPC(RplId id, float pitch, float roll, float yaw, float throttle, float brake)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft) return;
  float now = GetGame().GetWorld().GetWorldTime();
  if (now - m_fORDLastInput < 30) return;
  m_fORDLastInput = now;
  aircraft.Input(GetPlayerId(), pitch, roll, yaw, throttle, brake);
 }
 [RplRpc(RplChannel.Unreliable, RplRcver.Server)]
 protected void ORD_AimRPC(RplId id, vector direction, bool designated)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft) return;
  float now = GetGame().GetWorld().GetWorldTime();
  if (now - m_fORDLastAim < 80) return;
  m_fORDLastAim = now;
  aircraft.Aim(GetPlayerId(), direction, designated);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_LockPointRPC(RplId id, vector direction)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft) return;
  float now = GetGame().GetWorld().GetWorldTime();
  if (now - m_fORDLastLock < 80) return;
  m_fORDLastLock = now;
  aircraft.Aim(GetPlayerId(), direction, true);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_FireAtRPC(RplId id, vector direction)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft) return;
  float now = GetGame().GetWorld().GetWorldTime();
  if (now - m_fORDLastFire < 100) return;
  m_fORDLastFire = now;
  aircraft.FireAt(GetPlayerId(), direction);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_MapRPC(RplId id, vector point, bool orbit, float radius)
 {
  ORD_AircraftComponent aircraft = ORD_Find(id);
  if (!aircraft || !aircraft.ValidLink(GetPlayerId())) { ORD_Reply("Loiter rejected: you do not control this aircraft"); return; }
  aircraft.MapPoint(GetPlayerId(), point, orbit, radius); ORD_Reply(aircraft.MissionStatus());
 }
}

class ORD_ServiceComponentClass : ScriptComponentClass {}
class ORD_ServiceComponent : ScriptComponent
{
 static ref array<ORD_ServiceComponent> Stations = {};
 [Attribute("20")] protected float m_fRadius;
 float Radius() { return m_fRadius; }
 override void OnPostInit(IEntity owner) { super.OnPostInit(owner); Stations.Insert(this); }
 override void OnDelete(IEntity owner) { Stations.RemoveItem(this); super.OnDelete(owner); }
}
