class ORD_OperateAction : ScriptedUserAction
{
 override bool GetActionNameScript(out string outName) { outName = "Operate Orion UAV"; return true; }
 override bool HasLocalEffectOnlyScript() { return true; }
 override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)
 {
  ORD_TerminalComponent terminal = ORD_TerminalComponent.Cast(pOwnerEntity.FindComponent(ORD_TerminalComponent));
  if (terminal) terminal.Open();
 }
}
class ORD_TerminalComponentClass : ScriptComponentClass {}
class ORD_TerminalComponent : ScriptComponent
{
 protected static ORD_TerminalComponent s_RemoteSession;
 [Attribute("0")] protected bool m_LocalSession;
 protected int m_ClaimRequest;
 protected bool m_FarObserver, m_DeleteScheduled;
 [Attribute("20000")] protected float m_fSearchRadius;
 [Attribute("0")] protected bool m_bDiagnostics;
 [Attribute("", UIWidgets.ResourceNamePicker, "Operator HUD", "layout")] protected ResourceName m_rHUD;
 [Attribute("", UIWidgets.ResourceNamePicker, "External white-hot material", "emat")] protected ResourceName m_rWhite;
 [Attribute("", UIWidgets.ResourceNamePicker, "External black-hot material", "emat")] protected ResourceName m_rBlack;
 protected ORD_AircraftComponent m_Drone;
 protected ORD_AudioPresentation m_OperatorFeed;
 protected SCR_CameraBase m_Camera;
 protected Widget m_HUD;
 protected ref ORD_SensorHUD m_SensorHUD;
 protected ref ORD_ThermalController m_Thermal;
 protected float m_ThermalErrorUntil;
 protected TextWidget m_TopLeft, m_HeadingTape, m_TopRight, m_PitchValue, m_ZoomReadout;
 protected TextWidget m_Reticle, m_ReticleVertical, m_TrackBox, m_CenterStatus;
 protected TextWidget m_BottomLeft, m_BottomCenter, m_BottomRight, m_ControlHint;
 protected TextWidget m_MapStatus, m_MapCursor;
 protected bool m_bPending, m_bActive, m_bPilot = true, m_bMap, m_bInputMissing, m_bAutoRequested, m_bBoxesEnabled = true, m_bUnlockPending;
 protected int m_iLastInputTick;
 protected float m_ResolvedYaw, m_ResolvedPitch, m_YawVelocity, m_PitchVelocity;
 protected bool m_PoseReady, m_GimbalLimited, m_QueueDesignation, m_QueueFire, m_QueueOptics;
 protected float m_ObservationStamp = -1, m_ObservationAge, m_ObservationInterval = 0.1;
 protected vector m_PreviousObservation, m_CurrentObservation;
 protected int m_iWeaponMode = ORD_TargetMode.SENSOR_POINT;
 protected float m_fPendingTime, m_fHeartbeat, m_fSend, m_fThrottle, m_fYaw, m_fPitch = -20, m_fZoom = 1, m_fMapZoom = 1, m_fFeedTime, m_fAutoRequestTime;
 protected int m_iSensor, m_iAppliedSensor = -1;
 protected vector m_vMapCenter;
 protected CharacterControllerComponent m_Character;
 protected bool m_bPreviousMovement, m_bPreviousWeapons;
 protected bool m_bInputProbeDone;
 protected float m_fInputProbeTime;
 protected float m_fContactScan, m_fContactCos;
 protected vector m_vContactOrigin, m_vContactForward;
 protected ref array<IEntity> m_aContactCandidates = {};
 protected ref array<float> m_ContactScores = {};
 protected ref array<ref ORD_LocalObservation> m_Observations = {};
 protected float m_ContactAspect = 1.77778;
 protected int m_ContactCursor, m_OpticsSequence;
 protected ref array<Widget> m_aContactWidgets = {};
 protected ref array<Widget> m_aMapWidgets = {};
 protected ref array<vector> m_aMapPoints = {};
 protected vector m_vMapOrbit;
 protected bool m_bMapOrbit;
 protected ref ORD_MissionMap m_MissionMap;
 protected ref map<string, bool> m_Keys = new map<string, bool>();

 override void OnPostInit(IEntity owner)
 {
  super.OnPostInit(owner);
  SetEventMask(owner, EntityEvent.FRAME);
  if (m_bDiagnostics && GetGame() && GetGame().GetInputManager())
  {
   InputManager input = GetGame().GetInputManager();
   bool foundEngine;
   for (int i = 0; i < input.GetActionCount(); i++)
   {
    if (input.GetActionName(i) == "ORD_Engine") { foundEngine = true; break; }
   }
   bool operatorContext = input.ActivateContext("ORD_OperatorContext");
   bool flightContext = input.ActivateContext("ORD_FlightContext");
   bool sensorContext = input.ActivateContext("ORD_SensorContext");
   Print(string.Format("ORD terminal startup input: engine registered=%1 actions=%2 contexts=%3/%4/%5", foundEngine, input.GetActionCount(), operatorContext, flightContext, sensorContext));
  }
 }
 override void OnDelete(IEntity owner) { if (m_bActive || m_bPending) Close(); super.OnDelete(owner); }
 void Open()
 {
  if (s_RemoteSession) { s_RemoteSession.Close(); return; }
  if (m_bActive || m_bPending) { Close(); return; }
  if(!Replication.IsServer() && !m_LocalSession)
  {
   IEntity session=GetGame().SpawnEntityPrefab(Resource.Load("Prefabs/ORD/ORD_OperatorSession.et"),GetOwner().GetWorld());
   if(!session) return;
   s_RemoteSession=ORD_TerminalComponent.Cast(session.FindComponent(ORD_TerminalComponent));
   if(s_RemoteSession) s_RemoteSession.BeginRemote(GetOwner());
   return;
  }
  SCR_PlayerController player = SCR_PlayerController.Cast(GetGame().GetPlayerController());
  if (!player) return;
  float nearest = m_fSearchRadius;
  foreach (ORD_AircraftComponent candidate : ORD_AircraftComponent.Aircraft)
  {
   if (!candidate || candidate.Operator() != 0 || candidate.Destroyed()) continue;
   float distance = vector.Distance(candidate.GetOwner().GetOrigin(), GetOwner().GetOrigin());
   if (distance < nearest) { nearest = distance; m_Drone = candidate; }
  }
  if (!m_Drone) return;
  m_bPending = true; m_fPendingTime = 0;
  player.ORD_Send(m_Drone.GetOwner(), ORD_Command.CLAIM, GetOwner());
 }
 void BeginRemote(IEntity terminal)
 {
  SCR_PlayerController player=SCR_PlayerController.Cast(GetGame().GetPlayerController());
  if(!player) { Close(); return; }
  m_bPending=true; m_fPendingTime=0;
  m_ClaimRequest=player.ORD_RequestAircraft(terminal);
  m_HUD=GetGame().GetWorkspace().CreateWidgets(m_rHUD);
  m_CenterStatus=HudText("CenterStatus");
  if(m_CenterStatus) m_CenterStatus.SetText("CONNECTING TO AIRCRAFT...");
 }
 protected bool Pressed(InputManager input, string action)
 {
  bool down = input.GetActionValue(action) > 0.5;
  bool previous = m_Keys.Get(action); m_Keys.Set(action, down);
  return down && !previous;
 }
 protected TextWidget HudText(string name)
 {
  if (!m_HUD) return null;
  TextWidget widget = TextWidget.Cast(m_HUD.FindAnyWidget(name));
  if (widget) widget.SetOutline(1, 0xFF000000);
  return widget;
 }
 protected bool Start()
 {
  m_Camera = SCR_CameraBase.Cast(GetGame().SpawnEntity(ORD_OpticalCamera, GetOwner().GetWorld()));
  if (!m_Camera) return false;
  ORD_OpticalCamera.Cast(m_Camera).Bind(this);
  ChimeraGame game = ChimeraGame.Cast(GetGame());
  if (!game || !game.GetCameraManager() || !game.GetCameraManager().SetCamera(m_Camera)) return false;
  m_HUD = GetGame().GetWorkspace().CreateWidgets(m_rHUD);
  if (!m_HUD) { game.GetCameraManager().SetPreviousCamera(); return false; }
  m_Thermal = new ORD_ThermalController();
  m_SensorHUD = new ORD_SensorHUD();
  if (!m_SensorHUD.Open()) { game.GetCameraManager().SetPreviousCamera(); return false; }
  m_TopLeft = HudText("TopLeft"); m_HeadingTape = HudText("HeadingTape"); m_TopRight = HudText("TopRight");
  m_ZoomReadout = HudText("ZoomReadout");
  m_PitchValue = HudText("PitchValue"); m_Reticle = HudText("Reticle"); m_ReticleVertical = HudText("ReticleVertical");
  m_TrackBox = HudText("TrackBox"); m_CenterStatus = HudText("CenterStatus");
  m_BottomLeft = HudText("BottomLeft"); m_BottomCenter = HudText("BottomCenter");
  m_BottomRight = HudText("BottomRight"); m_ControlHint = HudText("ControlHint");
  m_MapStatus = HudText("MapStatus"); m_MapCursor = HudText("MapCursor");
  for (int contactIndex = 0; contactIndex < 9; contactIndex++)
  {
   Widget contactWidget = GetGame().GetWorkspace().CreateWidgets("{59A370ECB6924FD3}UI/ORD/Contact.layout");
   if (!contactWidget) break;
   contactWidget.SetVisible(false);
   m_aContactWidgets.Insert(contactWidget);
  }
  for (int mapIndex = 0; mapIndex < 9; mapIndex++)
  {
   Widget marker = GetGame().GetWorkspace().CreateWidgets("{59A370ECB6924FD3}UI/ORD/Contact.layout");
   if (!marker) break;
   marker.SetVisible(false);
   m_aMapWidgets.Insert(marker);
  }
  m_bActive = true; m_bPilot = !m_Drone.SensorMode(); m_fYaw = m_Drone.Heading();
  AudioSystem.PlaySound("{68077215888B092C}Sounds/ORD/ORD_LinkOpen.wav");
  InputManager input = game.GetInputManager();
  bool foundEngine, foundZoomIn, foundZoomOut, foundZoomWheel, foundWheelOut;
  for (int i = 0; i < input.GetActionCount(); i++)
  {
   if (input.GetActionName(i) == "ORD_Engine") { foundEngine = true; break; }
  }
  for (int j = 0; j < input.GetActionCount(); j++)
  {
   if (input.GetActionName(j) == "ORD_ZoomIn") foundZoomIn = true;
   if (input.GetActionName(j) == "ORD_ZoomOut") foundZoomOut = true;
   if (input.GetActionName(j) == "ORD_ZoomWheelOut") foundWheelOut = true;
   if (input.GetActionName(j) == "ORD_ZoomWheelIn") foundZoomWheel = true;
  }
  m_bInputMissing = !foundEngine || !foundZoomIn || !foundZoomOut || !foundZoomWheel || !foundWheelOut;
  Print(string.Format("ORD terminal input: engine=%1 zoom key=%2 zoom wheel=%3 actions=%4", foundEngine, foundZoomIn, foundZoomWheel, input.GetActionCount()));
  IEntity controlled = GetGame().GetPlayerController().GetControlledEntity();
  if (controlled) m_Character = CharacterControllerComponent.Cast(controlled.FindComponent(CharacterControllerComponent));
  if (m_Character)
  {
   m_bPreviousMovement = m_Character.GetDisableMovementControls();
   m_bPreviousWeapons = m_Character.GetDisableWeaponControls();
   m_Character.SetDisableMovementControls(true);
   m_Character.SetDisableWeaponControls(true);
  }
  ResetZoomInput(); m_fZoom = 1; m_fPitch = -20; m_iWeaponMode = ORD_TargetMode.SENSOR_POINT;
  m_fThrottle = 0; m_fHeartbeat = 0; m_fSend = 0; m_fFeedTime = 0; m_fContactScan = 0; m_iSensor = 0; m_iAppliedSensor = -1; m_bMap = false; m_fMapZoom = 1; m_bMapOrbit = false; m_aMapPoints.Clear(); m_bAutoRequested = false; m_bBoxesEnabled = true; m_bUnlockPending = false;
  return true;
 }
 // Onboard microphone mix is intentionally local to the connected operator.
 protected vector CameraAnchor(IEntity aircraft,string name,vector fallback)
 {
  vector marker[4];
  if (ORD_RC8Rig.Socket(aircraft,name,marker))
   return marker[3];
  return fallback;
 }
 protected void UpdateEngineAudio()
 {
  ORD_AudioPresentation next;
  if(m_Drone && m_Drone.GetOwner()) next=ORD_AudioPresentation.Cast(m_Drone.GetOwner().FindComponent(ORD_AudioPresentation));
  if(next!=m_OperatorFeed)
  {
   if(m_OperatorFeed)m_OperatorFeed.SetOperatorFeed(false);
   m_OperatorFeed=next;
  }
  if(m_OperatorFeed)m_OperatorFeed.SetOperatorFeed(true);
 }
 void Close()
 {
  CloseMissionMap();
  if(m_Thermal) m_Thermal.Clear();
  m_Thermal=null;
  ResetZoomInput();
  if(m_OperatorFeed)m_OperatorFeed.SetOperatorFeed(false);
  m_OperatorFeed=null;
  if (m_bActive) AudioSystem.PlaySound("{7EEB78418155F733}Sounds/ORD/ORD_LinkClose.wav");
  ChimeraGame game = ChimeraGame.Cast(GetGame());
  SCR_PlayerController player;
  if (game) player = SCR_PlayerController.Cast(game.GetPlayerController());
  if(player && m_LocalSession) player.ORD_CancelAircraft(m_ClaimRequest);
  if(m_FarObserver && game) { ObserversSystem observers=ObserversSystem.Cast(game.GetWorld().FindSystem(ObserversSystem)); if(observers) observers.DelFarObserver(); m_FarObserver=false; }
  if (player && m_Drone && m_Drone.GetOwner()) player.ORD_Send(m_Drone.GetOwner(), ORD_Command.RELEASE);
  if (m_bActive)
  {
   World world;
   if (GetOwner()) world = GetOwner().GetWorld();
   if (game && game.GetCameraManager()) game.GetCameraManager().SetPreviousCamera();
  }
  if (m_Camera && m_Camera.GetWorld()) SCR_EntityHelper.DeleteEntityAndChildren(m_Camera);
  if (m_Character)
  {
   m_Character.SetDisableMovementControls(m_bPreviousMovement);
   m_Character.SetDisableWeaponControls(m_bPreviousWeapons);
   m_Character = null;
  }
  if (m_HUD) m_HUD.RemoveFromHierarchy();
  if (m_SensorHUD) m_SensorHUD.Close();
  m_SensorHUD = null;
  foreach (Widget contactWidget : m_aContactWidgets) if (contactWidget) contactWidget.RemoveFromHierarchy();
  foreach (Widget mapWidget : m_aMapWidgets) if (mapWidget) mapWidget.RemoveFromHierarchy();
  m_aContactWidgets.Clear(); m_aContactCandidates.Clear(); m_Observations.Clear(); m_ContactScores.Clear();
  m_aMapWidgets.Clear(); m_aMapPoints.Clear();
  m_Camera = null; m_HUD = null; m_Drone = null;
  m_TopLeft = null; m_HeadingTape = null; m_TopRight = null; m_PitchValue = null; m_ZoomReadout = null;
  m_Reticle = null; m_ReticleVertical = null; m_TrackBox = null; m_CenterStatus = null;
  m_BottomLeft = null; m_BottomCenter = null; m_BottomRight = null; m_ControlHint = null; m_MapStatus = null; m_MapCursor = null;
  if(s_RemoteSession==this) s_RemoteSession=null;
  if(m_LocalSession && !m_DeleteScheduled) { m_DeleteScheduled=true; GetGame().GetCallqueue().CallLater(DeleteSession,1,false); }
  m_bActive = false; m_bPending = false; m_bMap = false; m_bAutoRequested = false; m_bUnlockPending = false; m_iAppliedSensor = -1; m_Keys.Clear();
 }
 protected void DeleteSession() { if(GetOwner()) SCR_EntityHelper.DeleteEntityAndChildren(GetOwner()); }
 override void EOnFrame(IEntity owner, float timeSlice)
 {
  if (m_bDiagnostics && !m_bInputProbeDone)
  {
   m_fInputProbeTime += timeSlice;
   if (m_fInputProbeTime > 8)
   {
    m_bInputProbeDone = true;
    InputManager probe = GetGame().GetInputManager();
    Print(string.Format("ORD terminal active input contexts: character=%1 operator=%2 flight=%3 sensor=%4", probe.ActivateContext("CharacterGeneralContext"), probe.ActivateContext("ORD_OperatorContext"), probe.ActivateContext("ORD_FlightContext"), probe.ActivateContext("ORD_SensorContext")));
   }
  }
  if (!m_bPending && !m_bActive) return;
  SCR_PlayerController player = SCR_PlayerController.Cast(GetGame().GetPlayerController());
  if (!player) { Close(); return; }
  if (m_bPending)
  {
   m_fPendingTime += timeSlice;
   if(m_LocalSession && player.ORD_ClaimResponse()==m_ClaimRequest)
   {
    IEntity resolved=SCR_PlayerController.ORD_Entity(player.ORD_ClaimId());
    if(resolved) m_Drone=ORD_AircraftComponent.Cast(resolved.FindComponent(ORD_AircraftComponent));
   }
   if (m_Drone && m_Drone.Operator() == player.GetPlayerId())
   {
    m_bPending = false; if(m_HUD) m_HUD.RemoveFromHierarchy(); m_HUD=null;
    if (!Start()) Close();
   }
   else if (m_fPendingTime > 15) Close();
   return;
  }
  if (!m_Drone || m_Drone.Operator() != player.GetPlayerId() || m_Drone.Destroyed()) { Close(); return; }
  if(m_Character && (player.GetControlledEntity()!=m_Character.GetOwner() || m_Character.IsDead())) { Close(); return; }
  m_fFeedTime += timeSlice;
  bool wasPilot = m_bPilot;
  m_bPilot = !m_Drone.SensorMode();
  if (wasPilot != m_bPilot) ResetZoomInput();
  UpdateEngineAudio();
  InputManager input = GetGame().GetInputManager();
  int inputTick = System.GetTickCount();
  if (m_iLastInputTick > 0 && inputTick - m_iLastInputTick > 250) { ResetZoomInput(); m_Keys.Clear(); }
  m_iLastInputTick = inputTick;
  bool operatorContext = input.ActivateContext("ORD_OperatorContext");
  bool modeContext;
  if (m_bMap) modeContext = true; // Native map owns its mouse and wheel bindings.
  else if (m_bPilot) modeContext = input.ActivateContext("ORD_FlightContext");
  else modeContext = input.ActivateContext("ORD_SensorContext");
  if ((!operatorContext || !modeContext) && !m_bInputMissing)
  {
   m_bInputMissing = true;
   Print(string.Format("ORD terminal input context missing: operator=%1 mode=%2", operatorContext, modeContext), LogLevel.ERROR);
  }
  if (!m_bMap) { input.ActivateAction("ORD_MouseYaw"); input.ActivateAction("ORD_MousePitch"); }
  if (Pressed(input, "ORD_Exit")) { if (m_bMap) CloseMissionMap(); else Close(); return; }
  IEntity drone = m_Drone.GetOwner();
  m_fHeartbeat += timeSlice;
  if (m_fHeartbeat >= 1) { m_fHeartbeat = 0; player.ORD_Send(drone, ORD_Command.HEARTBEAT); }
  if (Pressed(input, "ORD_Mode"))
  {
   CloseMissionMap(); ResetZoomInput();
   if (m_bPilot) player.ORD_Send(drone, ORD_Command.SENSOR);
   else player.ORD_Send(drone, ORD_Command.PILOT);
  }
  if (Pressed(input, "ORD_Map"))
  {
   ResetZoomInput();
   if (m_bMap) CloseMissionMap();
   else
   {
    m_MissionMap = new ORD_MissionMap();
    m_bMap = m_MissionMap.Open(m_Drone);
    if (m_bMap) player.ORD_Send(drone, ORD_Command.SENSOR);
   }
  }
  if (Pressed(input, "ORD_Service")) player.ORD_Send(drone, ORD_Command.SERVICE);
  if (Pressed(input, "ORD_Patrol")) { player.ORD_Send(drone, ORD_Command.PATROL); m_bAutoRequested = true; m_fAutoRequestTime = m_fFeedTime; }
  if (Pressed(input, "ORD_Return")) { player.ORD_Send(drone, ORD_Command.RETURN_HOME); m_bAutoRequested = true; m_fAutoRequestTime = m_fFeedTime; }
  if (Pressed(input, "ORD_Engine")) player.ORD_Send(drone, ORD_Command.ENGINE);
  if (Pressed(input, "ORD_ClearRoute")) { player.ORD_Send(drone, ORD_Command.CLEAR_ROUTE); m_aMapPoints.Clear(); }
  if (m_bPilot && Pressed(input, "ORD_AltUp")) player.ORD_Send(drone, ORD_Command.ALT_UP);
  if (m_bPilot && Pressed(input, "ORD_AltDown")) player.ORD_Send(drone, ORD_Command.ALT_DOWN);
  if (m_bPilot && Pressed(input, "ORD_SpeedUp")) player.ORD_Send(drone, ORD_Command.SPEED_UP);
  if (m_bPilot && Pressed(input, "ORD_SpeedDown")) player.ORD_Send(drone, ORD_Command.SPEED_DOWN);
  if (Pressed(input, "ORD_RadiusUp")) player.ORD_Send(drone, ORD_Command.RADIUS_UP);
  if (Pressed(input, "ORD_RadiusDown")) player.ORD_Send(drone, ORD_Command.RADIUS_DOWN);
  if((m_bMap || m_bPilot) && m_FarObserver)
  {
   ObserversSystem observers=ObserversSystem.Cast(GetGame().GetWorld().FindSystem(ObserversSystem));
   if(observers) observers.DelFarObserver(); m_FarObserver=false;
  }
  if (m_bMap)
  {
   if (m_HUD) m_HUD.SetVisible(false);
   if (m_SensorHUD) m_SensorHUD.SetVisible(false);
   if (m_MissionMap && m_MissionMap.IsOpen()) m_MissionMap.Update(timeSlice);
   else CloseMissionMap();
   HideContacts();
   return;
  }
  else if (m_bPilot) m_fThrottle = Math.Clamp(m_fThrottle + (input.GetActionValue("ORD_ThrottleUp") - input.GetActionValue("ORD_ThrottleDown")) * timeSlice * 0.3, 0, 1);
  else
  {
   float mouseX = input.GetActionValue("ORD_MouseYaw");
   float mouseY = input.GetActionValue("ORD_MousePitch");
   // Relative movement is a delta, never a held rotation command.
   input.ResetAction("ORD_MouseYaw"); input.ResetAction("ORD_MousePitch");
   if (Math.AbsFloat(mouseX) <= 0.001) mouseX = 0;
   if (Math.AbsFloat(mouseY) <= 0.001) mouseY = 0;
   // Screen-direction controls: right increases bearing; up raises elevation.
   float panX = Math.AbsFloat(input.GetActionValue("ORD_CamRight")) - Math.AbsFloat(input.GetActionValue("ORD_CamLeft"));
   float panY = Math.AbsFloat(input.GetActionValue("ORD_CamUp")) - Math.AbsFloat(input.GetActionValue("ORD_CamDown"));
   if (Math.AbsFloat(panX) <= 0.1) panX = 0;
   if (Math.AbsFloat(panY) <= 0.1) panY = 0;
   bool manualAim = Math.AbsFloat(mouseX) > 0.001 || Math.AbsFloat(mouseY) > 0.001 || Math.AbsFloat(panX) > 0.1 || Math.AbsFloat(panY) > 0.1;
   if (!m_Drone.Designated()) m_bUnlockPending = false;
   bool locked = m_Drone.PointLocked() || m_Drone.Tracking() || m_Drone.ContactState() == ORD_ContactState.LOST;
   if (locked && manualAim && !m_bUnlockPending) { m_fYaw=m_ResolvedYaw; m_fPitch=m_ResolvedPitch; player.ORD_Send(drone, ORD_Command.CLEAR_TRACK); m_bUnlockPending = true; }
   if (m_bUnlockPending) locked = false;
   if (!locked)
   {
    float aimScale = 1 / m_fZoom;
    m_fYaw += (mouseX * 0.12 + panX * timeSlice * 55) * aimScale;
    m_fPitch = Math.Clamp(m_fPitch - mouseY * 0.12 * aimScale + panY * timeSlice * 55 * aimScale, -89, 75);
   }
   if (m_fYaw > 180) m_fYaw -= 360; if (m_fYaw < -180) m_fYaw += 360;
   m_fZoom = ORD_SensorZoom.Step(m_fZoom,input.GetActionValue("ORD_ZoomIn"),input.GetActionValue("ORD_ZoomOut"),input.GetActionValue("ORD_ZoomWheelIn"),input.GetActionValue("ORD_ZoomWheelOut"),timeSlice);
   input.ResetAction("ORD_ZoomWheelIn"); input.ResetAction("ORD_ZoomWheelOut");
   if (Pressed(input, "ORD_Thermal"))
   {
    m_iSensor = (m_iSensor + 1) % 3;
   }
   if (Pressed(input, "ORD_Designate"))
   {
    if (m_Drone.Designated()) { player.ORD_Send(drone, ORD_Command.CLEAR_TRACK); m_bUnlockPending = true; }
    else m_QueueDesignation = true;
   }
   if (Pressed(input, "ORD_Boxes")) m_bBoxesEnabled = !m_bBoxesEnabled;
   if (Pressed(input, "ORD_Track"))
   {
    if (m_Drone.Tracking()) { player.ORD_Send(drone, ORD_Command.CLEAR_TRACK); m_bUnlockPending = true; }
    else player.ORD_Send(drone, ORD_Command.TRACK);
   }
   if (Pressed(input, "ORD_Group")) player.ORD_Send(drone, ORD_Command.GROUP_TRACK);
   if (Pressed(input, "ORD_Recenter"))
   {
    player.ORD_Send(drone, ORD_Command.CLEAR_TRACK); m_bUnlockPending = true;
    m_fYaw = m_Drone.Heading(); m_fPitch = -20;
   }
   if (Pressed(input, "ORD_Arm")) player.ORD_Send(drone, ORD_Command.ARM);
   if (Pressed(input, "ORD_TargetMode"))
   {
    if (m_iWeaponMode == ORD_TargetMode.SENSOR_POINT) m_iWeaponMode = ORD_TargetMode.VEHICLE;
    else m_iWeaponMode = ORD_TargetMode.SENSOR_POINT;
   }
   if (Pressed(input, "ORD_Fire"))
   {
    m_QueueFire = true;
   }
   if (Pressed(input, "ORD_QueuePoint")) player.ORD_Send(drone, ORD_Command.QUEUE_POINT);
   if (Pressed(input, "ORD_Loiter")) player.ORD_Send(drone, ORD_Command.LOITER);
  }
  int desiredEffect = 0;
  if (!m_bPilot && !m_bMap) desiredEffect = m_iSensor;
  if(m_Thermal) m_iAppliedSensor=m_Thermal.Update(owner.GetWorld(),m_Camera.GetCameraIndex(),desiredEffect,m_rWhite,m_rBlack,m_fZoom);
  if(m_Thermal && m_Thermal.Fallback) { m_iSensor=0; m_ThermalErrorUntil=m_fFeedTime+5; }
  float width, height; GetGame().GetWorkspace().GetScreenSize(width, height);
  float horizontalFOV = 60;
  if (m_bMap) horizontalFOV = 60 / m_fMapZoom;
  else if (!m_bPilot) horizontalFOV = 2 * Math.Atan2(Math.Tan(30 * Math.DEG2RAD) / m_fZoom, 1) * Math.RAD2DEG;
  float aspect = width / Math.Max(height, 1);
  m_Camera.SetFOVDegree(2 * Math.Atan2(Math.Tan(horizontalFOV * Math.DEG2RAD * 0.5), aspect) * Math.RAD2DEG);
  UpdateMapMarkers();
  if (m_HUD) m_HUD.SetVisible(m_bPilot);
  if (m_SensorHUD) m_SensorHUD.SetVisible(!m_bPilot);
  m_fContactScan += timeSlice;
  if (m_bPilot || m_bMap) { HideContacts(); m_Observations.Clear(); }
  else if (m_fContactScan >= 0.1) { m_fContactScan = 0; UpdateContacts(horizontalFOV, aspect); }

  m_fSend += timeSlice;
  if (m_fSend >= 0.1)
  {
   m_fSend = 0;
   if (!m_bPilot) m_QueueOptics = true;
   float pitchInput = input.GetActionValue("ORD_Pitch");
   float rollInput = input.GetActionValue("ORD_Roll");
   float yawInput = input.GetActionValue("ORD_Yaw");
   float brakeInput = input.GetActionValue("ORD_Brake");
   bool manualTakeover = Math.AbsFloat(pitchInput) > 0.05 || Math.AbsFloat(rollInput) > 0.05 || Math.AbsFloat(yawInput) > 0.05 || brakeInput > 0.05 || input.GetActionValue("ORD_ThrottleUp") > 0.05 || input.GetActionValue("ORD_ThrottleDown") > 0.05;
   if (manualTakeover) m_bAutoRequested = false;
   if (m_bAutoRequested && m_fFeedTime - m_fAutoRequestTime > 3) m_bAutoRequested = false;
   if (m_bPilot && ((!m_Drone.Automatic() && !m_bAutoRequested) || manualTakeover)) player.ORD_Controls(drone, pitchInput, rollInput, yawInput, m_fThrottle, brakeInput);
   UpdateHUD(drone);
  }
 }
 // Resolve once after physics. Aircraft-motion compensation is never damped.
 void UpdateOpticalPose(float timeSlice = 0.016667)
 {
  if (!m_bActive || !m_Drone || !m_Camera || m_bMap) return;
  IEntity drone=m_Drone.GetOwner();
  if(m_bPilot)
  {
   vector pilot[4]; drone.GetTransform(pilot); pilot[3]=ORD_CameraMounts.PilotOrigin(drone);
   m_Camera.SetTransform(pilot); m_PoseReady=false; return;
  }
  if(!m_PoseReady) { m_ResolvedYaw=m_fYaw; m_ResolvedPitch=m_fPitch; m_PoseReady=true; }
  bool locked=m_Drone.Designated() && !m_bUnlockPending;
  vector requested;
  if(locked)
  {
   vector target=m_Drone.Target();
   // Interpolate only fresh observed positions; freeze immediately on loss.
   if(m_Drone.Tracking() && m_Drone.ContactState()!=ORD_ContactState.TEMP_LOSS)
   {
    float stamp=m_Drone.ObservedTime();
    if(stamp!=m_ObservationStamp)
    {
     m_PreviousObservation=m_CurrentObservation;
     if(m_ObservationStamp<0) m_PreviousObservation=target;
     m_ObservationInterval=Math.Clamp(stamp-m_ObservationStamp,0.05,0.2);
     m_CurrentObservation=target; m_ObservationStamp=stamp; m_ObservationAge=0;
    }
    m_ObservationAge+=timeSlice;
    target=m_PreviousObservation+(m_CurrentObservation-m_PreviousObservation)*Math.Clamp(m_ObservationAge/m_ObservationInterval,0,1);
   }
   else m_ObservationStamp=-1;
   requested=ORD_CameraMounts.Forward(m_ResolvedYaw,m_ResolvedPitch);
   // Articulating the gimbal moves the lens. Four bounded corrections also cover very close ground points.
   for(int iteration=0;iteration<4;iteration++)
    requested=vector.Direction(ORD_CameraMounts.SensorOrigin(drone,ORD_CameraMounts.Constrain(drone,requested)),target).Normalized();
  }
  else
  {
   m_ObservationStamp=-1;
   float error=m_fYaw-m_ResolvedYaw;
   while(error>180) error-=360;
   while(error< -180) error+=360;
   float blend=1-Math.Pow(2.718281828,-Math.Max(timeSlice,0)/0.022);
   m_YawVelocity=error*blend/Math.Max(timeSlice,0.001);
   m_PitchVelocity=(m_fPitch-m_ResolvedPitch)*blend/Math.Max(timeSlice,0.001);
   m_ResolvedYaw+=error*blend; m_ResolvedPitch+=(m_fPitch-m_ResolvedPitch)*blend;
   requested=ORD_CameraMounts.Forward(m_ResolvedYaw,m_ResolvedPitch);
  }
  vector aim=ORD_CameraMounts.Constrain(drone,requested);
  m_GimbalLimited=vector.Dot(aim,requested)<0.999999;
  m_ResolvedYaw=Math.Atan2(aim[0],aim[2])*Math.RAD2DEG;
  m_ResolvedPitch=Math.Asin(Math.Clamp(aim[1],-1,1))*Math.RAD2DEG;
  vector pose[4]; pose[2]=aim;
  pose[0]=Vector(Math.Cos(m_ResolvedYaw*Math.DEG2RAD),0,-Math.Sin(m_ResolvedYaw*Math.DEG2RAD));
  pose[1]=Vector(-Math.Sin(m_ResolvedYaw*Math.DEG2RAD)*Math.Sin(m_ResolvedPitch*Math.DEG2RAD),Math.Cos(m_ResolvedPitch*Math.DEG2RAD),-Math.Cos(m_ResolvedYaw*Math.DEG2RAD)*Math.Sin(m_ResolvedPitch*Math.DEG2RAD));
  pose[3]=ORD_CameraMounts.SensorOrigin(drone,aim); m_Camera.SetTransform(pose);
  ORD_AircraftVisuals visuals=ORD_AircraftVisuals.Cast(drone.FindComponent(ORD_AircraftVisuals));
  if(visuals) visuals.SensorAim(m_ResolvedYaw,m_ResolvedPitch);
  SCR_PlayerController player=SCR_PlayerController.Cast(GetGame().GetPlayerController());
  if(player)
  {
   ObserversSystem observers=ObserversSystem.Cast(GetGame().GetWorld().FindSystem(ObserversSystem));
   if(observers && player.GetControlledEntity())
   {
    float limit=GetGame().GetMaximumViewDistance();
    float serverLimit=GetGame().GetViewDistanceServerLimit();
    if(serverLimit>0) limit=Math.Min(limit,serverLimit);
    float range=Math.Clamp(5000,GetGame().GetMinimumViewDistance(),limit);
    m_Camera.SetFarPlane(range);
    observers.AddFarObserver(player.GetControlledEntity(),drone,pose[3],aim,range,timeSlice); m_FarObserver=true;
   }
   float width,height; GetGame().GetWorkspace().GetScreenSize(width,height);
   if(m_QueueOptics || m_QueueDesignation) player.ORD_Optics(drone,aim,m_fZoom,width/Math.Max(height,1),m_iSensor,++m_OpticsSequence,m_QueueDesignation);
   if(m_QueueFire) player.ORD_Weapon(drone,m_iWeaponMode,aim);
  }
  m_QueueDesignation=false; m_QueueFire=false; m_QueueOptics=false;
 }
 void ProjectOpticalContacts()
 {
  if (m_bActive && m_Drone && m_Camera && !m_bPilot && !m_bMap && m_SensorHUD)
   m_SensorHUD.Project(m_Drone, m_Camera, m_bBoxesEnabled);
 }
 protected void ResetZoomInput()
 {
  m_PoseReady=false; m_YawVelocity=0; m_PitchVelocity=0; m_QueueDesignation=false; m_QueueFire=false; m_QueueOptics=false; m_ObservationStamp=-1;
  InputManager input = GetGame().GetInputManager();
  input.ResetAction("ORD_MouseYaw"); input.ResetAction("ORD_MousePitch");
  input.ResetAction("ORD_CamLeft"); input.ResetAction("ORD_CamRight");
  input.ResetAction("ORD_CamUp"); input.ResetAction("ORD_CamDown");
  input.ResetAction("ORD_ZoomIn"); input.ResetAction("ORD_ZoomOut");
  input.ResetAction("ORD_ZoomWheelIn"); input.ResetAction("ORD_ZoomWheelOut");
 }
 protected void CloseMissionMap()
 {
  if (m_MissionMap) m_MissionMap.Close();
  m_MissionMap = null; m_bMap = false; ResetZoomInput();
 }
 protected void UpdateMapMarkers()
 {
  if (m_MapCursor) m_MapCursor.SetVisible(m_bMap);
  if (m_MapStatus) m_MapStatus.SetVisible(m_bMap);
  foreach (Widget marker : m_aMapWidgets) if (marker) marker.SetVisible(false);
  if (!m_bMap) return;
  int refWidth, refHeight;
  WidgetManager.GetReferenceScreenSize(refWidth, refHeight);
  BaseWorld world = m_Drone.GetOwner().GetWorld();
  for (int i = 0; i < m_aMapPoints.Count() && i < 8 && i < m_aMapWidgets.Count(); i++)
  {
   vector screen = GetGame().GetWorkspace().ProjWorldToScreen(m_aMapPoints[i], world, world.GetCurrentCameraId());
   if (screen[0] < 22 || screen[0] > refWidth - 22 || screen[1] < 22 || screen[1] > refHeight - 22) continue;
   Widget waypoint = m_aMapWidgets[i];
   FrameSlot.SetOffsets(waypoint, screen[0] - 18, screen[1] - 18, screen[0] + 18, screen[1] + 18);
   TextWidget label = TextWidget.Cast(waypoint.FindAnyWidget("ContactLabel"));
   if (label) label.SetText(string.Format("WP %1", i + 1));
   waypoint.SetVisible(true);
  }
  if (m_bMapOrbit && m_aMapWidgets.Count() > 8)
  {
   vector orbitScreen = GetGame().GetWorkspace().ProjWorldToScreen(m_vMapOrbit, world, world.GetCurrentCameraId());
   if (orbitScreen[0] >= 24 && orbitScreen[0] <= refWidth - 24 && orbitScreen[1] >= 24 && orbitScreen[1] <= refHeight - 24)
   {
    Widget orbitMarker = m_aMapWidgets[8];
    FrameSlot.SetOffsets(orbitMarker, orbitScreen[0] - 20, orbitScreen[1] - 20, orbitScreen[0] + 20, orbitScreen[1] + 20);
    TextWidget orbitLabel = TextWidget.Cast(orbitMarker.FindAnyWidget("ContactLabel"));
    if (orbitLabel) orbitLabel.SetText("LOITER");
    orbitMarker.SetVisible(true);
   }
  }
 }
 protected string HeadingMark(float degrees)
 {
  int heading = (int)Math.Round(degrees);
  while (heading < 0) heading += 360;
  while (heading >= 360) heading -= 360;
  if (heading == 0) return "N";
  if (heading == 90) return "E";
  if (heading == 180) return "S";
  if (heading == 270) return "W";
  if (heading < 10) return string.Format("00%1", heading);
  if (heading < 100) return string.Format("0%1", heading);
  return string.Format("%1", heading);
 }
 protected bool CollectContact(IEntity entity)
 {
  if (!ORD_ObservationPolicy.Alive(entity) || entity == m_Drone.GetOwner()) return true;
  vector offset = ORD_ObservationPolicy.Point(entity) - m_vContactOrigin;
  float distance = offset.Length();
  if (distance <= 1 || distance > m_Drone.SensorRange()) return true;
  float shortSide, longSide;
  if (!ORD_ObservationPolicy.Measure(entity,m_vContactOrigin,m_vContactForward,m_fZoom,m_ContactAspect,m_iSensor,shortSide,longSide)) return true;
  if (shortSide < 2 || longSide < 4) return true;
  float score = (1-vector.Dot(offset/distance,m_vContactForward))*100 + distance/m_Drone.SensorRange();
  if (entity == m_Drone.HUDTrackedEntity()) score = -1;
  int index = 0;
  while (index < m_ContactScores.Count() && m_ContactScores[index] <= score) index++;
  if (index >= 96) return true;
  m_ContactScores.InsertAt(score,index); m_aContactCandidates.InsertAt(entity,index);
  if (m_aContactCandidates.Count() > 96) { m_aContactCandidates.Remove(96); m_ContactScores.Remove(96); }
  return true;
 }
 protected ORD_LocalObservation LocalObservation(IEntity entity, float now)
 {
  for (int i=m_Observations.Count()-1;i>=0;i--)
  {
   if (!m_Observations[i].Entity || now-m_Observations[i].LastCandidate>30) { m_Observations.Remove(i); continue; }
   if (m_Observations[i].Entity == entity) { m_Observations[i].LastCandidate=now; return m_Observations[i]; }
  }
  if (m_Observations.Count()>=128) m_Observations.Remove(0);
  ORD_LocalObservation result=new ORD_LocalObservation(); result.Entity=entity; result.LastCandidate=now;
  m_Observations.Insert(result); return result;
 }
 protected void HideContacts()
 {
  foreach (Widget contactWidget : m_aContactWidgets) if (contactWidget) contactWidget.SetVisible(false);
  if ((m_bPilot || m_bMap || !m_bBoxesEnabled) && m_SensorHUD) m_SensorHUD.ClearContacts();
 }
 protected bool ContactVisible(vector point, IEntity entity)
 {
  return ORD_ObservationPolicy.Visible(m_Drone.GetOwner(),m_vContactOrigin,point,entity);
 }
 protected void ShowContact(int index, vector point, float halfWidth, float halfHeight, string label)
 {
  if (index >= m_aContactWidgets.Count()) return;
  Widget widget = m_aContactWidgets[index];
  vector screen = GetGame().GetWorkspace().ProjWorldToScreen(point, m_Drone.GetOwner().GetWorld(), m_Drone.GetOwner().GetWorld().GetCurrentCameraId());
  int refWidth, refHeight; WidgetManager.GetReferenceScreenSize(refWidth, refHeight);
  if (screen[0] < halfWidth || screen[0] > refWidth - halfWidth || screen[1] < halfHeight || screen[1] > refHeight - halfHeight) return;
  FrameSlot.SetAnchorMin(widget,0,0); FrameSlot.SetAnchorMax(widget,0,0);
  FrameSlot.SetSize(widget,halfWidth*2,halfHeight*2);
  FrameSlot.SetPos(widget,screen[0]-halfWidth,screen[1]-halfHeight);
  TextWidget textLabel = TextWidget.Cast(widget.FindAnyWidget("ContactLabel"));
  if (textLabel) textLabel.SetText(label);
  widget.SetVisible(true);
 }
 protected void UpdateContacts(float horizontalFOV, float aspect)
 {
  if (!m_SensorHUD) return;
  m_SensorHUD.BeginScan(); m_aContactCandidates.Clear(); m_ContactScores.Clear();
  m_vContactOrigin=m_Camera.GetOrigin(); m_vContactForward=m_Camera.GetTransformAxis(2); m_ContactAspect=aspect;
  BaseWorld world=m_Drone.GetOwner().GetWorld();
  float now=world.GetWorldTime()*0.001;
  world.QueryEntitiesBySphere(m_vContactOrigin,m_Drone.SensorRange(),CollectContact,null,EQueryEntitiesFlags.DYNAMIC);
  int count=m_aContactCandidates.Count();
  int budget=Math.Min(count,48);
  float quality=ORD_ObservationPolicy.Quality(world,m_iSensor);
  for(int i=0;i<budget;i++)
  {
   int index=i;
   if(i>=8 && count>48) index=8+((i-8+m_ContactCursor)%(count-8));
   IEntity candidate=m_aContactCandidates[index];
   ORD_LocalObservation observation=LocalObservation(candidate,now);
   bool classified;
   bool eligible=ORD_ObservationPolicy.Observe(m_Drone.GetOwner(),candidate,m_vContactForward,m_fZoom,aspect,m_iSensor,m_Drone.SensorRange(),classified);
   observation.Evidence.Sample(now,eligible,classified,ChimeraCharacter.Cast(candidate)!=null,quality);
  }
  m_ContactCursor+=40;
  foreach(ORD_LocalObservation item:m_Observations)
  {
   if(!m_aContactCandidates.Contains(item.Entity)) item.Evidence.Sample(now,false,false,false);
  }
  // Present in stable priority order, rather than discovery or registry order.
  foreach(IEntity entity:m_aContactCandidates)
  {
   ORD_LocalObservation item=LocalObservation(entity,now);
   if(item.Evidence.Visible && item.Evidence.Acquired && now-item.Evidence.LastEligible<=0.3)
    m_SensorHUD.AddContact(entity,item.Evidence.Classified);
  }
 }

 protected void UpdateHUD(IEntity drone)
 {
  if (!m_bPilot)
  {
   if (m_SensorHUD) m_SensorHUD.Update(m_Drone, m_Camera, m_iAppliedSensor, m_bInputMissing, m_GimbalLimited, m_fFeedTime<m_ThermalErrorUntil);
   return;
  }
  if (!m_TopLeft) return;
  vector position = drone.GetOrigin();
  float agl = position[1] - drone.GetWorld().GetSurfaceY(position[0], position[2]);
  float heading = m_Drone.Heading();
  float tapeHeading = heading;
  if (!m_bPilot && !m_bMap) tapeHeading = m_fYaw;
  int tapeCenter = (int)Math.Round(tapeHeading / 30) * 30;
  string mode = "SENSOR";
  if (m_bPilot) mode = "FLIGHT";
  if (m_bMap) mode = "MAP";
  if (m_Drone.ReturningHome()) mode += "/RTB";
  else if (m_Drone.Automatic()) mode += "/AUTO";
  string sensor = "EO DAY";
  if (!m_bPilot && !m_bMap && m_iSensor == 1) sensor = "IR WHITE HOT";
  if (!m_bPilot && !m_bMap && m_iSensor == 2) sensor = "IR BLACK HOT";
  int seconds = (int)m_fFeedTime;
  int minutes = seconds / 60;
  string secondText = string.Format("%1", seconds - minutes * 60);
  if (seconds - minutes * 60 < 10) secondText = "0" + secondText;
  m_TopLeft.SetText(string.Format("ORION-E  /  CAM 01\nLINK CLAIMED   %1\nASL %2 M  AGL %3 M\nGSPD %4 KM/H  HDG %5", mode, Math.Round(position[1]), Math.Round(agl), Math.Round(m_Drone.Speed() * 3.6), HeadingMark(heading)));
  if (m_HeadingTape) m_HeadingTape.SetText(string.Format("%1       %2       %3       %4       %5\n|---------|---------|---------|---------|", HeadingMark(tapeCenter - 60), HeadingMark(tapeCenter - 30), HeadingMark(tapeCenter), HeadingMark(tapeCenter + 30), HeadingMark(tapeCenter + 60)));
  string trackState = "OFF";
  if (m_Drone.ContactState() == ORD_ContactState.ENTITY) trackState = "TRACK";
  else if (m_Drone.ContactState() == ORD_ContactState.GROUP) trackState = "GROUP";
  else if (m_Drone.ContactState() == ORD_ContactState.TEMP_LOSS) trackState = "SEARCH";
  else if (m_Drone.ContactState() == ORD_ContactState.LOST) trackState = "LAST KNOWN";
  else if (m_Drone.PointLocked()) trackState = "POINT";
  float shownZoom = m_fZoom;
  if (m_bMap) shownZoom = m_fMapZoom;
  else if (m_bPilot) shownZoom = 1;
  if (m_ZoomReadout)
  {
   m_ZoomReadout.SetVisible(true);
   if (m_bMap) m_ZoomReadout.SetText(string.Format("MAP  %1X", Math.Round(shownZoom * 10) / 10));
   else if (m_bPilot) m_ZoomReadout.SetText("FLIGHT CAM  /  H FOR SENSOR ZOOM");
   else m_ZoomReadout.SetText(string.Format("SENSOR  %1X / 40X", Math.Round(shownZoom * 10) / 10));
  }
  string weaponState = "SAFE";
  if (m_Drone.Armed()) weaponState = "ARMED";
  string fireState = "READY";
  switch (m_Drone.FireStatus())
  {
   case ORD_FireStatus.SAFED: fireState = "SAFE - V TO ARM"; break;
   case ORD_FireStatus.EMPTY: fireState = "NO STORES"; break;
   case ORD_FireStatus.NO_SENSOR: fireState = "SENSOR REQUIRED"; break;
   case ORD_FireStatus.GROUND: fireState = "AIRBORNE REQUIRED"; break;
   case ORD_FireStatus.NO_TARGET: fireState = "NO VISIBLE POINT"; break;
   case ORD_FireStatus.RANGE: fireState = "TARGET OUT OF RANGE"; break;
   case ORD_FireStatus.COOLDOWN: fireState = "RELOADING"; break;
   case ORD_FireStatus.RESOURCE: fireState = "STORE UNAVAILABLE"; break;
   case ORD_FireStatus.FIRED: fireState = "LAUNCHED"; break;
  }
  if (m_TopRight) m_TopRight.SetText(string.Format("FEED %1:%2\nTRK %3\nMODE %4\nZOOM %5X\nBDL %6 / %7\nFIRE %8", minutes, secondText, trackState, sensor, Math.Round(shownZoom * 10) / 10, m_Drone.Ammo(), weaponState, fireState));
  float shownPitch = Math.Asin(drone.GetTransformAxis(2)[1])*Math.RAD2DEG;
  if (!m_bPilot && !m_bMap) shownPitch = m_fPitch;
  if (m_PitchValue) m_PitchValue.SetText(string.Format("PITCH %1 DEG", Math.Round(shownPitch)));
  bool showReticle = !m_bMap;
  if (m_Reticle) m_Reticle.SetVisible(showReticle);
  if (m_ReticleVertical) m_ReticleVertical.SetVisible(showReticle);
  bool showTrack = false;
  if (m_TrackBox)
  {
   m_TrackBox.SetVisible(showTrack);
   if (showTrack) m_TrackBox.SetText(string.Format("[  %1  ]\n+------------------------+\n|                        |\n|                        |\n+------------------------+", trackState));
  }
  if (m_CenterStatus)
  {
   string status = "STABILIZED";
   if (m_Drone.ContactState() == ORD_ContactState.TEMP_LOSS) status = "SEARCH / LAST SEEN";
   if (m_Drone.ContactState() == ORD_ContactState.LOST) status = "TARGET LOST";
   if (m_bPilot) status = "FLIGHT CAMERA";
   if (m_bMap) status = "MAP / SELECT";
   m_CenterStatus.SetText(status);
  }
  string engineStatus = "OFF";
  if (m_Drone.EngineOn()) engineStatus = "ON";
  string cameraStatus = string.Format("GIMBAL %1 / %2", Math.Round(m_fYaw), Math.Round(m_fPitch));
  if (m_bPilot) cameraStatus = "AIRFRAME CAMERA";
  if (m_bMap) cameraStatus = "MAP CAMERA";
  if (m_BottomLeft) m_BottomLeft.SetText(string.Format("%1\n%2\nENGINE %3\nFUEL %4%%", sensor, cameraStatus, engineStatus, Math.Round(m_Drone.Fuel() * 100)));
  string range = "----";
  string grid = "---- ----";
  string scale = "--      --      --      --      --";
  if (!m_bPilot && !m_bMap && m_Drone.Designated())
  {
   vector target = m_Drone.Target();
   float slantRange = vector.Distance(position, target);
   range = string.Format("%1", Math.Round(slantRange));
   grid = string.Format("%1 %2", Math.Round(target[0] / 100), Math.Round(target[2] / 100));
   float halfWidth = slantRange * Math.Tan(30 * Math.DEG2RAD) / m_fZoom;
   scale = string.Format("0      %1      %2      %3      %4", Math.Round(halfWidth * 0.5), Math.Round(halfWidth), Math.Round(halfWidth * 1.5), Math.Round(halfWidth * 2));
  }
  if (m_BottomCenter) m_BottomCenter.SetText(string.Format("RNG %1 M\n%2\n|-------|--------|--------|--------|", range, scale));
  string targeting = "SENSOR POINT"; if (m_iWeaponMode == ORD_TargetMode.VEHICLE) targeting = "TRACKED VEHICLE";
  if (m_BottomRight) m_BottomRight.SetText(string.Format("GRID %1\nSLANT RNG %2 M\nSET AGL %3 M\nSET SPD %4 KM/H\nY TARGET: %5", grid, range, Math.Round(m_Drone.TargetAltitude()), Math.Round(m_Drone.TargetSpeed() * 3.6), targeting));
  if (m_MapStatus && m_bMap)
  {
   vector mapDistance = m_vMapCenter - position; mapDistance[1] = 0;
   string mapRange = "IN RANGE";
   if (mapDistance.Length() > m_Drone.LinkRange()) mapRange = "OUT OF LINK RANGE";
   m_MapStatus.SetText(string.Format("MISSION MAP  /  GRID %1 %2  /  WAYPOINTS %3/8  /  LOITER %4 M  /  %5\nPAN MOUSE/ARROWS   WHEEL ZOOM   ENTER ADD   P LOITER   J FLY ROUTE   C CLEAR", Math.Round(m_vMapCenter[0] / 100), Math.Round(m_vMapCenter[2] / 100), m_Drone.RouteCount(), Math.Round(m_Drone.LoiterRadius()), mapRange));
  }
  if (m_ControlHint)
  {
   string controls = "ESC EXIT   H SENSOR   M MAP   I ENGINE   R RTB   S UP / W DOWN   A/D BANK   SHIFT/Z POWER";
   if (!m_bPilot) controls = "M MAP | LOOK MOUSE/ARROWS | +/- ZOOM | TAB POINT | T TRACK | B BOXES | Y TARGET MODE | V ARM | F FIRE";
   if (m_bMap) controls = "ESC EXIT   M SENSOR   MOUSE/ARROWS PAN   WHEEL ZOOM   ENTER WP   P LOITER   J ROUTE   C CLEAR";
   if (m_bInputMissing) controls = "INPUT ACTIONS MISSING - RELOAD ADDON IN WORKBENCH";
   m_ControlHint.SetText(controls);
  }
 }
}

// Action values for wheel-down may be negative; direction belongs to the action.
class ORD_SensorZoom
{
 static float Step(float zoom, float keyIn, float keyOut, float wheelIn, float wheelOut, float dt)
 {
  // Multiple bindings held in one direction must not defeat the opposite key.
  float keys = Math.Min(Math.AbsFloat(keyIn),1)-Math.Min(Math.AbsFloat(keyOut),1);
  float wheel = Math.Min(Math.AbsFloat(wheelIn),1)-Math.Min(Math.AbsFloat(wheelOut),1);
  return Math.Clamp(zoom*Math.Pow(2.7182818,keys*Math.Clamp(dt,0,0.1)*2.5+wheel*0.35),1,40);
 }
}




