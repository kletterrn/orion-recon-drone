// Local, read-only sensor presentation. No camera, flight or targeting commands.
class ORD_HUDContact
{
 IEntity Entity;
 string Id;
 float LastSeen;
}

class ORD_SensorHUD
{
 protected Widget m_Root;
 protected CanvasWidget m_Text, m_Geometry;
 protected ref array<ref CanvasWidgetCommand> m_TextDraw = {};
 protected ref array<ref CanvasWidgetCommand> m_Draw = {};
 protected ref array<ref ORD_HUDContact> m_Registry = {};
 protected ref array<IEntity> m_Visible = {};
 protected ref array<IEntity> m_Classified = {};
 protected int m_NextId, m_ContactCount;
 protected float m_Width, m_Height, m_Scale = 1;
 protected string m_Selected = "--";
 protected bool m_Observed;
 protected vector m_Observation;

 bool Open()
 {
  m_Root = GetGame().GetWorkspace().CreateWidgets("{707B22AC91E47701}UI/ORD/Sensor.layout");
  if (!m_Root) return false;
  m_Text = CanvasWidget.Cast(m_Root.FindAnyWidget("Telemetry"));
  m_Geometry = CanvasWidget.Cast(m_Root.FindAnyWidget("Symbology"));
  SetVisible(false);
  return m_Text && m_Geometry;
 }
 void Close()
 {
  if (m_Root) m_Root.RemoveFromHierarchy();
  m_Root = null; m_Text = null; m_Geometry = null;
  m_Registry.Clear(); m_Visible.Clear(); m_TextDraw.Clear(); m_Draw.Clear();
 }
 void SetVisible(bool visible) { if (m_Root) m_Root.SetVisible(visible); }
 int ContactCount() { return m_ContactCount; }
 string SelectedId() { return m_Selected; }
 bool HasObservation() { return m_Observed; }
 vector Observation() { return m_Observation; }
 void ClearContacts() { m_Classified.Clear(); m_Visible.Clear(); m_ContactCount = 0; }
 void BeginScan() { m_Visible.Clear(); m_Classified.Clear(); }
 void AddContact(IEntity entity, bool classified = false) { if (entity && m_Visible.Count() < 48) { m_Visible.Insert(entity); if(classified) m_Classified.Insert(entity); } }

 static float Bearing(vector direction)
 {
  float value = Math.Atan2(direction[0], direction[2]) * Math.RAD2DEG;
  if (value < 0) value += 360;
  return value;
 }
 static string Pad(int value, int digits = 2)
 {
  string text = value.ToString();
  while (text.Length() < digits) text = "0" + text;
  return text;
 }
 static string Azimuth(float value)
 {
  int rounded = Math.Round(value);
  rounded = ((rounded % 360) + 360) % 360;
  return Pad(rounded, 3);
 }
 static string Column(string value, int width)
 {
  while (value.Length() < width) value = " " + value;
  return value;
 }
 static string Decimal(float value, int places = 1)
 {
  int factor = Math.Pow(10, places);
  int scaled = Math.Round(Math.AbsFloat(value) * factor);
  string sign;
  if (value < 0 && scaled != 0) sign = "-";
  return sign + (scaled / factor).ToString() + "." + Pad(scaled % factor, places);
 }
 static string Grid(vector point)
 {
  if (!SCR_MapEntity.GetMapInstance()) return "--";
  int east, north;
  // Native map conversion: metre resolution, five digits, easting/northing.
  SCR_MapEntity.GetGridPos(point, east, north, 0, 4);
  return Pad(east, 5) + " " + Pad(north, 5);
 }
 protected void Dimensions()
 {
  // Canvas draw commands use physical pixels. The fixed UI reference remains
  // 1920x1080 even on a larger/ultrawide viewport; it is not the canvas extent.
  GetGame().GetWorkspace().GetScreenSize(m_Width, m_Height);
  m_Scale = Math.Min(m_Width / 1920, m_Height / 1080);
 }
 // Fixed character advance gives a monospaced display using the shipped font.
 // Each glyph is native editable canvas text; no baked artwork or extra font dependency.
 protected void Text(array<ref CanvasWidgetCommand> commands, float x, float y, string value, float size = 24, int color = 0xFFF0F2ED)
 {
  float advance = size * 0.60 * m_Scale;
  for (int i = 0; i < value.Length(); i++)
  {
   string glyph = value.Substring(i, 1);
   if (glyph == " ") continue;
   // Native line degree mark avoids the canvas font's legacy UTF-8 decoding.
   if (glyph == "~")
   {
    ref array<float> circle = {};
    for (int segment = 0; segment <= 12; segment++)
    {
     float angle = segment * Math.PI * 2 / 12;
     circle.Insert(x + i * advance + (4 + Math.Cos(angle) * 2.5) * m_Scale);
     circle.Insert(y + (5 + Math.Sin(angle) * 2.5) * m_Scale);
    }
    LineDrawCommand ringShadow = new LineDrawCommand();
    ringShadow.m_iColor = 0xFF000000; ringShadow.m_fWidth = 3*m_Scale; ringShadow.m_Vertices = circle;
    commands.Insert(ringShadow);
    LineDrawCommand ring = new LineDrawCommand();
    ring.m_iColor = color; ring.m_fWidth = m_Scale; ring.m_Vertices = circle;
    commands.Insert(ring);
    continue;
   }
   for (int edge = 0; edge < 4; edge++)
   {
    float dx = 0, dy = 0;
    if (edge == 0) dx = -m_Scale;
    if (edge == 1) dx = m_Scale;
    if (edge == 2) dy = -m_Scale;
    if (edge == 3) dy = m_Scale;
    TextDrawCommand shadow = new TextDrawCommand();
    shadow.m_Position = Vector(x + i * advance + dx, y + dy, 0);
    shadow.m_sText = glyph; shadow.m_iColor = 0xFF000000;
    shadow.m_fSize = size * m_Scale; shadow.m_iFontPropertiesId = 0;
    commands.Insert(shadow);
   }
   TextDrawCommand text = new TextDrawCommand();
   text.m_Position = Vector(x + i * advance, y, 0);
   text.m_sText = glyph; text.m_iColor = color;
   text.m_fSize = size * m_Scale; text.m_iFontPropertiesId = 0;
   commands.Insert(text);
  }
 }
 protected void CenterText(array<ref CanvasWidgetCommand> commands, float y, string value, float size = 24)
 {
  Text(commands, (m_Width - value.Length() * size * 0.60 * m_Scale) * 0.5, y, value, size);
 }
 protected void Line(float x1, float y1, float x2, float y2, float width = 1.5, int color = 0xFFF0F2ED)
 {
  LineDrawCommand shadow = new LineDrawCommand();
  shadow.m_iColor = 0xFF000000; shadow.m_fWidth = (width + 2) * m_Scale;
  shadow.m_Vertices = {x1, y1, x2, y2}; m_Draw.Insert(shadow);
  LineDrawCommand line = new LineDrawCommand();
  line.m_iColor = color; line.m_fWidth = width * m_Scale;
  line.m_Vertices = {x1, y1, x2, y2}; m_Draw.Insert(line);
 }
 protected string ContactId(IEntity entity, float now, IEntity selected)
 {
  for (int i = m_Registry.Count() - 1; i >= 0; i--)
  {
   ORD_HUDContact old = m_Registry[i];
   if (old.Entity == entity) { old.LastSeen = now; return old.Id; }
   if (!old.Entity || (old.Entity != selected && now - old.LastSeen > 30)) m_Registry.Remove(i);
  }
  if (m_Registry.Count() >= 64)
  {
   int oldest = -1; float age = -1;
   for (int j = 0; j < m_Registry.Count(); j++)
   {
    if (m_Registry[j].Entity == selected) continue;
    float candidateAge = now - m_Registry[j].LastSeen;
    if (candidateAge > age) { oldest = j; age = candidateAge; }
   }
   if (oldest >= 0) m_Registry.Remove(oldest);
  }
  ORD_HUDContact contact = new ORD_HUDContact();
  contact.Entity = entity; contact.LastSeen = now; m_NextId++;
  string prefix = "C-";
  contact.Id = prefix + Pad(m_NextId); m_Registry.Insert(contact);
  return contact.Id;
 }
 protected bool Bounds(IEntity entity, SCR_CameraBase camera, out vector minimum, out vector maximum)
 {
  vector low, high; entity.GetWorldBounds(low, high);
  minimum = Vector(m_Width, m_Height, 0); maximum = vector.Zero;
  for (int i = 0; i < 8; i++)
  {
   vector corner = low;
   if ((i & 1) != 0) corner[0] = high[0];
   if ((i & 2) != 0) corner[1] = high[1];
   if ((i & 4) != 0) corner[2] = high[2];
   if (vector.Dot(corner - camera.GetOrigin(), camera.GetTransformAxis(2)) <= 0.1) return false;
   vector screen = GetGame().GetWorkspace().ProjWorldToScreen(corner, entity.GetWorld(), entity.GetWorld().GetCurrentCameraId());
   // World projection is DPI-unscaled UI space; convert exactly once for canvas.
   screen[0] = GetGame().GetWorkspace().DPIScale(screen[0]);
   screen[1] = GetGame().GetWorkspace().DPIScale(screen[1]);
   minimum[0] = Math.Min(minimum[0], screen[0]); minimum[1] = Math.Min(minimum[1], screen[1]);
   maximum[0] = Math.Max(maximum[0], screen[0]); maximum[1] = Math.Max(maximum[1], screen[1]);
  }
  vector center = (minimum + maximum) * 0.5;
  float halfWidth = Math.Clamp((maximum[0] - minimum[0]) * 0.5 + 5 * m_Scale, 18 * m_Scale, 180 * m_Scale);
  float halfHeight = Math.Clamp((maximum[1] - minimum[1]) * 0.5 + 5 * m_Scale, 20 * m_Scale, 180 * m_Scale);
  minimum = center - Vector(halfWidth, halfHeight, 0); maximum = center + Vector(halfWidth, halfHeight, 0);
  return maximum[0] > 0 && minimum[0] < m_Width && maximum[1] > 0 && minimum[1] < m_Height;
 }
 protected void Bracket(vector low, vector high, bool selected)
 {
  float length = 10 * m_Scale, width = 1;
  if (selected) { length = 22 * m_Scale; width = 2; }
  length = Math.Min(length, (high[0] - low[0]) * 0.3);
  Line(low[0], low[1], low[0] + length, low[1], width);
  Line(low[0], low[1], low[0], low[1] + length, width);
  Line(high[0], low[1], high[0] - length, low[1], width);
  Line(high[0], low[1], high[0], low[1] + length, width);
  Line(low[0], high[1], low[0] + length, high[1], width);
  Line(low[0], high[1], low[0], high[1] - length, width);
  Line(high[0], high[1], high[0] - length, high[1], width);
  Line(high[0], high[1], high[0], high[1] - length, width);
 }
 // Projection every frame; the terminal's existing bounded LOS scan refreshes at 10 Hz.
 void Project(ORD_AircraftComponent drone, SCR_CameraBase camera, bool boxes)
 {
  if (!m_Geometry || !camera) return;
  Dimensions(); m_Draw.Clear(); m_ContactCount = 0;
  float s = m_Scale, cx = m_Width * 0.5, cy = m_Height * 0.5;
  Line(cx - 28*s, cy, cx - 5*s, cy); Line(cx + 5*s, cy, cx + 28*s, cy);
  Line(cx, cy - 28*s, cx, cy - 5*s); Line(cx, cy + 5*s, cx, cy + 28*s);
  float azimuth = Bearing(camera.GetTransformAxis(2));
  int first = Math.Floor(azimuth / 5) * 5 - 25;
  for (int bearing = first; bearing <= first + 55; bearing += 5)
  {
   float delta = bearing - azimuth;
   if (Math.AbsFloat(delta) > 25) continue;
   float x = cx + delta * 12*s;
   float length = 17*s;
   if (bearing % 10 == 0)
   {
    length = 28*s;
    Text(m_Draw, x - 20*s, 59*s, Azimuth(bearing), 23);
   }
   Line(x, 122*s, x, 122*s - length);
  }
  Line(cx, 137*s, cx - 11*s, 158*s); Line(cx - 11*s,158*s,cx + 11*s,158*s); Line(cx + 11*s,158*s,cx,137*s);
  Line(cx - 240*s,m_Height - 119*s,cx - 139*s,m_Height - 119*s,1);
  Line(cx + 139*s,m_Height - 119*s,cx + 240*s,m_Height - 119*s,1);
  IEntity selected = drone.HUDTrackedEntity();
  m_Selected = "--";
  if (selected) m_Selected = ContactId(selected, drone.GetOwner().GetWorld().GetWorldTime() * 0.001, selected);
  if (boxes)
  {
   // Selected contact gets the first slot, but only when the existing LOS scan sees it.
   ref array<IEntity> ordered = {};
   if (selected && m_Visible.Contains(selected)) ordered.Insert(selected);
   foreach (IEntity visible : m_Visible) if (visible && visible != selected) ordered.Insert(visible);
   foreach (IEntity entity : ordered)
   {
    if (m_ContactCount >= 8) break;
    vector low, high;
    if (!Bounds(entity, camera, low, high)) continue;
    if (!ORD_ObservationPolicy.Alive(entity) || !ORD_ObservationPolicy.Visible(drone.GetOwner(),camera.GetOrigin(),ORD_ObservationPolicy.Point(entity),entity)) continue;
    bool confirmed = entity == selected && drone.ContactState() == ORD_ContactState.ENTITY;
    string label = ContactId(entity, drone.GetOwner().GetWorld().GetWorldTime() * 0.001, selected);
    if (m_Classified.Contains(entity))
    {
     if (ChimeraCharacter.Cast(entity)) label += " PERSON";
     else label += " VEHICLE";
    }
    Bracket(low, high, confirmed);
    float labelX = Math.Clamp(high[0] + 9*s, 12*s, m_Width - label.Length() * 13.2*s - 12*s);
    float labelY = Math.Clamp(low[1] - 27*s, 12*s, m_Height - 32*s);
    Text(m_Draw, labelX, labelY, label, 22);
    m_ContactCount++;
   }
  }
  m_Geometry.SetDrawCommands(m_Draw);
 }
 void Update(ORD_AircraftComponent drone, SCR_CameraBase camera, int sensor, bool missingInput, bool limited = false, bool thermalFallback = false)
 {
  if (!m_Text || !camera) return;
  Dimensions(); m_TextDraw.Clear();
  float s = m_Scale;
  IEntity aircraft = drone.GetOwner(); BaseWorld world = aircraft.GetWorld();
  vector position = aircraft.GetOrigin(), direction = camera.GetTransformAxis(2);
  float azimuth = Bearing(direction), elevation = Math.Asin(Math.Clamp(direction[1], -1, 1)) * Math.RAD2DEG;
  float pixelWidth, pixelHeight; GetGame().GetWorkspace().GetScreenSize(pixelWidth,pixelHeight);
  float hfov = 2 * Math.Atan2(Math.Tan(camera.GetVerticalFOV() * Math.DEG2RAD * 0.5) * pixelWidth / Math.Max(pixelHeight, 1), 1) * Math.RAD2DEG;
  string identifier = aircraft.GetName();
  if (identifier.IsEmpty()) identifier = "UAV";
  // Scenario entity name is authoritative when no callsign provider exists.
  if (identifier.Length() > 23) identifier = identifier.Substring(0, 23);
  Text(m_TextDraw, 68*s, 62*s, "ORION / " + identifier);
  string flight = drone.FlightModeText();
  if (drone.Automatic() && !drone.ReturningHome() && !drone.FlyingRoute()) flight = "OVERWATCH";
  Text(m_TextDraw, 68*s, 98*s, "FLIGHT " + flight);
  CenterText(m_TextDraw, 168*s, "LOS AZ " + Azimuth(azimuth) + "~G", 22);
  string mode = "EO";
  if (sensor == 1) mode = "IR WH";
  if (sensor == 2) mode = "IR BH";
  if(thermalFallback) mode="EO FALLBACK";
  Text(m_TextDraw, m_Width - 270*s, 62*s, mode);
  // Sensor orientation is world-stabilized by the existing terminal basis.
  string stability="STAB ON"; if(limited) stability="GIMBAL LIMIT";
  Text(m_TextDraw, m_Width - 270*s, 98*s, stability);
  string link = "LINK --";
  PlayerController player = GetGame().GetPlayerController();
  if (player && drone.Operator() == player.GetPlayerId() && !drone.Destroyed()) link = "LINK OK";
  Text(m_TextDraw, m_Width - 270*s, 134*s, link);
  int seconds = world.GetWorldTime() * 0.001;
  Text(m_TextDraw, m_Width - 270*s, 170*s, "SIM " + Pad(seconds / 3600) + ":" + Pad((seconds / 60) % 60) + ":" + Pad(seconds % 60));
  string speed = "--";
  Physics physics = aircraft.GetPhysics();
  if (physics)
  {
   vector velocity = physics.GetVelocity(); velocity[1] = 0;
   speed = Math.Round(velocity.Length() * 3.6).ToString();
  }
  Text(m_TextDraw,68*s,280*s,"GS   " + Column(speed,5) + " km/h");
  Text(m_TextDraw,68*s,316*s,"HDG  " + Column(Azimuth(Bearing(aircraft.GetTransformAxis(2))),5) + "~G");
  Text(m_TextDraw,68*s,352*s,"ALT  " + Column(Math.Round(position[1] - world.GetOceanBaseHeight()).ToString(),5) + " m ASL");
  Text(m_TextDraw,68*s,388*s,"AGL  " + Column(Math.Round(position[1] - world.GetSurfaceY(position[0],position[2])).ToString(),5) + " m");
  // Observation is ALWAYS the present optical axis hit, not a stale designated coordinate.
  TraceParam trace = new TraceParam(); trace.Start = camera.GetOrigin();
  trace.End = trace.Start + direction * drone.SensorRange();
  trace.Flags = TraceFlags.WORLD | TraceFlags.ENTS; trace.Exclude = aircraft;
  float fraction = world.TraceMove(trace,null);
  m_Observed = fraction > 0 && fraction < 1;
  m_Observation = vector.Zero;
  string observation = "--", range = "--";
  if (m_Observed)
  {
   m_Observation = trace.Start + (trace.End - trace.Start) * fraction;
   observation = Grid(m_Observation); range = Decimal(vector.Distance(trace.Start,m_Observation) / 1000,2) + " km";
  }
  Text(m_TextDraw,68*s,m_Height - 134*s,"UAV GRID " + Grid(position));
  Text(m_TextDraw,68*s,m_Height - 98*s,"OBS GRID " + observation);
  string track = "FREE";
  switch (drone.ContactState())
  {
   case ORD_ContactState.POINT: track = "POINT LOCK"; break;
   case ORD_ContactState.ACQUIRING: track = "ACQUIRING"; break;
   case ORD_ContactState.ENTITY: track = "ENTITY TRACK"; break;
   case ORD_ContactState.GROUP: track = "GROUP TRACK"; break;
   case ORD_ContactState.TEMP_LOSS: track = "COASTING"; break;
   case ORD_ContactState.LOST: track = "TRACK LOST"; break;
  }
  CenterText(m_TextDraw,m_Height - 134*s,track,22);
  string selectedId = m_Selected;
  if (drone.ContactState() == ORD_ContactState.NONE || drone.ContactState() == ORD_ContactState.POINT) selectedId = "--";
  CenterText(m_TextDraw,m_Height - 98*s,selectedId + " | CONTACTS " + Pad(m_ContactCount),22);
  float right = m_Width - 315*s;
  Text(m_TextDraw,right,m_Height - 206*s,"AZ      " + Column(Azimuth(azimuth),5) + "~G");
  Text(m_TextDraw,right,m_Height - 170*s,"EL      " + Column(Decimal(elevation),5) + "~");
  Text(m_TextDraw,right,m_Height - 134*s,"HFOV    " + Column(Decimal(hfov),5) + "~");
  Text(m_TextDraw,right,m_Height - 98*s,"GEO RNG " + range);
  if (missingInput) CenterText(m_TextDraw,m_Height - 40*s,"INPUTS UNAVAILABLE - RESTART WITH ADDON",16);
  m_Text.SetDrawCommands(m_TextDraw);
 }
}
