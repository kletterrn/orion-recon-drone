// Server-guided game projectile. Values are playability estimates, not Banderol flight data.
class ORD_BanderolComponentClass : ScriptComponentClass {}
class ORD_BanderolComponent : ScriptComponent
{
 [Attribute("150")] protected float m_fCruiseSpeed;
 [Attribute("40")] protected float m_fLifetime;
 [Attribute("160")] protected float m_fDirectDamage;
 [Attribute("75")] protected float m_fBlastDamage;
 [Attribute("8")] protected float m_fBlastRadius;
 protected vector m_vTarget, m_vVelocity;
 protected vector m_vImpact;
 protected IEntity m_Aircraft;
 protected bool m_bLaunched;
 protected float m_fAge;

 override void OnPostInit(IEntity owner)
 {
  super.OnPostInit(owner);
  SetEventMask(owner, EntityEvent.FRAME);
 }

 void Launch(IEntity aircraft, vector target, vector inheritedVelocity)
 {
  if (!Replication.IsServer() || !aircraft) return;
  m_Aircraft = aircraft;
  m_vTarget = target;
  m_vVelocity = inheritedVelocity + aircraft.GetTransformAxis(2) * 80 - Vector(0, 10, 0);
  m_bLaunched = true;
 }

 override void EOnFrame(IEntity owner, float timeSlice)
 {
  if (!Replication.IsServer() || !m_bLaunched) return;
  m_fAge += timeSlice;
  if (m_fAge > m_fLifetime) { SCR_EntityHelper.DeleteEntityAndChildren(owner); return; }
  vector origin = owner.GetOrigin();
  vector toTarget = m_vTarget - origin;
  if (toTarget.Length() > 2 && m_fAge > 0.6)
  {
   vector desired = toTarget.Normalized() * m_fCruiseSpeed;
   m_vVelocity = vector.Lerp(m_vVelocity, desired, Math.Clamp(timeSlice * 1.5, 0, 1));
  }
  else if (m_fAge <= 0.6) m_vVelocity[1] = m_vVelocity[1] - 9.81 * timeSlice;
  vector next = origin + m_vVelocity * timeSlice;
  TraceParam trace = new TraceParam();
  trace.Start = origin; trace.End = next; trace.Flags = TraceFlags.WORLD | TraceFlags.ENTS;
  trace.Exclude = owner;
  float hitFraction = owner.GetWorld().TraceMove(trace, null);
  if (hitFraction < 1)
  {
   if (trace.TraceEnt == m_Aircraft && m_fAge < 1) { owner.SetOrigin(next); return; }
   m_vImpact = origin + (next - origin) * hitFraction;
   IEntity hit = trace.TraceEnt;
   for (int i = 0; i < 4 && hit; i++)
   {
    SCR_DamageManagerComponent damage = SCR_DamageManagerComponent.Cast(hit.FindComponent(SCR_DamageManagerComponent));
    if (damage && damage.GetDefaultHitZone()) { damage.GetDefaultHitZone().HandleDamage(m_fDirectDamage, EDamageType.KINETIC, null); break; }
    hit = hit.GetParent();
   }
   owner.GetWorld().QueryEntitiesBySphere(m_vImpact, m_fBlastRadius, BlastCandidate, null, EQueryEntitiesFlags.DYNAMIC);
   SCR_EntityHelper.DeleteEntityAndChildren(owner);
   return;
  }
  Physics physics = owner.GetPhysics();
  if (physics) physics.SetVelocity(m_vVelocity);
  owner.SetAngles(m_vVelocity.VectorToAngles() + Vector(0, -90, 0));
 }

 protected bool BlastCandidate(IEntity entity)
 {
  if (!entity || entity == GetOwner() || entity == m_Aircraft) return true;
  if (!ChimeraCharacter.Cast(entity) && !Vehicle.Cast(entity)) return true;
  SCR_DamageManagerComponent damage = SCR_DamageManagerComponent.Cast(entity.FindComponent(SCR_DamageManagerComponent));
  if (!damage || !damage.GetDefaultHitZone()) return true;
  vector sample = entity.GetOrigin();
  if (ChimeraCharacter.Cast(entity)) sample[1] = sample[1] + 1;
  float distance = vector.Distance(m_vImpact, sample);
  if (distance >= m_fBlastRadius) return true;
  TraceParam visibility = new TraceParam();
  visibility.Start = m_vImpact + Vector(0, 0.5, 0);
  visibility.End = sample;
  visibility.Flags = TraceFlags.WORLD | TraceFlags.ENTS;
  visibility.Exclude = GetOwner();
  float fraction = GetOwner().GetWorld().TraceMove(visibility, null);
  if (fraction < 0.98)
  {
   IEntity blocker = visibility.TraceEnt;
   bool sameEntity;
   for (int i = 0; i < 4 && blocker; i++)
   {
    if (blocker == entity) { sameEntity = true; break; }
    blocker = blocker.GetParent();
   }
   if (!sameEntity) return true;
  }
  damage.GetDefaultHitZone().HandleDamage(m_fBlastDamage * (1 - distance / m_fBlastRadius), EDamageType.KINETIC, null);
  return true;
 }
}
