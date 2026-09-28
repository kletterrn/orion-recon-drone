from pathlib import Path
R=Path(__file__).resolve().parents[1]
def edit(path, old, new):
 p=R/path;s=p.read_text(encoding='utf-8');assert old in s,(path,old[:80]);p.write_text(s.replace(old,new),encoding='utf-8')

# SetBoneMatrix consumes the parent-local pose. Preserve rest translation and
# rotate in the bone's own basis, never premultiply a rest matrix around origin.
edit('Scripts/Game/ORD/ORD_AircraftVisuals.c','Math3D.MatrixMultiply3(rotation, m_aRest[index].Matrix, pose);','Math3D.MatrixMultiply3(m_aRest[index].Matrix, rotation, pose);')
# Simulation has separate, unskinned contact pivots; visual wheels have one owner.
for bone in ['front_wheel','rear_wheel_l','rear_wheel_r']:
 edit('Prefabs/ORD/ORD_Aircraft.et',f'PivotID "{bone}"',f'PivotID "{bone}_contact"')
edit('Tools/export_orion_detailed_game.py',"bpy.ops.object.mode_set(mode='OBJECT')", """for name in ['front_wheel','rear_wheel_l','rear_wheel_r']:
    source=rig.data.edit_bones[name]
    contact=rig.data.edit_bones.new(name+'_contact')
    contact.head=source.head;contact.tail=source.tail;contact.parent=root
bpy.ops.object.mode_set(mode='OBJECT')""")

p='Scripts/Game/ORD/ORD_TerminalComponent.c'
edit(p,'protected ref map<string, bool> m_Keys', 'protected ref ORD_MissionMap m_MissionMap;\n protected ref map<string, bool> m_Keys')
edit(p,'bool foundEngine, foundZoomIn, foundZoomWheel;', 'bool foundEngine, foundZoomIn, foundZoomOut, foundZoomWheel, foundWheelOut;')
edit(p,'if (input.GetActionName(j) == "ORD_ZoomIn") foundZoomIn = true;', 'if (input.GetActionName(j) == "ORD_ZoomIn") foundZoomIn = true;\n   if (input.GetActionName(j) == "ORD_ZoomOut") foundZoomOut = true;\n   if (input.GetActionName(j) == "ORD_ZoomWheelOut") foundWheelOut = true;')
edit(p,'!foundEngine || !foundZoomIn || !foundZoomWheel','!foundEngine || !foundZoomIn || !foundZoomOut || !foundZoomWheel || !foundWheelOut')
edit(p,'void Close()\n {','void Close()\n {\n  CloseMissionMap();\n  ResetZoomInput();')
edit(p,'m_bMap = false;\n   if (m_bPilot)', 'CloseMissionMap(); ResetZoomInput();\n   if (m_bPilot)')
edit(p,'m_bMap = !m_bMap;\n   if (m_bMap) { m_vMapCenter = drone.GetOrigin(); player.ORD_Send(drone, ORD_Command.SENSOR); }', '''ResetZoomInput();
   if (m_bMap) CloseMissionMap();
   else
   {
    m_MissionMap = new ORD_MissionMap();
    m_bMap = m_MissionMap.Open(m_Drone);
    if (m_bMap) player.ORD_Send(drone, ORD_Command.SENSOR);
   }''')
s=(R/p).read_text();a=s.index('  if (m_bMap)\n  {\n   float mapPanX');b=s.index('  else if (m_bPilot)',a)
s=s[:a]+'''  if (m_bMap)
  {
   if (m_MissionMap) m_MissionMap.Update(timeSlice);
   HideContacts();
   return;
  }
'''+s[b:];(R/p).write_text(s)
a='''   if (input.GetActionValue("ORD_ZoomIn") > 0.5) m_fZoom = Math.Min(40, m_fZoom * (1 + timeSlice * 2.5));
   if (input.GetActionValue("ORD_ZoomOut") > 0.5) m_fZoom = Math.Max(1, m_fZoom / (1 + timeSlice * 2.5));
   if (input.GetActionValue("ORD_ZoomWheelIn") > 0) m_fZoom = Math.Min(40, m_fZoom * 1.6);
   if (input.GetActionValue("ORD_ZoomWheelOut") > 0) m_fZoom = Math.Max(1, m_fZoom / 1.6);'''
edit(p,a,'''   float zoomAxis = Math.AbsFloat(input.GetActionValue("ORD_ZoomIn")) - Math.AbsFloat(input.GetActionValue("ORD_ZoomOut"));
   float wheelAxis = Math.AbsFloat(input.GetActionValue("ORD_ZoomWheelIn")) - Math.AbsFloat(input.GetActionValue("ORD_ZoomWheelOut"));
   m_fZoom = Math.Clamp(m_fZoom * Math.Pow(2.7182818, Math.Clamp(zoomAxis, -1, 1) * Math.Min(timeSlice, 0.1) * 2.5 + Math.Clamp(wheelAxis, -1, 1) * 0.35), 1, 40);
   input.ResetAction("ORD_ZoomWheelIn"); input.ResetAction("ORD_ZoomWheelOut");''')
edit(p,'if (Pressed(input, "ORD_Fire")) player.ORD_FireAt(drone, m_Camera.GetTransformAxis(2));', '''if (Pressed(input, "ORD_Fire"))
   {
    if (m_Drone.Tracking()) player.ORD_Weapon(drone, ORD_TargetMode.VEHICLE, vector.Zero);
    else player.ORD_FireAt(drone, m_Camera.GetTransformAxis(2));
   }''')
edit(p,'protected void UpdateMapMarkers()', '''protected void ResetZoomInput()
 {
  InputManager input = GetGame().GetInputManager();
  input.ResetAction("ORD_ZoomIn"); input.ResetAction("ORD_ZoomOut");
  input.ResetAction("ORD_ZoomWheelIn"); input.ResetAction("ORD_ZoomWheelOut");
 }
 protected void CloseMissionMap()
 {
  if (m_MissionMap) m_MissionMap.Close();
  m_MissionMap = null; m_bMap = false;
 }
 protected void UpdateMapMarkers()''')
edit(p,'m_fThrottle = 0; m_fHeartbeat = 0;', 'ResetZoomInput(); m_fZoom = 1;\n  m_fThrottle = 0; m_fHeartbeat = 0;')
