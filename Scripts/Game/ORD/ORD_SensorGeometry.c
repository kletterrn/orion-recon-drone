class ORD_SensorGeometry
{
 static bool Ray(IEntity aircraft, vector origin, vector direction, float range, out vector point)
 {
  TraceParam trace=new TraceParam(); trace.Start=origin; trace.End=origin+direction.Normalized()*range;
  trace.Flags=TraceFlags.WORLD|TraceFlags.ENTS; trace.Exclude=aircraft;
  float hit=aircraft.GetWorld().TraceMove(trace,null); point=trace.Start+(trace.End-trace.Start)*hit;
  return hit<1;
 }
 // Four surface rays approximate the frustum footprint, not visibility of every pixel.
 static bool Footprint(IEntity aircraft, vector pose[4], float hfov, float aspect, float range, array<vector> output)
 {
  output.Clear(); float h=Math.Tan(hfov*Math.DEG2RAD*0.5), v=h/Math.Max(aspect,0.5);
  for(int i=0;i<4;i++)
  {
   float x=1,y=1; if(i==0 || i==3)x=-1; if(i>=2)y=-1;
   vector direction=(pose[2]+pose[0]*h*x+pose[1]*v*y).Normalized(); vector point;
   if(!Ray(aircraft,pose[3],direction,range,point)) { output.Clear(); return false; }
   output.Insert(point);
  }
  return true;
 }
}
