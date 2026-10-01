// Optional local rendering prototype. Camera slots 30/31 are reserved while open.
class ORD_SensorDisplay
{
 protected Widget m_Root, m_Inset, m_Attenuation;
 protected World m_Scene;
 protected RenderTargetWidget m_Blend, m_Wide;
 protected CanvasWidget m_Box;
 protected TextWidget m_Label;
 protected ref array<ref CanvasWidgetCommand> m_Draw = {};
 int InsetMode = 1; // 0 off, 1 low-cost map schematic, 2 experimental video
 bool Open()
 {
  m_Root=GetGame().GetWorkspace().CreateWidgets("{9B3EE60890DA461E}UI/ORD/SensorDisplay.layout"); if(!m_Root)return false;
  m_Attenuation=m_Root.FindAnyWidget("ThermalWeight");
  m_Blend=RenderTargetWidget.Cast(m_Root.FindAnyWidget("EOBlend"));
  m_Wide=RenderTargetWidget.Cast(m_Root.FindAnyWidget("WideVideo"));
  m_Inset=m_Root.FindAnyWidget("OrientationInset"); m_Box=CanvasWidget.Cast(m_Root.FindAnyWidget("OrientationDraw"));
  m_Label=TextWidget.Cast(m_Root.FindAnyWidget("OrientationLabel"));
  // Attenuate the main IR image, then add weighted EO. Secondary scene alpha
  // is not suitable for ordinary RTW alpha blending on the tested renderer.
  m_Blend.SetClearColor(true,0xFF000000);
  m_Blend.SetColorInt(0xFFFFFFFF);
  m_Blend.SetFormat(RenderTargetWidgetFormat.DEFAULT);
  m_Blend.SetBlendMode(RenderTargetWidgetBlendMode.ADDITIVE);
  m_Blend.SetFlags(WidgetFlags.BLEND); m_Blend.SetOpacity(0.45);
  m_Blend.SetResolutionScale(0.5,0.5); m_Blend.SetMaxFPS(30);
  m_Wide.SetResolutionScale(1,1); m_Wide.SetMaxFPS(15);
  Hide(); return true;
 }
 void Hide()
 {
  if(!m_Root)
  {
   return;
  }
  m_Root.SetVisible(false);
  m_Blend.SetWorld(null,0); m_Wide.SetWorld(null,0);
 }
 void Close()
 {
  Hide();
  if(m_Scene)
  {
   m_Scene.SetCameraPostProcessEffect(30,10,PostProcessEffectType.HDR,string.Empty);
   m_Scene.SetCameraPostProcessEffect(31,10,PostProcessEffectType.HDR,string.Empty);
  }
  m_Scene=null;
  if(m_Root)m_Root.RemoveFromHierarchy(); m_Root=null;
 }
 protected void Line(float x1,float y1,float x2,float y2,int color=0xFFFFFFFF)
 {
  LineDrawCommand line=new LineDrawCommand(); line.m_iColor=color; line.m_fWidth=2;
  line.m_Vertices={x1,y1,x2,y2}; m_Draw.Insert(line);
 }
 void Update(IEntity aircraft, SCR_CameraBase camera, float zoom, bool blend, bool visible, array<vector> footprint)
 {
  if(!m_Root)return;
  if(!visible) { Hide(); return; }
  m_Root.SetVisible(true); m_Blend.SetVisible(blend); m_Attenuation.SetVisible(blend);
  World scene=aircraft.GetWorld(); vector pose[4]; camera.GetTransform(pose);
  if(m_Scene!=scene)
  {
   m_Scene=scene;
   scene.SetCameraPostProcessEffect(30,10,PostProcessEffectType.HDR,"{8C54D3F019AC426E}Assets/ORD/SensorDisplayHDR.emat");
   scene.SetCameraPostProcessEffect(31,10,PostProcessEffectType.HDR,"{8C54D3F019AC426E}Assets/ORD/SensorDisplayHDR.emat");
  }
  float exposure=scene.GetCameraHDRBrightness(camera.GetCameraIndex());
  scene.SetCameraHDRBrightness(30,exposure); scene.SetCameraHDRBrightness(31,exposure);
  if(blend)
  {
   scene.SetCameraEx(30,pose); scene.SetCameraVerticalFOV(30,camera.GetVerticalFOV());
   scene.SetCameraNearPlane(30,0.1); scene.SetCameraFarPlane(30,5000); m_Blend.SetWorld(scene,30);
  }
  else m_Blend.SetWorld(null,0);
  bool show=InsetMode>0 && zoom>=5; m_Inset.SetVisible(show); m_Wide.SetVisible(show && InsetMode==2 && !blend);
  m_Draw.Clear();
  if(!show) { m_Wide.SetWorld(null,0); return; }
  float width,height; m_Box.GetScreenSize(width,height);
  if(InsetMode==2 && !blend)
  {
   float wideZoom=Math.Max(1,Math.Min(4,zoom/4));
   float wideHFOV=ORD_ObservationPolicy.HorizontalFOV(wideZoom);
   scene.SetCameraEx(31,pose); scene.SetCameraVerticalFOV(31,2*Math.Atan2(Math.Tan(wideHFOV*Math.DEG2RAD*0.5),width/height)*Math.RAD2DEG);
   scene.SetCameraNearPlane(31,0.1); scene.SetCameraFarPlane(31,5000); m_Wide.SetWorld(scene,31);
   float ratio=wideZoom/zoom; float screenW,screenH; GetGame().GetWorkspace().GetScreenSize(screenW,screenH);
   float rw=width*ratio, rh=rw/(screenW/screenH);
   float x=(width-rw)*0.5,y=(height-rh)*0.5;
   Line(x,y,x+rw,y); Line(x+rw,y,x+rw,y+rh); Line(x+rw,y+rh,x,y+rh); Line(x,y+rh,x,y);
   m_Label.SetText(string.Format("WIDE EO %1x | 15 FPS | EXPERIMENTAL",ORD_SensorHUD.Decimal(wideZoom)));
  }
  else
  {
   m_Wide.SetWorld(null,0); vector origin=aircraft.GetOrigin(); float scale=width/4000;
   Line(width/2,0,width/2,height,0xFF607078); Line(0,height/2,width,height/2,0xFF607078);
   Line(width/2-5,height/2,width/2+5,height/2,0xFFB4D1CB); Line(width/2,height/2-5,width/2,height/2+5,0xFFB4D1CB);
   vector forward=camera.GetTransformAxis(2);
   Line(width/2,height/2,width/2+forward[0]*60,height/2-forward[2]*60,0xFFB4D1CB);
   if(footprint.Count()==4)
    for(int i=0;i<4;i++)
    {
     vector a=footprint[i]-origin,b=footprint[(i+1)%4]-origin;
     Line(Math.Clamp(width/2+a[0]*scale,0,width),Math.Clamp(height/2-a[2]*scale,0,height),Math.Clamp(width/2+b[0]*scale,0,width),Math.Clamp(height/2-b[2]*scale,0,height),0xFFE5BE78);
    }
   string label="N UP | 4 KM SCHEMATIC | EST. FOOTPRINT";
   if(blend && InsetMode==2)label="SCHEMATIC | VIDEO PAUSED DURING BLEND";
   m_Label.SetText(label);
  }
  m_Box.SetDrawCommands(m_Draw);
 }
}
