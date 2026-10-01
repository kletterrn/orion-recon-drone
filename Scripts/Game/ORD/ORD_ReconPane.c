class ORD_ReconPane : ScriptedWidgetEventHandler
{
 protected Widget m_Root;
 protected CanvasWidget m_Canvas;
 protected TextWidget m_CardText, m_State;
 protected EditBoxWidget m_Note;
 protected string m_NoteDraft;
 protected TextWidget m_AimLabel, m_CategoryLabel, m_BlendLabel, m_InsetLabel;
 protected SCR_MapEntity m_Map;
 protected ORD_TerminalComponent m_Terminal;
 protected ref array<ref CanvasWidgetCommand> m_Draw = {};
 protected int m_SelectedId = -1, m_Category;
 protected float m_Poll = 2;
 protected string m_Faction, m_Message;
 protected float m_MessageAge;
 bool EditingNote() { return m_Note && GetGame().GetWorkspace().GetFocusedWidget()==m_Note; }
 bool AimMode;
 protected bool m_OpenedBefore;
 bool Open(Widget parent, ORD_TerminalComponent terminal = null)
 {
  m_Map=SCR_MapEntity.GetMapInstance(); m_Terminal=terminal;
  if(!m_OpenedBefore)AimMode=terminal!=null;
  m_OpenedBefore=true;
  SCR_PlayerController player=Player(); if(player)m_Faction=player.ORD_SyncReportFaction();
  m_Root=GetGame().GetWorkspace().CreateWidgets("{4DCF1BB954D140DB}UI/ORD/Recon.layout",parent); if(!m_Root)return false;
  m_Canvas=CanvasWidget.Cast(m_Root.FindAnyWidget("ReconDrawing"));
  m_CardText=TextWidget.Cast(m_Root.FindAnyWidget("ReconCard")); m_State=TextWidget.Cast(m_Root.FindAnyWidget("ReconState"));
  m_Note=EditBoxWidget.Cast(m_Root.FindAnyWidget("ReconNote")); m_Note.SetPlaceholderText("Operator note (160 characters maximum)");
  m_Note.SetText(m_NoteDraft);
  m_AimLabel=TextWidget.Cast(m_Root.FindAnyWidget("LabelReconAim"));
  m_CategoryLabel=TextWidget.Cast(m_Root.FindAnyWidget("LabelReconCategory"));
  m_BlendLabel=TextWidget.Cast(m_Root.FindAnyWidget("LabelReconBlend"));
  m_InsetLabel=TextWidget.Cast(m_Root.FindAnyWidget("LabelReconInset"));
  Widget child=m_Root.FindAnyWidget("ReconPanel").GetChildren();
  while(child) { if(ButtonWidget.Cast(child))child.AddHandler(this); child=child.GetSibling(); }
  if(!terminal)
  {
   FrameSlot.SetPos(m_Root.FindAnyWidget("ReconPanel"),-432,40);
   FrameSlot.SetSize(m_Root.FindAnyWidget("ReconPanel"),412,340);
   FrameSlot.SetPos(m_State,12,292); FrameSlot.SetSize(m_State,388,40);
   m_Canvas.ClearFlags(WidgetFlags.IGNORE_CURSOR); m_Canvas.AddHandler(this);
   foreach(string name:{"ReconAim","ReconSave","ReconCategory","ReconNote","NoteBG","ReconBlend","ReconInset"}) m_Root.FindAnyWidget(name).SetVisible(false);
  }
  return true;
 }
 void Close()
 {
  if(m_Note) { m_NoteDraft=m_Note.GetText(); if(EditingNote())GetGame().GetWorkspace().SetFocusedWidget(null); }
  if(m_Root)m_Root.RemoveFromHierarchy();
  m_Root=null; m_Terminal=null; m_Note=null; m_Canvas=null; m_CardText=null; m_State=null;
  m_AimLabel=null; m_CategoryLabel=null; m_BlendLabel=null; m_InsetLabel=null;
 }
 protected SCR_PlayerController Player() { return SCR_PlayerController.Cast(GetGame().GetPlayerController()); }
 protected ORD_ReconCard Selected()
 {
  SCR_PlayerController player=Player(); if(!player)return null;
  foreach(ORD_ReconCard card:player.ORD_Reports) if(card.Id==m_SelectedId)return card;
  return null;
 }
 protected vector Screen(vector point)
 {
  int x,y; m_Map.WorldToScreen(point[0],point[2],x,y,true); return Vector(x,y,0);
 }
 protected void Line(vector a,vector b,int color=0xFFB4D1CB)
 {
  LineDrawCommand line=new LineDrawCommand(); line.m_iColor=color; line.m_fWidth=2;
  line.m_Vertices={a[0],a[1],b[0],b[1]}; m_Draw.Insert(line);
 }
 protected void Label(vector position,string value,int color=0xFFB4D1CB)
 {
  TextDrawCommand label=new TextDrawCommand(); label.m_Position=position; label.m_sText=value;
  label.m_fSize=17; label.m_iColor=color; label.m_iFontPropertiesId=0; m_Draw.Insert(label);
 }
 protected string AimLabel()
 {
  if(AimMode)return "Point sensor: ON";
  return "Point sensor: off";
 }
 bool MapClick(int x,int y)
 {
  SCR_PlayerController player=Player(); if(!player)return false;
  foreach(ORD_ReconCard card:player.ORD_Reports)
   if(vector.Distance(Screen(card.Position),Vector(x,y,0))<22)
   {
    m_SelectedId=card.Id;
    if(m_Terminal)m_Terminal.PointSensorAt(card.Position);
    return true;
   }
  if(!AimMode || !m_Terminal)return false;
  float wx,wz; m_Map.ScreenToWorld(x,y,wx,wz);
  m_Terminal.PointSensorAt(Vector(wx,GetGame().GetWorld().GetSurfaceY(wx,wz),wz)); return true;
 }
 override bool OnMouseButtonDown(Widget w,int x,int y,int button)
 {
  if(button==0 && w==m_Canvas) return MapClick(x,y);
  return false;
 }
 override bool OnClick(Widget w,int x,int y,int button)
 {
  if(button!=0)return false;
  SCR_PlayerController player=Player();
  if(!player)return false;
  string name=w.GetName();
  if(name=="ReconAim" && m_Terminal) { AimMode=!AimMode; return true; }
  if(name=="ReconCategory") { m_Category=(m_Category+1)%4; return true; }
  if(name=="ReconSave" && m_Terminal)
  {
   string note=m_Note.GetText(); if(note.Length()>160) { m_Message="Note too long (maximum 160 characters)"; m_MessageAge=5; return true; }
   m_Terminal.SaveSighting(note,m_Category); return true;
  }
  if(name=="ReconBlend" && m_Terminal) { m_Terminal.ToggleBlend(); return true; }
  if(name=="ReconInset" && m_Terminal) { m_Terminal.CycleInset(); return true; }
  if(name=="ReconRefresh") { player.ORD_RequestReports(); return true; }
  if(name=="ReconLook")
  {
   ORD_ReconCard selected=Selected(); if(!selected)return true;
   m_Map.ZoomPanSmooth(m_Map.GetTargetZoomPPU(),selected.Position[0],selected.Position[2]);
   if(m_Terminal)m_Terminal.PointSensorAt(selected.Position); return true;
  }
  if(name=="ReconPrevious" || name=="ReconNext")
  {
   int count=player.ORD_Reports.Count(); if(count==0)return true;
   int index=-1; for(int i=0;i<count;i++) if(player.ORD_Reports[i].Id==m_SelectedId)index=i;
   if(name=="ReconPrevious")index=(index+count-1)%count; else index=(index+1)%count;
   m_SelectedId=player.ORD_Reports[index].Id; return true;
  }
  return false;
 }
 void Update(float dt)
 {
  if(!m_Root || !m_Map || !m_Map.IsOpen())return;
  SCR_PlayerController player=Player(); if(!player)return;
  string faction=player.ORD_SyncReportFaction();
  if(faction!=m_Faction) { m_Faction=faction; m_SelectedId=-1; m_Poll=2; }
  m_MessageAge=Math.Max(0,m_MessageAge-dt);
  m_Poll+=dt; if(m_Poll>=2) { m_Poll=0; player.ORD_RequestReports(); }
  m_Draw.Clear();
  foreach(ORD_ReconCard card:player.ORD_Reports)
  {
   int color=0xFFE5BE78; if(card.Id==m_SelectedId)color=0xFFFFFFFF;
   Label(Screen(card.Position),string.Format("[R%1] LAST",card.Id),color);
  }
  if(!Selected() && player.ORD_Reports.Count()>0)m_SelectedId=player.ORD_Reports[player.ORD_Reports.Count()-1].Id;
  ORD_ReconCard selected=Selected();
  string text="FACTION RECON | no report selected\nClick a report marker or use Previous / Next.\nPositions are fixed observations, not live tracks.";
  if(selected)
  {
   int stamp=selected.Observed; int age=Math.Max(0,GetGame().GetWorld().GetWorldTime()*0.001-stamp);
   text=string.Format("R%1 | %2\nGRID %3\nLAST OBSERVED SIM %4:%5:%6\n%7 seconds ago | %8\n%9",selected.Id,ORD_ReconCard.CategoryName(selected.Category),ORD_SensorHUD.Grid(selected.Position),ORD_SensorHUD.Pad(stamp/3600),ORD_SensorHUD.Pad((stamp/60)%60),ORD_SensorHUD.Pad(stamp%60),age,selected.Author,selected.Note);
  }
  m_CardText.SetText(text);
  string status="Shared faction reports | newest 16 | mission only";
  if(m_Terminal)
  {
   vector pose[4]; m_Terminal.SensorPose(pose);
   ORD_AircraftComponent aircraft=m_Terminal.ReconAircraft();
   vector position=aircraft.GetOwner().GetOrigin();
   array<vector> trail=m_Terminal.ReconTrail();
   for(int j=1;j<trail.Count();j++)Line(Screen(trail[j-1]),Screen(trail[j]),0xFF75A5B0);
   Line(Screen(position),Screen(position+pose[2]*600));
   array<vector> area=m_Terminal.ReconFootprint();
   if(area.Count()==4) for(int k=0;k<4;k++)Line(Screen(area[k]),Screen(area[(k+1)%4]),0xFFB4D1CB);
   status="EST. CAMERA FOOTPRINT"; if(area.Count()!=4)status="FOOTPRINT UNAVAILABLE | sky / beyond range";
   if(AimMode)status+="\nCLICK MAP TO POINT SENSOR";
   status+="\n"+player.ORD_RecentFeedback();
   m_AimLabel.SetText(AimLabel());
   m_CategoryLabel.SetText(ORD_ReconCard.CategoryName(m_Category));
   m_BlendLabel.SetText(m_Terminal.BlendLabel());
   m_InsetLabel.SetText(m_Terminal.InsetLabel());
  }
  if(m_MessageAge>0)status=m_Message;
  m_State.SetText(status); m_Canvas.SetDrawCommands(m_Draw);
 }
}
class ORD_ReportViewer
{
 protected static ref ORD_ReportViewer s_Active;
 protected ref ORD_ReconPane m_Pane;
 protected MenuBase m_Menu;
 protected int m_OpenGrace=10;
 static void Open()
 {
  if(s_Active) { s_Active.Close(); return; }
  s_Active=new ORD_ReportViewer();
  s_Active.m_Menu=GetGame().GetMenuManager().OpenMenu(ChimeraMenuPreset.MapMenu);
  if(!s_Active.m_Menu) { s_Active=null; return; }
  s_Active.m_Pane=new ORD_ReconPane();
  if(!s_Active.m_Pane.Open(s_Active.m_Menu.GetRootWidget())) { s_Active.Close(); return; }
  GetGame().GetCallqueue().CallLater(s_Active.Tick,100,true);
 }
 protected void Tick()
 {
  if(!SCR_MapEntity.GetMapInstance() || !SCR_MapEntity.GetMapInstance().IsOpen())
  {
   if(m_OpenGrace-- > 0)return;
   Close(); return;
  }
  m_OpenGrace=0;
  m_Pane.Update(0.1);
 }
 void Close()
 {
  GetGame().GetCallqueue().Remove(Tick); if(m_Pane)m_Pane.Close();
  if(m_Menu && GetGame().GetMenuManager().GetTopMenu()==m_Menu)GetGame().GetMenuManager().CloseMenu(m_Menu);
  m_Pane=null; m_Menu=null; s_Active=null;
 }
}
class ORD_ReviewReportsAction : ScriptedUserAction
{
 override bool GetActionNameScript(out string outName) { outName="Review faction reconnaissance"; return true; }
 override bool HasLocalEffectOnlyScript() { return true; }
 override void PerformAction(IEntity pOwnerEntity,IEntity pUserEntity) { ORD_ReportViewer.Open(); }
}


