from pathlib import Path
p=Path('Prefabs/ORD/ORD_Aircraft.et');s=p.read_text();s=s.replace('{9E31A4C705ECBD82}Assets/ORD/Models/OrionE_Game/ORD_Orion_Detailed.xob','{63E70502EA1FCF67}Assets/ORD/Models/RC8/ORD_Orion_RC8_Probe.xob');s=s.replace('  ORD_AircraftVisuals {}','  ORD_AircraftVisuals {}\n  ORD_AudioPresentation {}\n  SoundComponent { Filenames { "{4B25B09A31945782}Sounds/ORD/RC8/ORD_Orion_RC8.acp" } }');p.write_text(s)
for n in ['ORD_Banderol','ORD_BanderolStore']:
 p=Path('Prefabs/ORD/'+n+'.et');s=p.read_text().replace('{0B02A7C868F7549D}Assets/ORD/Models/ORD_Missile.xob','{B84F5EBBB009A23F}Assets/ORD/Models/RC8/ORD_Banderol_RC8_Probe.xob');s=s.replace('  RplComponent {}','  RplComponent {}\n  ORD_BanderolPresentation {}');
 if n=='ORD_Banderol':s=s.replace('  ORD_GuidedMissile {}','  ORD_GuidedMissile {}\n  SignalsManagerComponent {}\n  SoundComponent { Filenames { "{97BA0B2CA879CD12}Sounds/ORD/RC8/ORD_Banderol_RC8.acp" } }')
 p.write_text(s)
