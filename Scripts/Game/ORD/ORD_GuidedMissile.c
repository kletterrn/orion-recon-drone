// Server-authoritative game projectile with replicated flight/impact state.
class ORD_GuidedMissileClass : ScriptGameComponentClass {}
class ORD_GuidedMissile : ScriptGameComponent
{
 override event bool OnTicksOnRemoteProxy() { return true; }
 protected bool m_RelevancyConfigured;
 [Attribute("150")] protected float m_fCruiseSpeed;
 [Attribute("45")] protected float m_fLifetime;
 [Attribute("300")] protected float m_fDirectDamage;
 [Attribute("120")] protected float m_fBlastDamage;
 [Attribute("25")] protected float m_fBlastRadius;
 [Attribute("20")] protected float m_fVehicleDamageMultiplier;
 protected vector m_vLastTrackSample;
 protected bool m_bTrackSample;
 [RplProp()] protected vector m_vPosition;
 [RplProp()] protected vector m_vVelocity;
 [RplProp()] protected int m_iState;
 protected vector m_vTarget, m_vImpact;
 protected IEntity m_Aircraft, m_Tracked;
 protected int m_Operator, m_LocalState;
 [RplProp()] protected float m_fAge;
 [RplProp()] protected float m_fDeploymentStart = -1;
 int PresentationState() { return m_iState; }
 float FlightAge() { return m_fAge; }
 float DeploymentStart() { return m_fDeploymentStart; }
 protected float  m_fNetwork, m_fFinished;
 protected ParticleEffectEntity m_Trail;
 protected ref array<IEntity> m_Damaged = {};
 override void OnPostInit(IEntity owner) { super.OnPostInit(owner); SetEventMask(owner, EntityEvent.FRAME); }
 void Launch(IEntity aircraft, vector target, vector inheritedVelocity, IEntity tracked = null, int operatorId = 0)
 {
  if (!Replication.IsServer() || !aircraft) return;
  m_Aircraft = aircraft; m_Tracked = tracked; m_Operator = operatorId;
  m_vTarget = target; m_vPosition = GetOwner().GetOrigin();
  m_vVelocity = inheritedVelocity + aircraft.GetTransformAxis(2)*30-Vector(0,6,0);
  m_iState = 1; Replication.BumpMe();
 }
 protected ParticleEffectEntity Effect(ResourceName resource, bool follow)
 {
  ParticleEffectEntitySpawnParams params = new ParticleEffectEntitySpawnParams();
  params.TargetWorld = GetOwner().GetWorld(); params.TransformMode = ETransformMode.WORLD;
  Math3D.MatrixIdentity4(params.Transform); params.Transform[3] = m_vPosition;
  params.PlayOnSpawn = true; params.DeleteWhenStopped = true; params.UseFrameEvent = true;
  if (follow) params.FollowParent = GetOwner();
  return ParticleEffectEntity.SpawnParticleEffect(resource,params);
 }
 protected void LocalEffects()
 {
  if (System.IsConsoleApp() || m_LocalState == m_iState) return;
  m_LocalState = m_iState;
  if (m_iState == 1)
  {
   m_Trail = Effect("{0F364F4CD1D72350}Particles/Weapon/Trail_PG7VL.ptc",true);

  }
  else
  {
   if (m_Trail) { m_Trail.StopEmission(); m_Trail = null; }
   GetOwner().SetScale(0.001);
   if (m_iState == 2)
   {
    Effect("{79ED2EDBC38185AB}Particles/Logistics/Explosion/TNT/Explosion_TNT_Large.ptc",false);
    // Synthetic impact audio is owned by the presentation adapter.
   }
  }
 }
 override void OnDelete(IEntity owner) { if (m_Trail) m_Trail.StopEmission(); super.OnDelete(owner); }
 override void EOnFrame(IEntity owner, float timeSlice)
 {
  if (!m_RelevancyConfigured)
  {
   RplComponent replication = RplComponent.Cast(owner.FindComponent(RplComponent));
   if (replication && replication.Id().IsValid())
   {
    // Operators may be kilometres from the aircraft and its projectile.
    replication.EnableSpatialRelevancy(false); replication.EnableStreaming(false);
    m_RelevancyConfigured = true;
   }
  }
  float dt = timeSlice;
  if (!Replication.IsServer())
  {
   if (m_iState > 0) { owner.SetOrigin(m_vPosition); if (m_vVelocity.LengthSq() > 1) owner.SetAngles(m_vVelocity.VectorToAngles()); }
   LocalEffects(); return;
  }
  if (m_iState == 0) return;
  if (m_iState > 1) { LocalEffects(); m_fFinished += dt; if (m_fFinished > 3) SCR_EntityHelper.DeleteEntityAndChildren(owner); return; }
  float remaining = Math.Min(dt,0.25);
  while (remaining > 0 && m_iState == 1) { float step = Math.Min(remaining,0.02); remaining -= step; Step(step); }
  owner.SetOrigin(m_vPosition);
  if (m_vVelocity.LengthSq() > 1) owner.SetAngles(m_vVelocity.VectorToAngles());
  UpdateVisualClearance();
  m_fNetwork += dt;
  if (m_fNetwork >= 0.05) { m_fNetwork = 0; Replication.BumpMe(); }
  LocalEffects();
 }
 // Conservative visual envelope only; never affects projectile flight or damage.
 protected void UpdateVisualClearance()
 {
  if(m_fDeploymentStart>=0 || !m_Aircraft || m_iState!=1)return;
  vector lo="100000 100000 100000",hi="-100000 -100000 -100000";
  for(int i=0;i<8;i++)
  {
   float x=-1.1,y=-0.273,z=-2.2;
   if(i & 1)x=1.1;if(i & 2)y=0.46;if(i & 4)z=2.2;
   vector p=m_Aircraft.CoordToLocal(GetOwner().CoordToParent(Vector(x,y,z)));
   for(int j=0;j<3;j++) { lo[j]=Math.Min(lo[j],p[j]);hi[j]=Math.Max(hi[j],p[j]); }
  }
  vector bodyLo,bodyHi;m_Aircraft.GetBounds(bodyLo,bodyHi);
  bool separate=false;
  for(int k=0;k<3;k++) if(hi[k]<bodyLo[k]-0.15 || lo[k]>bodyHi[k]+0.15)separate=true;
  if(separate) { m_fDeploymentStart=m_fAge;Replication.BumpMe(); }
 }
 protected IEntity DamageEntity(IEntity entity)
 {
  IEntity fallback;
  for (int i = 0; i < 10 && entity; i++)
  {
   if (entity.FindComponent(SCR_DamageManagerComponent))
   {
    if (Vehicle.Cast(entity) || ChimeraCharacter.Cast(entity)) return entity;
    if (!fallback) fallback=entity;
   }
   IEntity parent=entity.GetParent(); if(parent==entity) break; entity=parent;
  }
  return fallback;
 }
 protected void Step(float dt)
 {
  m_fAge += dt;
  if (m_fAge > m_fLifetime) { m_iState = 3; Replication.BumpMe(); return; }
  if (!m_Tracked && m_bTrackSample) { m_vTarget=m_vLastTrackSample; m_bTrackSample=false; }
  if (m_Tracked)
  {
   SCR_DamageManagerComponent health = SCR_DamageManagerComponent.Cast(m_Tracked.FindComponent(SCR_DamageManagerComponent));
   TraceParam sight = new TraceParam(); sight.Start = m_vPosition; sight.End = m_Tracked.GetOrigin()+Vector(0,0.7,0);
   sight.Flags = TraceFlags.WORLD | TraceFlags.ENTS;
   ref array<IEntity> sightExcluded = {GetOwner()}; if(m_fAge < 1 && m_Aircraft) sightExcluded.Insert(m_Aircraft); sight.ExcludeArray=sightExcluded;
   float visible = GetOwner().GetWorld().TraceMove(sight,null);
   if ((!health || !health.IsDestroyed()) && (visible >= 0.99 || DamageEntity(sight.TraceEnt) == m_Tracked))
   {
    m_vTarget = sight.End;
    if(m_bTrackSample && dt>0)
    {
     vector motion=(sight.End-m_vLastTrackSample)/dt;
     Physics trackedPhysics=m_Tracked.GetPhysics();
     if(trackedPhysics) motion=trackedPhysics.GetVelocity();
     if(motion.Length()<80) m_vTarget += motion*Math.Clamp(vector.Distance(m_vPosition,sight.End)/m_fCruiseSpeed,0,1);
    }
    m_vLastTrackSample=sight.End; m_bTrackSample=true;
   }
   else { if(m_bTrackSample) m_vTarget=m_vLastTrackSample; m_Tracked = null; }
  }
  vector toTarget = m_vTarget-m_vPosition;
  // Increase game steering near impact so a moving target is not overshot.
  float steering = 1.5+4.5*Math.Clamp((200-toTarget.Length())/200,0,1);
  if (m_fAge > 0.6 && toTarget.LengthSq() > 0.01) m_vVelocity = vector.Lerp(m_vVelocity,toTarget.Normalized()*m_fCruiseSpeed,Math.Clamp(dt*steering,0,1));
  else m_vVelocity[1] = m_vVelocity[1]-9.81*dt;
  vector next = m_vPosition+m_vVelocity*dt;
  TraceParam trace = new TraceParam(); trace.Start = m_vPosition; trace.End = next; trace.Flags = TraceFlags.WORLD | TraceFlags.ENTS;
  ref array<IEntity> excluded = {GetOwner()}; if (m_fAge < 1 && m_Aircraft) excluded.Insert(m_Aircraft); trace.ExcludeArray = excluded;
  float fraction = GetOwner().GetWorld().TraceMove(trace,null);
  if (fraction < 1) { m_vPosition = trace.Start+(trace.End-trace.Start)*fraction; Impact(trace.TraceEnt); return; }
  m_vPosition = next;
 }
 protected void Damage(IEntity entity, float amount)
 {
  SCR_DamageManagerComponent manager = SCR_DamageManagerComponent.Cast(entity.FindComponent(SCR_DamageManagerComponent));
  if (!manager || !manager.GetDefaultHitZone()) return;
  IEntity instigator = GetGame().GetPlayerManager().GetPlayerControlledEntity(m_Operator); if (!instigator) instigator = m_Aircraft;
  if(Vehicle.Cast(entity)) amount *= m_fVehicleDamageMultiplier;
  manager.GetDefaultHitZone().HandleDamage(amount,EDamageType.EXPLOSIVE,instigator);
 }
 protected void Impact(IEntity hit)
 {
  if (m_iState != 1) return;
  m_iState = 2; m_vImpact = m_vPosition; m_vVelocity = vector.Zero;
  IEntity direct = DamageEntity(hit); if (direct) { Damage(direct,m_fDirectDamage); m_Damaged.Insert(direct); }
  GetOwner().GetWorld().QueryEntitiesBySphere(m_vImpact,m_fBlastRadius,BlastCandidate,null,EQueryEntitiesFlags.DYNAMIC);
  Replication.BumpMe();
 }
 protected bool BlastCandidate(IEntity candidate)
 {
  IEntity entity = DamageEntity(candidate);
  if (!entity || entity == GetOwner() || m_Damaged.Contains(entity)) return true;
  if (!ChimeraCharacter.Cast(entity) && !Vehicle.Cast(entity)) return true;
  vector sample = entity.GetOrigin()+Vector(0,0.7,0);
  float distance = vector.Distance(m_vImpact,sample); if (distance >= m_fBlastRadius) return true;
  TraceParam sight = new TraceParam(); sight.Start = m_vImpact+Vector(0,0.3,0); sight.End = sample;
  sight.Flags = TraceFlags.WORLD | TraceFlags.ENTS; sight.Exclude = GetOwner();
  float fraction = GetOwner().GetWorld().TraceMove(sight,null);
  if (fraction < 0.98 && DamageEntity(sight.TraceEnt) != entity) return true;
  m_Damaged.Insert(entity); Damage(entity,m_fBlastDamage*(1-distance/m_fBlastRadius)); return true;
 }
}



