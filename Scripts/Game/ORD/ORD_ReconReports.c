// Immutable mission-lifetime sightings. No entity references or tracking updates.
class ORD_ReconCard
{
 int Id, Category;
 vector Position;
 float Observed;
 string Note, Author, FactionId;
 static string CategoryName(int category)
 {
  switch (category) { case 1: return "Vehicle (estimate)"; case 2: return "Personnel (estimate)"; case 3: return "Activity (estimate)"; }
  return "Unclassified";
 }
}
class ORD_ReconReports
{
 static ref array<ref ORD_ReconCard> Cards = {};
 protected static BaseWorld s_World;
 protected static int s_NextId;
 static void ResetForWorld()
 {
  if (s_World == GetGame().GetWorld()) return;
  s_World = GetGame().GetWorld(); Cards.Clear(); s_NextId = 0;
 }
 static string FactionOf(IEntity character)
 {
  if (!character) return "";
  CharacterControllerComponent controls = CharacterControllerComponent.Cast(character.FindComponent(CharacterControllerComponent));
  if (!controls || controls.IsDead()) return "";
  FactionAffiliationComponent affiliation = FactionAffiliationComponent.Cast(character.FindComponent(FactionAffiliationComponent));
  if (!affiliation || !affiliation.GetAffiliatedFaction()) return "";
  return affiliation.GetAffiliatedFaction().GetFactionKey();
 }
 static ORD_ReconCard Add(vector position, float observed, string note, int category, string author, string factionKey)
 {
  ResetForWorld();
  if (factionKey == "" || category < 0 || category > 3 || note.Length() > 160) return null;
  int factionCount;
  foreach (ORD_ReconCard existing : Cards) if (existing.FactionId == factionKey) factionCount++;
  if (factionCount >= 16)
   for (int i = 0; i < Cards.Count(); i++) if (Cards[i].FactionId == factionKey) { Cards.RemoveOrdered(i); break; }
  if (Cards.Count() >= 128) Cards.RemoveOrdered(0);
  ORD_ReconCard card = new ORD_ReconCard(); card.Id = ++s_NextId;
  card.Position = position; card.Observed = observed; card.Note = note;
  card.Category = category; card.Author = author; card.FactionId = factionKey; Cards.Insert(card); return card;
 }
 static string Snapshot(string factionKey)
 {
  ResetForWorld();
  ref array<int> ids = {}, categories = {}; ref array<vector> points = {};
  ref array<float> times = {}; ref array<string> notes = {}, authors = {};
  foreach (ORD_ReconCard card : Cards)
  {
   if (factionKey == "" || card.FactionId != factionKey) continue;
   ids.Insert(card.Id); categories.Insert(card.Category); points.Insert(card.Position);
   times.Insert(card.Observed); notes.Insert(card.Note); authors.Insert(card.Author);
  }
  JsonSaveContext context = new JsonSaveContext();
  context.WriteValue("ids", ids); context.WriteValue("categories", categories); context.WriteValue("points", points);
  context.WriteValue("times", times); context.WriteValue("notes", notes); context.WriteValue("authors", authors);
  return context.SaveToString();
 }
 static void Decode(string data, array<ref ORD_ReconCard> output)
 {
  output.Clear(); JsonLoadContext context = new JsonLoadContext(); if (!context.LoadFromString(data)) return;
  ref array<int> ids = {}, categories = {}; ref array<vector> points = {};
  ref array<float> times = {}; ref array<string> notes = {}, authors = {};
  context.ReadValue("ids", ids); context.ReadValue("categories", categories); context.ReadValue("points", points);
  context.ReadValue("times", times); context.ReadValue("notes", notes); context.ReadValue("authors", authors);
  int count = ids.Count();
  if (count > 16 || categories.Count()!=count || points.Count()!=count || times.Count()!=count || notes.Count()!=count || authors.Count()!=count) return;
  for (int i = 0; i < count; i++)
  {
   ORD_ReconCard card = new ORD_ReconCard(); card.Id=ids[i]; card.Category=categories[i]; card.Position=points[i];
   card.Observed=times[i]; card.Note=notes[i]; card.Author=authors[i]; output.Insert(card);
  }
 }
}
modded class SCR_PlayerController
{
 ref array<ref ORD_ReconCard> ORD_Reports = {};
 protected string m_ORDReportsFaction;
 protected float m_ORDReportPoll = -100, m_ORDReportSave = -100;
 // Keep cached reports tied to the current living character's faction, even
 // when a reply arrives after changing sides or closing the map.
 string ORD_SyncReportFaction()
 {
  string factionKey=ORD_ReconReports.FactionOf(GetControlledEntity());
  if(factionKey!=m_ORDReportsFaction) { ORD_Reports.Clear(); m_ORDReportsFaction=factionKey; }
  return factionKey;
 }
 void ORD_RequestReports()
 {
  if (this != GetGame().GetPlayerController()) return;
  if (Replication.IsServer()) ORD_ReportListRPC(); else Rpc(ORD_ReportListRPC);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_ReportListRPC()
 {
  if (!Replication.IsServer()) return;
  float now = GetGame().GetWorld().GetWorldTime()*0.001;
  if (now-m_ORDReportPoll < 1) return; m_ORDReportPoll=now;
  ORD_SendReports();
 }
 protected void ORD_SendReports()
 {
  string factionKey=ORD_ReconReports.FactionOf(GetControlledEntity());
  string data = ORD_ReconReports.Snapshot(factionKey);
  if (this == GetGame().GetPlayerController()) ORD_ReportListReply(data,factionKey); else Rpc(ORD_ReportListReply,data,factionKey);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Owner)]
 protected void ORD_ReportListReply(string data,string factionKey)
 {
  string currentFaction=ORD_SyncReportFaction();
  if(currentFaction=="" || factionKey!=currentFaction)return;
  ORD_ReconReports.Decode(data,ORD_Reports);
 }
 void ORD_SaveReport(IEntity drone, vector direction, string note, int category)
 {
  if (this != GetGame().GetPlayerController()) return;
  if (Replication.IsServer()) ORD_RecordReport(ORD_Local(drone),direction,note,category,m_ORDPresentationSession);
  else Rpc(ORD_SaveReportRPC,ORD_Id(drone),direction,note,category,m_ORDPresentationSession);
 }
 [RplRpc(RplChannel.Reliable, RplRcver.Server)]
 protected void ORD_SaveReportRPC(RplId id, vector direction, string note, int category,int session)
 {
  ORD_RecordReport(ORD_Find(id),direction,note,category,session);
 }
 protected void ORD_RecordReport(ORD_AircraftComponent aircraft, vector direction, string note, int category,int session)
 {
  if (!Replication.IsServer() || !aircraft || !aircraft.ValidLink(GetPlayerId()) || !aircraft.SensorMode()) return;
  float now=GetGame().GetWorld().GetWorldTime()*0.001;
  if (now-m_ORDReportSave < 2) { ORD_Reply("Wait before saving another sighting",session); return; }
  if (note.Length()>160 || category<0 || category>3 || !(direction.Length()>0.99 && direction.Length()<1.01)) { ORD_Reply("Invalid report",session); return; }
  string factionKey=ORD_ReconReports.FactionOf(GetControlledEntity()); if(factionKey=="")return;
  direction=ORD_CameraMounts.Constrain(aircraft.GetOwner(),direction);
  TraceParam trace=new TraceParam(); trace.Start=ORD_CameraMounts.SensorOrigin(aircraft.GetOwner(),direction);
  trace.End=trace.Start+direction*aircraft.SensorRange(); trace.Flags=TraceFlags.WORLD|TraceFlags.ENTS; trace.Exclude=aircraft.GetOwner();
  float hit=GetGame().GetWorld().TraceMove(trace,null);
  if(hit>=1) { ORD_Reply("No observed surface - sighting not saved",session); return; }
  vector position=trace.Start+(trace.End-trace.Start)*hit;
  string author=GetGame().GetPlayerManager().GetPlayerName(GetPlayerId());
  note.Replace("\n"," "); note.Replace("\r"," ");
  if(ORD_ReconReports.Add(position,now,note,category,author,factionKey))
  { m_ORDReportSave=now; ORD_Reply("Sighting saved - fixed last-observed position",session); ORD_SendReports(); }
 }
}

