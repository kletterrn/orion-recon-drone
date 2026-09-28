from pathlib import Path
p=Path('Scripts/Game/ORD/ORD_GuidedMissile.c');s=p.read_text(encoding='utf-8-sig');s=s.replace(' [RplProp()] protected float m_fAge;',' [RplProp()] protected float m_fAge;\n [RplProp()] protected float m_fDeploymentStart = -1;\n int PresentationState() { return m_iState; }\n float FlightAge() { return m_fAge; }\n float DeploymentStart() { return m_fDeploymentStart; }')
a=s.index('   if (m_fAge < 1)');b=s.index('\n  }\n  else',a);s=s[:a]+s[b:]
s=s.replace('    vector transform[4]; Math3D.MatrixIdentity4(transform); transform[3] = m_vPosition;\n    AudioSystem.PlayEvent("{E4EF3755472EC669}Sounds/Particles/Logistics/Explosion/TNT/Particles_Explosions_TNT_Large.acp","SOUND_EXPLOSION",transform);','    // Synthetic impact audio is owned by the presentation adapter.')
s=s.replace('  m_fNetwork += dt;','  UpdateVisualClearance();\n  m_fNetwork += dt;')
pos=s.index(' protected IEntity DamageEntity(')
s=s[:pos]+''' // Conservative visual envelope only; never affects projectile flight or damage.
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
'''+s[pos:];p.write_text(s,encoding='utf-8')
