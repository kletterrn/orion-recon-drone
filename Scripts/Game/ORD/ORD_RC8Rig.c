// Native import verified: model coordinates are Blender (x,z,y). SetBoneMatrix takes a bind-local offset.
class ORD_RC8Key
{
 vector P;
 float Q[4];
 void ORD_RC8Key(string text)
 {
  array<string> v={};text.Split(" ",v,true);
  P=Vector(v[0].ToFloat(),v[1].ToFloat(),v[2].ToFloat());
  for(int i=0;i<4;i++)Q[i]=v[i+3].ToFloat();
 }
}
class ORD_RC8Curve
{
 ref array<ref ORD_RC8Key> Keys={};
 void ORD_RC8Curve(string text)
 {
  array<string> rows={};text.Split(";",rows,true);
  foreach(string row:rows) Keys.Insert(new ORD_RC8Key(row));
 }
 void Sample(float phase,out vector pose[4])
 {
  float t=Math.Clamp(phase,0,1)*(Keys.Count()-1);int a=Math.Floor(t);int b=Math.Min(a+1,Keys.Count()-1);float q[4];
  Math3D.QuatLerp(q,Keys[a].Q,Keys[b].Q,t-a);vector rot[3];Math3D.QuatToMatrix(q,rot);
  pose[0]=rot[0];pose[1]=rot[1];pose[2]=rot[2];pose[3]=vector.Lerp(Keys[a].P,Keys[b].P,t-a);
 }
}
class ORD_RC8Bone
{
 TNodeId Id;
 vector Bind[4];
 bool Valid;
}
class ORD_RC8Rig
{
 static ref map<string,ref ORD_RC8Curve> Curves;
 protected IEntity m_Owner;
 protected ref map<string,ref ORD_RC8Bone> m_Bones=new map<string,ref ORD_RC8Bone>();
 void ORD_RC8Rig(IEntity owner)
 {
  m_Owner=owner;
  if(!Curves) { Curves=new map<string,ref ORD_RC8Curve>();ORD_RC8PoseData.Populate(Curves); }
  Animation anim=owner.GetAnimation();if(!anim)return;
  array<string> names={};anim.GetBoneNames(names);
  foreach(string name:names)
  {
   ORD_RC8Bone bone=new ORD_RC8Bone();bone.Id=anim.GetBoneIndex(name);bone.Valid=anim.GetBoneMatrix(bone.Id,bone.Bind);m_Bones.Insert(name,bone);
  }
 }
 bool Rest(string name,out vector pose[4])
 {
  ORD_RC8Bone b=m_Bones.Get(name);if(!b || !b.Valid)return false;
  for(int i=0;i<4;i++)pose[i]=b.Bind[i];return true;
 }
 bool Sample(string name,float phase,out vector pose[4])
 {
  ORD_RC8Curve curve=Curves.Get(name);if(curve) { curve.Sample(phase,pose);return true; }
  return Rest(name,pose);
 }
 void Apply(string name,vector pose[4])
 {
  ORD_RC8Bone b=m_Bones.Get(name);if(!b || !b.Valid || !m_Owner)return;
  vector delta[4];Math3D.MatrixInvMultiply4(b.Bind,pose,delta);m_Owner.GetAnimation().SetBoneMatrix(m_Owner,b.Id,delta);
 }
 static void RotateAround(inout vector pose[4],vector pivot,vector axis,float degrees)
 {
  axis.Normalize();float x=axis[0],y=axis[1],z=axis[2];float c=Math.Cos(degrees*Math.DEG2RAD),s=Math.Sin(degrees*Math.DEG2RAD),t=1-c;
  vector r[3];r[0]=Vector(t*x*x+c,t*x*y+s*z,t*x*z-s*y);r[1]=Vector(t*x*y-s*z,t*y*y+c,t*y*z+s*x);r[2]=Vector(t*x*z+s*y,t*y*z-s*x,t*z*z+c);
  for(int i=0;i<3;i++)pose[i]=pose[i].Multiply3(r);pose[3]=pivot+(pose[3]-pivot).Multiply3(r);
 }
 void Rotation(string name,vector axis,float degrees)
 {
  vector pose[4];if(!Rest(name,pose))return;RotateAround(pose,pose[3],axis,degrees);Apply(name,pose);
 }
 static bool Socket(IEntity owner,string name,out vector pose[4])
 {
  if(!owner || !owner.GetAnimation())return false;
  TNodeId boneIndex=owner.GetAnimation().GetBoneIndex(name);
  if(boneIndex<0)return false;
  return owner.GetAnimation().GetBoneMatrix(boneIndex,pose);
 }
}

