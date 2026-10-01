// Native terrain map with a local editable draft and server-confirmed mission.
class ORD_MissionMap : ScriptedWidgetEventHandler
{
 protected ORD_AircraftComponent m_Drone;
 protected bool m_Initialized, m_HasView;
 protected vector m_ViewCenter;
 protected float m_ViewZoom;
 bool OwnsTopMenu() { return m_Menu && GetGame().GetMenuManager().GetTopMenu()==m_Menu; }
 protected ref ORD_ReconPane m_Recon;
 bool EditingNote() { return m_Recon && m_Recon.EditingNote(); }
 protected SCR_MapEntity m_Map;
 protected MenuBase m_Menu;
 protected Widget m_Root;
 protected CanvasWidget m_Canvas;
 protected TextWidget m_Status, m_RouteSummary;
 protected ref array<vector> m_Points = {};
 protected ref array<ref CanvasWidgetCommand> m_Draw = {};
 protected int m_Revision, m_Selected = -1, m_Tool, m_Drag = -1;
 protected float m_Altitude, m_Speed, m_Radius, m_Age;
 protected vector m_Point;
 protected bool m_HasPoint, m_Dirty, m_Centered;
 protected string m_Message;
 protected bool m_Pending;
 protected int m_Response, m_Request;
 protected float m_PendingAge;
 protected vector m_DragStart;
 protected bool m_DragMoved;
 protected bool m_DragRecorded;
 protected ref array<ref ORD_RouteDraft> m_Undo = {};
 protected ref array<ref ORD_RouteDraft> m_Redo = {};
 protected int m_SaveSlot = 1, m_ConfirmSlot = -1;
 protected float m_ConfirmAge;

 protected ORD_RouteDraft CaptureDraft()
 {
  ORD_RouteDraft draft = new ORD_RouteDraft();
  foreach (vector point : m_Points) draft.Points.Insert(point);
  draft.Altitude = m_Altitude; draft.Speed = m_Speed; draft.Radius = m_Radius;
  draft.Selected = m_Selected; draft.Dirty = m_Dirty; draft.WorldPath = GetGame().GetWorldFile();
  return draft;
 }
 protected void RestoreDraft(ORD_RouteDraft draft)
 {
  m_Points.Clear(); foreach (vector point : draft.Points) m_Points.Insert(point);
  m_Altitude = draft.Altitude; m_Speed = draft.Speed; m_Radius = draft.Radius;
  m_Selected = draft.Selected; m_Dirty = draft.Dirty; m_Drag = -1; m_HasPoint = false;
 }
 protected void RecordEdit()
 {
  if (m_Undo.Count() >= 20) m_Undo.RemoveOrdered(0);
  m_Undo.Insert(CaptureDraft()); m_Redo.Clear(); m_ConfirmSlot = -1;
 }
 protected void UndoEdit()
 {
  if (m_Undo.IsEmpty()) { m_Message = "Nothing to undo"; return; }
  m_Redo.Insert(CaptureDraft());
  RestoreDraft(m_Undo[m_Undo.Count()-1]); m_Undo.Remove(m_Undo.Count()-1);
  m_ConfirmSlot = -1; m_Message = "Draft edit undone";
 }
 protected void RedoEdit()
 {
  if (m_Redo.IsEmpty()) { m_Message = "Nothing to redo"; return; }
  m_Undo.Insert(CaptureDraft());
  RestoreDraft(m_Redo[m_Redo.Count()-1]); m_Redo.Remove(m_Redo.Count()-1);
  m_ConfirmSlot = -1; m_Message = "Draft edit restored";
 }
 protected void ReverseDraft()
 {
  if (m_Points.Count() < 2) { m_Message = "Add two points before reversing"; return; }
  RecordEdit();
  int count = m_Points.Count();
  for (int i = 0; i < count / 2; i++)
  {
   vector point = m_Points[i]; m_Points[i] = m_Points[count-1-i]; m_Points[count-1-i] = point;
  }
  if (m_Selected >= 0) m_Selected = count-1-m_Selected;
  m_Dirty = true; m_Message = "Route reversed - Apply to use";
 }
 protected void SaveDraft()
 {
  ORD_RouteDraft draft = CaptureDraft();
  if (!draft.Valid()) { m_Message = "Add valid route points before saving"; return; }
  if (FileIO.FileExists(ORD_RouteDraft.SlotPath(m_SaveSlot)) && m_ConfirmSlot != m_SaveSlot)
  {
   m_ConfirmSlot = m_SaveSlot; m_ConfirmAge = 0;
   m_Message = "Slot occupied - click Save again within 5s"; return;
  }
  m_ConfirmSlot = -1;
  if (draft.Save(m_SaveSlot)) m_Message = string.Format("Draft saved in local slot %1", m_SaveSlot);
  else m_Message = "Could not save route in your profile";
 }
 protected void LoadDraft()
 {
  string error;
  ORD_RouteDraft draft = ORD_RouteDraft.Load(m_SaveSlot, GetGame().GetWorldFile(), error);
  if (!draft) { m_Message = error; return; }
  foreach (vector point : draft.Points)
   if (!m_Drone.ValidMapPoint(point)) { m_Message = "Saved point outside terrain or link range"; return; }
  RecordEdit(); RestoreDraft(draft); m_Tool = 0;
  m_Message = "Saved draft loaded - review, then Apply";
 }

 // Planning estimates use horizontal straight legs, including the return leg.
 // They intentionally exclude the approach, banked turns, wind and climb.
 static float CircuitDistance(array<vector> points)
 {
  if (!points || points.Count() < 2) return 0;
  float distance;
  for (int i = 0; i < points.Count(); i++)
  {
   vector delta = points[(i + 1) % points.Count()] - points[i]; delta[1] = 0;
   distance += delta.Length();
  }
  return distance;
 }
 static string CircuitEstimate(array<vector> points, float speed)
 {
  if (!points || points.Count() < 2 || speed <= 0) return "Circuit estimate: --";
  float distance = CircuitDistance(points);
  if (distance < 1) return "Circuit estimate: --";
  int seconds = Math.Round(distance / speed);
  return string.Format("Circuit %1 km | est. %2:%3", ORD_SensorHUD.Decimal(distance / 1000), seconds / 60, ORD_SensorHUD.Pad(seconds % 60));
 }
 static bool DragThresholdReached(vector start, int x, int y)
 {
  return vector.Distance(start, Vector(x, y, 0)) > 4;
 }

 bool Open(ORD_AircraftComponent drone, ORD_TerminalComponent terminal = null)
 {
  m_Drone = drone; m_Map = SCR_MapEntity.GetMapInstance();
  if (!m_Map) return false;
  m_Menu = GetGame().GetMenuManager().OpenMenu(ChimeraMenuPreset.MapMenu);
  if (!m_Menu) return false;
  m_Root = GetGame().GetWorkspace().CreateWidgets("{A3F84D861D444A20}UI/ORD/MissionMap.layout", m_Menu.GetRootWidget());
  if (!m_Root) { Close(); return false; }
  TextWidget help=TextWidget.Cast(m_Root.FindAnyWidget("Help"));
  if(help)help.SetText("Click: select / aim | Drag: move | Right drag: pan | Wheel: zoom | "+ORD_SensorHUD.Binding("ORD_Map")+" / "+ORD_SensorHUD.Binding("ORD_Exit")+": camera");
  m_Root.AddHandler(this);
  
  m_Canvas = CanvasWidget.Cast(m_Root.FindAnyWidget("MissionCanvas"));
  m_Canvas.AddHandler(this);
  Widget panel = m_Root.FindAnyWidget("MissionPanel");
  Widget child = panel.GetChildren();
  while (child) { if (ButtonWidget.Cast(child)) child.AddHandler(this); child = child.GetSibling(); }
  child = m_Root.FindAnyWidget("PlannerTools").GetChildren();
  while (child) { if (ButtonWidget.Cast(child)) child.AddHandler(this); child = child.GetSibling(); }
  m_Status = TextWidget.Cast(m_Root.FindAnyWidget("MissionStatus"));
  m_RouteSummary = TextWidget.Cast(m_Root.FindAnyWidget("RouteSummary"));
  Widget tools = m_Menu.GetRootWidget().FindAnyWidget("ToolMenuContainer");
  if (tools) tools.SetVisible(false);
  if(terminal) { if(!m_Recon)m_Recon=new ORD_ReconPane(); m_Recon.Open(m_Menu.GetRootWidget(),terminal); }
  if(!m_Initialized) { LoadAccepted(); m_Initialized=true; }
  m_Centered=false; m_Age=0; return true;
 }
 bool IsOpen() { return m_Root && m_Map && m_Map.IsOpen(); }
 void Close()
 {
  if(IsOpen())
  {
   float x,z; m_Map.GetMapCenterWorldPosition(x,z);
   m_ViewCenter=Vector(x,0,z); m_ViewZoom=m_Map.GetTargetZoomPPU(); m_HasView=true;
  }
  m_Drag=-1; m_ConfirmSlot=-1;
  if(m_Recon)m_Recon.Close();
  if (m_Root) { m_Root.RemoveHandler(this); m_Root.RemoveFromHierarchy(); }
  m_Root = null;
  if (m_Menu && GetGame().GetMenuManager().GetTopMenu() == m_Menu) GetGame().GetMenuManager().CloseMenu(m_Menu);
  m_Menu = null;
 }
 protected SCR_PlayerController Player() { return SCR_PlayerController.Cast(GetGame().GetPlayerController()); }
 protected void LoadAccepted()
 {
  m_Points.Clear();
  for (int i = 0; i < m_Drone.RouteCount(); i++) m_Points.Insert(m_Drone.RoutePoint(i));
  m_Revision = m_Drone.MissionRevision(); m_Altitude = m_Drone.TargetAltitude();
  m_Speed = m_Drone.TargetSpeed(); m_Radius = m_Drone.LoiterRadius();
  m_Selected = -1; m_Drag = -1; m_Dirty = false; m_Pending = false; m_Message = "Accepted route loaded";
  m_Undo.Clear(); m_Redo.Clear(); m_ConfirmSlot = -1;
 }
 protected vector MousePoint(int x, int y)
 {
  float worldX, worldZ; m_Map.ScreenToWorld(x, y, worldX, worldZ);
  return Vector(worldX, 0, worldZ);
 }
 protected vector Screen(vector point)
 {
  int x, y; m_Map.WorldToScreen(point[0], point[2], x, y, true);
  return Vector(x, y, 0);
 }
 override bool OnMouseButtonDown(Widget w, int x, int y, int button)
 {
  if (!m_Map || !m_Map.IsOpen() || button != 0) return false;
  // Panel children dispatch through OnClick, never become map targets.
  if (w != m_Canvas) return false;
  if (m_Pending) return true;
  if(m_Recon && m_Recon.MapClick(x,y))return true;
  m_Point = MousePoint(x, y); m_HasPoint = true;
  if (m_Tool != 0) { m_Message = "Point selected - use the command button"; return true; }
  m_Selected = -1;
  m_DragRecorded = false;
  vector cursor = Vector(x, y, 0);
  for (int i = 0; i < m_Points.Count(); i++) if (vector.Distance(Screen(m_Points[i]), cursor) < 18) { m_Selected = i; break; }
  if (m_Selected < 0)
  {
   if (m_Points.Count() >= 8) { m_Message = "Eight waypoints maximum"; return true; }
   RecordEdit(); m_DragRecorded = true;
   m_Points.Insert(m_Point); m_Selected = m_Points.Count() - 1; m_Dirty = true;
  }
  m_Drag = m_Selected; m_DragStart = cursor; m_DragMoved = false; return true;
 }
 override bool OnMouseButtonUp(Widget w, int x, int y, int button)
 {
  if (button != 0 || m_Drag < 0) return false;
  UpdateDrag(x, y); m_Drag = -1; return true;
 }
 protected void UpdateDrag(int x, int y)
 {
  if (m_Drag < 0 || m_Drag >= m_Points.Count()) return;
  if (!m_DragMoved && !DragThresholdReached(m_DragStart, x, y)) return;
  if (!m_DragRecorded) { RecordEdit(); m_DragRecorded = true; }
  m_DragMoved = true; m_Points[m_Drag] = MousePoint(x, y); m_Dirty = true;
 }
 override bool OnClick(Widget w, int x, int y, int button)
 {
  string name = w.GetName();
  if (button != 0) return false;
  if (name.StartsWith("Label")) name = w.GetParent().GetName();
  SCR_PlayerController player = Player();
  IEntity drone = m_Drone.GetOwner();
  if (m_Pending) { m_Message = "Waiting for the server to accept or reject this draft"; return true; }
  if (!player && (name == "Apply" || name == "Fly" || name == "Resume" || name == "Clear" || name == "Loiter" || name == "Arm" || name == "Fire")) { m_Message = "Operator controller unavailable"; return true; }
  switch (name)
  {
   case "RouteTool": m_Tool = 0; if(m_Recon)m_Recon.AimMode=false; break;
   case "LoiterTool": if(m_Recon)m_Recon.AimMode=false; m_Tool = 1; m_HasPoint = false; break;
   case "WeaponTool": if(m_Recon)m_Recon.AimMode=false; m_Tool = 2; m_HasPoint = false; break;
   case "Reload": LoadAccepted(); break;
   case "Delete": if (m_Selected >= 0 && m_Selected < m_Points.Count()) { RecordEdit(); m_Points.RemoveOrdered(m_Selected); m_Selected = -1; m_Dirty = true; } break;
   case "Undo": UndoEdit(); break;
   case "Redo": RedoEdit(); break;
   case "Reverse": ReverseDraft(); break;
   case "CenterAircraft":
    vector aircraftPosition = drone.GetOrigin(); m_Map.ZoomPanSmooth(m_Map.GetTargetZoomPPU(), aircraftPosition[0], aircraftPosition[2]); break;
   case "CenterHome":
    vector homePosition = m_Drone.Home(); m_Map.ZoomPanSmooth(m_Map.GetTargetZoomPPU(), homePosition[0], homePosition[2]); break;
   case "Slot": m_SaveSlot = m_SaveSlot % 3 + 1; m_ConfirmSlot = -1; break;
   case "SaveDraft": SaveDraft(); break;
   case "LoadDraft": LoadDraft(); break;
   case "Earlier": MoveSelected(-1); break;
   case "Later": MoveSelected(1); break;
   case "Apply":
    m_Drag = -1; m_Response = player.ORD_MissionResponse(); m_Pending = true; m_PendingAge = 0;
    player.ORD_ApplyMission(drone, m_Points, m_Altitude, m_Speed, m_Radius, m_Revision); m_Request = player.ORD_MissionRequest(); m_Message = "Submitted - awaiting server"; break;
   case "Fly": if (m_Dirty) m_Message = "Apply your draft before flying"; else player.ORD_Send(drone, ORD_Command.PATROL); break;
   case "Resume": player.ORD_Send(drone, ORD_Command.RESUME_ROUTE); break;
   case "Clear": player.ORD_Send(drone, ORD_Command.CLEAR_ROUTE); m_Dirty = false; m_Drag = -1; m_Message = "Clear requested - awaiting server"; break;
   case "Loiter": if (m_Tool == 1 && m_HasPoint) player.ORD_MapPoint(drone, m_Point, true, m_Radius); else m_Message = "Select Loiter tool, then click a point"; break;
   case "Arm": player.ORD_Send(drone, ORD_Command.ARM); break;
   case "Fire": if (m_Tool == 2 && m_HasPoint) player.ORD_Weapon(drone, ORD_TargetMode.MAP_POINT, m_Point); else m_Message = "Select Weapon target, then click a point"; break;
   case "AltMinus": if (m_Altitude > 150) { RecordEdit(); m_Altitude = Math.Max(150,m_Altitude-50); m_Dirty = true; } break;
   case "AltPlus": if (m_Altitude < 2000) { RecordEdit(); m_Altitude = Math.Min(2000,m_Altitude+50); m_Dirty = true; } break;
   case "SpeedMinus": if (m_Speed > 30) { RecordEdit(); m_Speed = Math.Max(30,m_Speed-2.78); m_Dirty = true; } break;
   case "SpeedPlus": if (m_Speed < 65) { RecordEdit(); m_Speed = Math.Min(65,m_Speed+2.78); m_Dirty = true; } break;
   case "RadiusMinus": if (m_Radius > 250) { RecordEdit(); m_Radius = Math.Max(250,m_Radius-50); m_Dirty = true; } break;
   case "RadiusPlus": if (m_Radius < 1500) { RecordEdit(); m_Radius = Math.Min(1500,m_Radius+50); m_Dirty = true; } break;
   default: return false;
  }
  return true;
 }
 protected void MoveSelected(int direction)
 {
  int next = m_Selected + direction;
  if (m_Selected < 0 || next < 0 || next >= m_Points.Count()) return;
  RecordEdit();
  vector point = m_Points[m_Selected]; m_Points[m_Selected] = m_Points[next]; m_Points[next] = point;
  m_Selected = next; m_Dirty = true;
 }
 protected void Line(vector a, vector b, int color, float width = 2)
 {
  LineDrawCommand command = new LineDrawCommand();
  command.m_iColor = color; command.m_fWidth = width;
  command.m_Vertices = {a[0],a[1],b[0],b[1]}; m_Draw.Insert(command);
 }
 protected void Label(vector point, string text, int color)
 {
  TextDrawCommand command = new TextDrawCommand(); command.m_Position = point;
  command.m_sText = text; command.m_iColor = color; command.m_fSize = 18; command.m_iFontPropertiesId = 0;
  m_Draw.Insert(command);
 }
 void Update(float dt)
 {
  if (!IsOpen()) return;
  if(m_Recon)m_Recon.Update(dt);
  m_Age += dt;
  if (m_ConfirmSlot >= 0)
  {
   m_ConfirmAge += dt;
   if (m_ConfirmAge > 5) { m_ConfirmSlot = -1; m_Message = "Save confirmation expired"; }
  }
  if (!m_Centered && m_Age > 0.5)
  {
   vector position = m_Drone.GetOwner().GetOrigin(); float zoom=0.12;
   if(m_HasView) { position=m_ViewCenter; zoom=m_ViewZoom; }
   m_Map.ZoomPanSmooth(zoom,position[0],position[2]); m_Centered=true;
  }
  if(m_Centered)
  {
   float viewX,viewZ; m_Map.GetMapCenterWorldPosition(viewX,viewZ);
   m_ViewCenter=Vector(viewX,0,viewZ); m_ViewZoom=m_Map.GetTargetZoomPPU(); m_HasView=true;
  }
  SCR_PlayerController responsePlayer = Player();
  if (m_Pending)
  {
   m_PendingAge += dt;
   if (responsePlayer && responsePlayer.ORD_MissionResponse() != m_Response && responsePlayer.ORD_ResponseRequest() == m_Request)
   {
    if (!responsePlayer.ORD_MissionAccepted()) { m_Pending = false; m_Message = responsePlayer.ORD_Feedback(); }
    else if (m_Drone.MissionRevision() >= responsePlayer.ORD_AcceptedRevision()) LoadAccepted();
   }
   if (m_Pending && m_PendingAge > 8) { m_Pending = false; m_Message = "No confirmation received. Reload accepted before retrying."; }
  }
  else if (m_Drone.MissionRevision() != m_Revision && !m_Dirty) LoadAccepted();
  if (m_Drag >= 0) { int mx,my; WidgetManager.GetMousePos(mx,my); UpdateDrag(mx,my); }
  m_Draw.Clear();
  for (int i = 0; i < m_Points.Count(); i++)
  {
   vector a = Screen(m_Points[i]); int color = 0xFFE5BE78;
   if (i == m_Selected) color = 0xFFFFFFFF;
   Label(a, string.Format("[%1]",i+1),color);
   if (m_Points.Count() > 1) Line(a,Screen(m_Points[(i+1)%m_Points.Count()]),0xFFE5BE78);
  }
  vector drone = Screen(m_Drone.GetOwner().GetOrigin()); Label(drone,"ORION",0xFFB4D1CB);
  Label(Screen(m_Drone.Home())+Vector(0,18,0),"HOME",0xFFFFFFFF);
  if (m_Drone.FlyingRoute()) Line(drone,Screen(m_Drone.RoutePoint(m_Drone.ActiveWaypoint())),0xFFB4D1CB,4);
  vector center = m_Drone.Orbit(); float radius = m_Drone.LoiterRadius();
  if (m_Tool == 1 && m_HasPoint) { center = m_Point; radius = m_Radius; }
  for (int segment = 0; segment < 48; segment++)
  {
   float a0 = segment * Math.PI2 / 48; float a1 = (segment+1)*Math.PI2/48;
   Line(Screen(center+Vector(Math.Sin(a0)*radius,0,Math.Cos(a0)*radius)),Screen(center+Vector(Math.Sin(a1)*radius,0,Math.Cos(a1)*radius)),0xFFB4D1CB);
  }
  if (m_Tool == 2 && m_HasPoint) Label(Screen(m_Point),"+ TARGET",0xFFFF7468);
  m_Canvas.SetDrawCommands(m_Draw);
  string tool = "ROUTE"; if (m_Tool == 1) tool = "LOITER"; if (m_Tool == 2) tool = "WEAPON TARGET";
  if(m_Recon && m_Recon.AimMode)tool="SENSOR AIM";
  string draft = "APPLIED"; if (m_Dirty) draft = "UNAPPLIED DRAFT"; if (m_Pending) draft = "AWAITING SERVER";
  string armed = "SAFE"; if (m_Drone.Armed()) armed = "ARMED";
  string active = "--";
  if (m_Drone.FlyingRoute() && m_Drone.ActiveWaypoint() >= 0 && m_Drone.ActiveWaypoint() < m_Drone.RouteCount()) active = (m_Drone.ActiveWaypoint()+1).ToString();
  string status = string.Format("%1 | %2\n%3/8 draft | live waypoint %4\nAltitude %5 m AGL\nSpeed %6 km/h\nLoiter radius %7 m",tool,draft,m_Points.Count(),active,Math.Round(m_Altitude),Math.Round(m_Speed*3.6),Math.Round(m_Radius));
  status += string.Format("\n%1 | %2 missiles\n%3\n%4\n%5",armed,m_Drone.Ammo(),m_Drone.FlightModeText()+" / "+m_Drone.MissionStatus(),m_Drone.WeaponStatusText(),m_Message);
  SCR_PlayerController controller = Player();
  if (controller && controller.ORD_RecentFeedback() != "") status += "\n" + controller.ORD_RecentFeedback();
  m_Status.SetText(status);
  if (m_RouteSummary)
  {
   string summary = "ROUTE PLAN | " + draft + "\n" + CircuitEstimate(m_Points, m_Speed);
   summary += "\nStraight legs at planned speed\nExcludes approach, turns and wind";
   if (m_Points.Count() == 1) summary += "\nAdd a second point for a circuit";
   else if (m_Points.IsEmpty()) summary += "\nSelect Route and add waypoints";
   else summary += "\nIncludes last-to-first return leg";
   if (m_Revision != m_Drone.MissionRevision()) summary += "\nRoute changed on server - reload";
   m_RouteSummary.SetText(summary);
  }
  TextWidget slotLabel = TextWidget.Cast(m_Root.FindAnyWidget("LabelSlot"));
  if (slotLabel) slotLabel.SetText(string.Format("Local slot %1 / 3", m_SaveSlot));
  m_Root.FindAnyWidget("Undo").SetEnabled(!m_Pending && !m_Undo.IsEmpty());
  m_Root.FindAnyWidget("Redo").SetEnabled(!m_Pending && !m_Redo.IsEmpty());
 }
}
