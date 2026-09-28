from pathlib import Path
R=Path(__file__).resolve().parents[1]
buttons=[('RouteTool','Route'),('LoiterTool','Loiter'),('WeaponTool','Weapon target'),('Delete','Delete point'),('Earlier','Move earlier'),('Later','Move later'),('AltMinus','Altitude -'),('AltPlus','Altitude +'),('SpeedMinus','Speed -'),('SpeedPlus','Speed +'),('RadiusMinus','Radius -'),('RadiusPlus','Radius +'),('Apply','Apply route'),('Fly','Fly route'),('Loiter','Loiter here'),('Resume','Resume route'),('Reload','Reload accepted'),('Clear','Clear route'),('Arm','Arm / Safe'),('Fire','Launch at target')]
def slot(x,y,w,h): return f'Slot FrameWidgetSlot {{ Anchor 0 0 0 0 OffsetLeft {x} OffsetTop {y} SizeX {w} OffsetRight {-x-w} SizeY {h} OffsetBottom {-y-h} }}'
s='''FrameWidgetClass {
 Name "ORD_MissionMap" "Z Order" 1000
 Slot FrameWidgetSlot { Anchor 0 0 1 1 OffsetLeft 0 OffsetTop 0 OffsetRight 0 OffsetBottom 0 }
 {
  CanvasWidgetClass {
   Name "MissionCanvas" "Ignore Cursor" 0
   Slot FrameWidgetSlot { Anchor 0 0 1 1 OffsetLeft 0 OffsetTop 0 OffsetRight 0 OffsetBottom 0 }
   FontProperties { FontProperties { Font "{3E7733BAC8C831F6}UI/Fonts/RobotoCondensed/RobotoCondensed_Regular.fnt" } }
  }
  FrameWidgetClass {
   Name "MissionPanel"
'''+slot(20,40,340,900)+'''
   {
    ImageWidgetClass { Name "PanelBackground" "Ignore Cursor" 1 Color 0.02 0.035 0.045 0.96
     Slot FrameWidgetSlot { Anchor 0 0 1 1 OffsetLeft 0 OffsetTop 0 OffsetRight 0 OffsetBottom 0 }
    }
    TextWidgetClass { Name "MissionStatus" "Font Size" 17 Color 1 1 1 1 Text "ORION MISSION"
'''+slot(12,12,316,295)+'''
    }
'''
for i,(name,label) in enumerate(buttons):
 x=12+(i%2)*160;y=315+(i//2)*48
 s+=f'''ButtonWidgetClass {{ Name "{name}" Color 0.16 0.23 0.28 1 {slot(x,y,152,42)}
 {{ TextWidgetClass {{ Name "Label{name}" Text "{label}" "Font Size" 17 Color 1 1 1 1 "Ignore Cursor" 1 Slot ButtonWidgetSlot {{ HorizontalAlign 3 VerticalAlign 3 Padding 6 8 6 6 }} }} }}
 }}\n'''
s+='''TextWidgetClass { Name "Help" Wrap 1 Text "Click: add/select | Drag: move | Right drag: pan | Wheel: zoom | M / Esc: return to sensor" "Font Size" 15 Color 0.7 0.8 0.85 1
'''+slot(12,806,316,80)+''' }
   }
  }
 }
}
'''
(R/'UI/ORD/MissionMap.layout').write_text(s)
(R/'UI/ORD/MissionMap.layout.meta').write_text('MetaFileClass { Name "{A3F84D861D444A20}UI/ORD/MissionMap.layout" Configurations { LayoutResourceClass PC {} } }\n')
