from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'Scripts/Game/ORD/ORD_AircraftComponent.c'; s=p.read_text(encoding='utf-8')
s=s.replace('m_iAmmo = 2','m_iAmmo = 1').replace('two missiles, weapon safe','one missile, weapon safe')
s=s.replace('if (m_iAmmo == 1) station = 1;','// The single store always uses station zero.')
s=s.replace('if (m_iAmmo == 2 && m_StoreLeft)','if (m_StoreLeft)')
s=s.replace('if (m_iAmmo >= 2 && !m_StoreLeft)','if (m_iAmmo >= 1 && !m_StoreLeft)')
s=s.replace('  if (m_iAmmo >= 1 && !m_StoreRight) m_StoreRight = SpawnStore(resource, 3.2);','  // No second mounted store: capacity is one in every flight and service state.')
p.write_text(s,encoding='utf-8')
p=R/'Scripts/Game/ORD/ORD_GuidedMissile.c'; s=p.read_text(encoding='utf-8')
s=s.replace('[Attribute("160")]','[Attribute("300")]').replace('[Attribute("75")]','[Attribute("120")]').replace('[Attribute("8")]','[Attribute("25")]')
s=s.replace('{D3F38F8AA37B77E8}Particles/Weapon/Explosion_M72LAW.ptc','{79ED2EDBC38185AB}Particles/Logistics/Explosion/TNT/Explosion_TNT_Large.ptc')
s=s.replace('{16913A6D6A54BD5B}Sounds/Particles/Logistics/Explosion/TNT/Particles_Explosions_TNT_Small.acp','{E4EF3755472EC669}Sounds/Particles/Logistics/Explosion/TNT/Particles_Explosions_TNT_Large.acp')
p.write_text(s,encoding='utf-8')
p=R/'Scripts/Game/ORD/ORD_TerminalComponent.c'; s=p.read_text(encoding='utf-8')
s=s.replace('bool cruise = running && m_Drone.Speed() > 30;','bool cruise = running && (m_Drone.Throttle > 0.45 || m_Drone.Speed() > 35);')
s=s.replace('FrameSlot.SetOffsets(widget, screen[0] - halfWidth, screen[1] - halfHeight, screen[0] + halfWidth, screen[1] + halfHeight);','FrameSlot.SetAnchorMin(widget,0,0); FrameSlot.SetAnchorMax(widget,0,0);\n  FrameSlot.SetSize(widget,halfWidth*2,halfHeight*2);\n  FrameSlot.SetPos(widget,screen[0]-halfWidth,screen[1]-halfHeight);')
s=s.replace('float panX = input.GetActionValue("ORD_CamRight") - input.GetActionValue("ORD_CamLeft");','// Screen-direction controls: right increases bearing; up raises elevation.\n   float panX = Math.AbsFloat(input.GetActionValue("ORD_CamRight")) - Math.AbsFloat(input.GetActionValue("ORD_CamLeft"));')
s=s.replace('float panY = input.GetActionValue("ORD_CamUp") - input.GetActionValue("ORD_CamDown");','float panY = Math.AbsFloat(input.GetActionValue("ORD_CamUp")) - Math.AbsFloat(input.GetActionValue("ORD_CamDown"));')
s=s.replace('else if (m_fContactScan >= 0.4) { m_fContactScan = 0; UpdateContacts(horizontalFOV, aspect); }','else if (m_fContactScan >= 0.1) { m_fContactScan = 0; UpdateContacts(horizontalFOV, aspect); }')
# One box per visible person rather than collapsing neighbouring people into one marker.
s=s.replace('if (vector.Distance(people[groupIndex], point) < 14)','if (m_Drone.ContactState() == ORD_ContactState.GROUP && vector.Distance(people[groupIndex], point) < 14)')
p.write_text(s,encoding='utf-8')
p=R/'UI/ORD/Contact.layout'
p.write_text('''FrameWidgetClass {
 Name "ORD_Contact" "Ignore Cursor" 1
 Slot FrameWidgetSlot { Anchor 0 0 0 0 OffsetLeft 0 OffsetTop 0 SizeX 80 OffsetRight -80 SizeY 80 OffsetBottom -80 }
 {
  TextWidgetClass {
   Name "ContactLabel" Color 0.35 1 0.55 1 "Font Size" 14 Text "CONTACT" "Ignore Cursor" 1
   Slot FrameWidgetSlot { Anchor 0 0 0 0 OffsetLeft 0 OffsetTop -23 SizeX 200 OffsetRight -200 SizeY 23 OffsetBottom 0 }
  }
  PanelWidgetClass {
   Name "Top" Color 0.35 1 0.55 1 "Ignore Cursor" 1
   Slot FrameWidgetSlot { Anchor 0 0 1 0 OffsetLeft 0 OffsetTop 0 OffsetRight 0 SizeY 2 OffsetBottom -2 }
  }
  PanelWidgetClass {
   Name "Bottom" Color 0.35 1 0.55 1 "Ignore Cursor" 1
   Slot FrameWidgetSlot { Anchor 0 1 1 1 OffsetLeft 0 OffsetTop -2 OffsetRight 0 SizeY 2 OffsetBottom 0 }
  }
  PanelWidgetClass {
   Name "Left" Color 0.35 1 0.55 1 "Ignore Cursor" 1
   Slot FrameWidgetSlot { Anchor 0 0 0 1 OffsetLeft 0 OffsetTop 0 SizeX 2 OffsetRight -2 OffsetBottom 0 }
  }
  PanelWidgetClass {
   Name "Right" Color 0.35 1 0.55 1 "Ignore Cursor" 1
   Slot FrameWidgetSlot { Anchor 1 0 1 1 OffsetLeft -2 OffsetTop 0 SizeX 2 OffsetRight 0 OffsetBottom 0 }
  }
 }
}
''',encoding='utf-8')
