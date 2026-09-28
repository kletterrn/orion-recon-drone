class ORD_OpticalCameraClass : SCR_CameraBaseClass {}

// Resolve the optical mount after physics, immediately before camera submission.
// Sampling in terminal FRAME leaves the view behind by velocity * frame time.
class ORD_OpticalCamera : SCR_CameraBase
{
 protected ORD_TerminalComponent m_Terminal;

 void Bind(ORD_TerminalComponent terminal)
 {
  m_Terminal = terminal;
  SetFlags(EntityFlags.ACTIVE);
  SetEventMask(EntityEvent.POSTFRAME);
 }

 override protected void EOnPostFrame(IEntity owner, float timeSlice)
 {
  if (!m_Terminal) return;
  m_Terminal.UpdateOpticalPose(timeSlice);
  ApplyTransform(timeSlice);
  m_Terminal.ProjectOpticalContacts();
 }
}
