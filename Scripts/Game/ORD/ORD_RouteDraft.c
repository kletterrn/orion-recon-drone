// Local planner state. Never sends commands or changes the accepted mission.
class ORD_RouteDraft
{
 ref array<vector> Points = {};
 float Altitude, Speed, Radius;
 int Selected = -1;
 bool Dirty;
 string WorldPath;

 bool Valid()
 {
  if (WorldPath == "" || !Points || Points.Count() < 1 || Points.Count() > 8) return false;
  if (!(Altitude >= 150 && Altitude <= 2000 && Speed >= 30 && Speed <= 65 && Radius >= 250 && Radius <= 1500)) return false;
  foreach (vector point : Points)
   for (int axis = 0; axis < 3; axis++)
    if (!(point[axis] >= -10000000 && point[axis] <= 10000000)) return false;
  return true;
 }
 static string SlotPath(int slot)
 {
  if (slot < 1 || slot > 3) return "";
  return string.Format("$profile:ORD_RouteSlot%1.json", slot);
 }
 bool Save(int slot)
 {
  string path = SlotPath(slot);
  if (path == "" || !Valid()) return false;
  JsonSaveContext context = new JsonSaveContext();
  if (!context.WriteValue("version", 1) || !context.WriteValue("world", WorldPath)) return false;
  if (!context.WriteValue("points", Points) || !context.WriteValue("altitude", Altitude)) return false;
  if (!context.WriteValue("speed", Speed) || !context.WriteValue("radius", Radius)) return false;
  return context.SaveToFile(path);
 }
 static ORD_RouteDraft Load(int slot, string world, out string error)
 {
  error = "Saved route unavailable or invalid";
  string path = SlotPath(slot);
  if (path == "" || !FileIO.FileExists(path)) { error = "This route slot is empty"; return null; }
  JsonLoadContext context = new JsonLoadContext();
  if (!context.LoadFromFile(path)) return null;
  ORD_RouteDraft draft = new ORD_RouteDraft(); int version;
  if (!context.ReadValue("version", version) || version != 1) return null;
  if (!context.ReadValue("world", draft.WorldPath) || !context.ReadValue("points", draft.Points)) return null;
  if (!context.ReadValue("altitude", draft.Altitude) || !context.ReadValue("speed", draft.Speed) || !context.ReadValue("radius", draft.Radius)) return null;
  if (!draft.Valid()) return null;
  if (draft.WorldPath != world) { error = "Saved route belongs to another world"; return null; }
  draft.Dirty = true; error = ""; return draft;
 }
}
