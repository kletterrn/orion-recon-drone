from pathlib import Path
p=Path('Scripts/Game/ORD/ORD_TerminalComponent.c');s=p.read_text(encoding='utf-8-sig');s=s.replace('drone.CoordToParent("0 -0.65 2.65")','drone.CoordToParent(CameraAnchor(drone,"ORD_SensorView","0 -0.73 2.42"))').replace('drone.CoordToParent("0 2.2 -9")','drone.CoordToParent(CameraAnchor(drone,"ORD_PilotView","0 2.2 -9"))');pos=s.index(' protected void UpdateEngineAudio()');s=s[:pos]+''' protected vector CameraAnchor(IEntity aircraft,string name,vector fallback)
 {
  vector marker[4];if(ORD_RC8Rig.Socket(aircraft,name,marker))return marker[3];return fallback;
 }
'''+s[pos:];p.write_text(s)
