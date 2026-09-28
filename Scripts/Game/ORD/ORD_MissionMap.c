// Native terrain map with a local editable draft and server-confirmed mission.
class ORD_MissionMap : ScriptedWidgetEventHandler
{
 protected ORD_AircraftComponent m_Drone;
 protected SCR_MapEntity m_Map;
 protected MenuBase m_Menu;
 protected Widget m_Root;
 protected CanvasWidget m_Canvas;
 protected TextWidget m_Status;
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

 bool Open(ORD_AircraftComponent drone)
 {
  m_Drone = drone; m_Map = SCR_MapEntity.GetMapInstance();
  if (!m_Map) return false;
  m_Menu = GetGame().GetMenuManager().OpenMenu(ChimeraMenuPreset.MapMenu);
  if (!m_Menu) return false;
  m_Root = GetGame().GetWorkspace().CreateWidgets("{A3F84D861D444A20}UI/ORD/MissionMap.layout", m_Menu.GetRootWidget());
  if (!m_Root) { Close(); return false; }
  m_Root.AddHandler(this);
  
  m_Canvas = CanvasWidget.Cast(m_Root.FindAnyWidget("MissionCanvas"));
  m_Canvas.AddHandler(this);
  Widget panel = m_Root.FindAnyWidget("MissionPanel");
  Widget child = panel.GetChildren();
  while (child) { if (ButtonWidget.Cast(child)) child.AddHandler(this); child = child.GetSibling(); }
  m_Status = TextWidget.Cast(m_Root.FindAnyWidget("MissionStatus"));
  Widget tools = m_Menu.GetRootWidget().FindAnyWidget("ToolMenuContainer");
  if (tools) tools.SetVisible(false);
  LoadAccepted(); return true;
 }
 bool IsOpen() { return m_Root && m_Map && m_Map.IsOpen(); }
 void Close()
 {
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
  m_Point = MousePoint(x, y); m_HasPoint = true;
  if (m_Tool != 0) { m_Message = "Point selected - use the command button"; return true; }
  m_Selected = -1;
  vector cursor = Vector(x, y, 0);
  for (int i = 0; i < m_Points.Count(); i++) if (vector.Distance(Screen(m_Points[i]), cursor) < 18) { m_Selected = i; break; }
  if (m_Selected < 0)
  {
   if (m_Points.Count() >= 8) { m_Message = "Eight waypoints maximum"; return true; }
   m_Points.Insert(m_Point); m_Selected = m_Points.Count() - 1; m_Dirty = true;
  }
  m_Drag = m_Selected; return true;
 }
 override bool OnMouseButtonUp(Widget w, int x, int y, int button)
 {
  if (button != 0 || m_Drag < 0) return false;
  m_Points[m_Drag] = MousePoint(x,y); m_Drag = -1; m_Dirty = true; return true;
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
   case "RouteTool": m_Tool = 0; break;
   case "LoiterTool": m_Tool = 1; m_HasPoint = false; break;
   case "WeaponTool": m_Tool = 2; m_HasPoint = false; break;
   case "Reload": LoadAccepted(); break;
   case "Delete": if (m_Selected >= 0 && m_Selected < m_Points.Count()) { m_Points.Remove(m_Selected); m_Selected = -1; m_Dirty = true; } break;
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
   case "AltMinus": m_Altitude = Math.Max(150,m_Altitude-50); m_Dirty = true; break;
   case "AltPlus": m_Altitude = Math.Min(2000,m_Altitude+50); m_Dirty = true; break;
   case "SpeedMinus": m_Speed = Math.Max(30,m_Speed-2.78); m_Dirty = true; break;
   case "SpeedPlus": m_Speed = Math.Min(65,m_Speed+2.78); m_Dirty = true; break;
   case "RadiusMinus": m_Radius = Math.Max(250,m_Radius-50); m_Dirty = true; break;
   case "RadiusPlus": m_Radius = Math.Min(1500,m_Radius+50); m_Dirty = true; break;
   default: return false;
  }
  return true;
 }
 protected void MoveSelected(int direction)
 {
  int next = m_Selected + direction;
  if (m_Selected < 0 || next < 0 || next >= m_Points.Count()) return;
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
  m_Age += dt;
  if (!m_Centered && m_Age > 0.5) { vector position = m_Drone.GetOwner().GetOrigin(); m_Map.ZoomPanSmooth(0.12, position[0], position[2]); m_Centered = true; }
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
  if (m_Drag >= 0) { int mx,my; WidgetManager.GetMousePos(mx,my); m_Points[m_Drag] = MousePoint(mx,my); }
  m_Draw.Clear();
  for (int i = 0; i < m_Points.Count(); i++)
  {
   vector a = Screen(m_Points[i]); int color = 0xFFFFCF60;
   if (i == m_Selected) color = 0xFFFFFFFF;
   Label(a, string.Format("[%1]",i+1),color);
   if (m_Points.Count() > 1) Line(a,Screen(m_Points[(i+1)%m_Points.Count()]),0xFFFFCF60);
  }
  vector drone = Screen(m_Drone.GetOwner().GetOrigin()); Label(drone,"ORION",0xFF48E0E0);
  Label(Screen(m_Drone.Home())+Vector(0,18,0),"HOME",0xFFFFFFFF);
  if (m_Drone.FlyingRoute()) Line(drone,Screen(m_Drone.RoutePoint(m_Drone.ActiveWaypoint())),0xFF48E0E0,4);
  vector center = m_Drone.Orbit(); float radius = m_Drone.LoiterRadius();
  if (m_Tool == 1 && m_HasPoint) { center = m_Point; radius = m_Radius; }
  for (int segment = 0; segment < 48; segment++)
  {
   float a0 = segment * Math.PI2 / 48; float a1 = (segment+1)*Math.PI2/48;
   Line(Screen(center+Vector(Math.Sin(a0)*radius,0,Math.Cos(a0)*radius)),Screen(center+Vector(Math.Sin(a1)*radius,0,Math.Cos(a1)*radius)),0xFF7CDE93);
  }
  if (m_Tool == 2 && m_HasPoint) Label(Screen(m_Point),"+ TARGET",0xFFFF7468);
  m_Canvas.SetDrawCommands(m_Draw);
  string tool = "ROUTE"; if (m_Tool == 1) tool = "LOITER"; if (m_Tool == 2) tool = "WEAPON TARGET";
  string draft = "APPLIED"; if (m_Dirty) draft = "UNAPPLIED DRAFT"; if (m_Pending) draft = "AWAITING SERVER";
  string armed = "SAFE"; if (m_Drone.Armed()) armed = "ARMED";
  string status = string.Format("%1 | %2\n%3/8 points | active %4\nAltitude %5 m AGL\nSpeed %6 km/h\nLoiter radius %7 m",tool,draft,m_Points.Count(),m_Drone.ActiveWaypoint()+1,Math.Round(m_Altitude),Math.Round(m_Speed*3.6),Math.Round(m_Radius));
  status += string.Format("\n%1 | %2 missiles\n%3\n%4\n%5",armed,m_Drone.Ammo(),m_Drone.FlightModeText()+" / "+m_Drone.MissionStatus(),m_Drone.WeaponStatusText(),m_Message);
  SCR_PlayerController controller = Player();
  if (controller && controller.ORD_Feedback() != "") status += "\n" + controller.ORD_Feedback();
  m_Status.SetText(status);
 }
}
