from pathlib import Path
p=Path('Scripts/Game/ORD/ORD_AircraftComponent.c');s=p.read_text(encoding='utf-8-sig');a=s.index(' static vector Hardpoint');b=s.index(' int Operator()',a)
s=s[:a]+''' bool PayloadTransform(out vector local[4])
 {
  return ORD_RC8Rig.Socket(GetOwner(),"ORION_PAYLOAD_SOCKET",local);
 }
'''+s[b:]
s=s.replace('  GetOwner().GetTransform(spawn.Transform);\n  int station = 0;\n  // The single store always uses station zero.\n  spawn.Transform[3] = GetOwner().CoordToParent(Hardpoint(station));','  vector localSocket[4], aircraftTransform[4];\n  if(!PayloadTransform(localSocket)) { SetFireStatus(ORD_FireStatus.RESOURCE); return; }\n  GetOwner().GetTransform(aircraftTransform);\n  Math3D.MatrixMultiply4(aircraftTransform,localSocket,spawn.Transform);')
s=s.replace('  missile.SetAngles(GetOwner().GetAngles());\n','')
s=s.replace('protected IEntity SpawnStore(Resource resource, float side)','protected IEntity SpawnStore(Resource resource)')
s=s.replace('  Math3D.MatrixIdentity4(spawn.Transform);\n  int station = 0; if (side > 0) station = 1;\n  spawn.Transform[3] = Hardpoint(station);','  if(!PayloadTransform(spawn.Transform)) return null;')
s=s.replace('SpawnStore(resource, -3.2)','SpawnStore(resource)');p.write_text(s,encoding='utf-8')
p=Path('Scripts/Game/ORD/ORD_TerminalComponent.c');s=p.read_text(encoding='utf-8-sig');s=s.replace(' protected AudioHandle m_ORD_EngineAudio;\n protected bool m_bORD_EngineAudioPlaying;\n protected bool m_bORD_CruiseAudio;',' protected ORD_AudioPresentation m_OperatorFeed;')
a=s.index(' protected void UpdateEngineAudio()');b=s.index(' void Close()',a)
s=s[:a]+''' protected void UpdateEngineAudio()
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
'''+s[b:]
s=s.replace('  if (m_bORD_EngineAudioPlaying) AudioSystem.TerminateSound(m_ORD_EngineAudio);\n  m_bORD_EngineAudioPlaying = false;','  if(m_OperatorFeed)m_OperatorFeed.SetOperatorFeed(false);\n  m_OperatorFeed=null;')
p.write_text(s,encoding='utf-8')
