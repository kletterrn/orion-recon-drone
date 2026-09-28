class ORD_FlightControllerClass : PFC_FlightControllerClass {}
class ORD_FlightController : PFC_FlightController
{
 protected ORD_AircraftComponent m_ORD;
 // PFC calls this on each physics step. No native seat or client authority is needed.
 override void PollInput(float timeSlice)
 {
  if (!Replication.IsServer()) return;
  if (!m_ORD) m_ORD = ORD_AircraftComponent.Cast(GetOwner().FindComponent(ORD_AircraftComponent));
  if (!m_ORD) return;
  m_ORD.Simulate(timeSlice);
  m_fPitchInput = MoveTowards(m_fPitchInput, m_ORD.Pitch, timeSlice * 0.7);
  m_fRollInput = MoveTowards(m_fRollInput, m_ORD.Roll, timeSlice);
  m_fYawInput = MoveTowards(m_fYawInput, m_ORD.Yaw, timeSlice * 1.5);
  if (m_ORD.EngineOn()) m_fThrottle = m_ORD.Throttle;
  else m_fThrottle = 0;
  VehicleWheeledSimulation wheels = VehicleWheeledSimulation.Cast(GetOwner().FindComponent(VehicleWheeledSimulation));
  if (wheels)
  {
   wheels.SetThrottle(0);
   wheels.SetSteering(-m_fYawInput);
   wheels.SetBreak(m_ORD.Brake, m_ORD.Brake > 0.9);
  }
 }
 override void ApplyGroundSteering() {}
 override void UpdateMouseFlight(float timeSlice) {}
 // Disable the inherited seat-input RPC path for this unmanned aircraft.
 protected override void RpcSrv_ReceiveInputs(float pitch, float roll, float yaw, float throttle) {}
}
