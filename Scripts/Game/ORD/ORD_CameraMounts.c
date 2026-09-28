// RC8 v022 optical surfaces measured from evaluated source geometry.
// Blender (x,y,z) maps to Enfusion (x,z,y). Origins sit just outside the glass.
// Use the same analytic articulation on clients and headless servers: renderer
// bone matrices are not a reliable authoritative observation origin.
class ORD_CameraMounts
{
 static vector Forward(float yaw, float pitch)
 {
  return Vector(Math.Sin(yaw*Math.DEG2RAD)*Math.Cos(pitch*Math.DEG2RAD),Math.Sin(pitch*Math.DEG2RAD),Math.Cos(yaw*Math.DEG2RAD)*Math.Cos(pitch*Math.DEG2RAD));
 }
 static vector PilotOrigin(IEntity aircraft)
 {
  // Forward view at the upper optical opening, fixed to aircraft attitude.
  return aircraft.CoordToParent("0.06721 -0.66366 2.335");
 }
 static void Angles(IEntity aircraft, vector direction, out float yaw, out float elevation)
 {
  vector matrix[4]; aircraft.GetTransform(matrix);
  vector local = Vector(vector.Dot(direction,matrix[0]),vector.Dot(direction,matrix[1]),vector.Dot(direction,matrix[2]));
  yaw = Math.Clamp(Math.Atan2(local[0],local[2])*Math.RAD2DEG,-120,120);
  elevation = Math.Clamp(Math.Atan2(local[1],Math.Sqrt(local[0]*local[0]+local[2]*local[2]))*Math.RAD2DEG,-80,35);
 }
 static vector Constrain(IEntity aircraft, vector direction)
 {
  float yaw, elevation; Angles(aircraft,direction,yaw,elevation);
  vector matrix[4]; aircraft.GetTransform(matrix);
  vector local=Forward(yaw,elevation);
  vector world=matrix[0]*local[0]+matrix[1]*local[1]+matrix[2]*local[2];
  world.Normalize(); return world;
 }
 static vector SensorOrigin(IEntity aircraft, vector direction)
 {
  float yaw, elevation; Angles(aircraft,direction,yaw,elevation);
  vector lens[4]; Math3D.MatrixIdentity4(lens);
  lens[3] = "-0.05795 -0.75486 2.340";
  ORD_RC8Rig.RotateAround(lens,"0 -0.73 2.05","-1 0 0",elevation);
  ORD_RC8Rig.RotateAround(lens,"0 -0.35 2.05","0 1 0",yaw);
  return aircraft.CoordToParent(lens[3]);
 }
}
