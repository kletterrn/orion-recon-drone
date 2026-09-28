# RC8 camera placement — 2026-09-28

Requested: fixed forward flight view from the pictured optical unit; sensor view through the rotating lens.

Implemented in the current RC8 project, preserving its newer model/audio work:

- `ORD_CameraMounts.c`: shared client/server mounting geometry measured from evaluated optical surfaces in `Orion_RC8_Motion_v022.blend`. Flight origin uses the upper optical opening at local `(0.06721,-0.66366,2.335)`. Sensor origin uses the main opening at rest `(-0.05795,-0.75486,2.340)`, articulated around the actual pitch/yaw pivots. Both sit slightly ahead of the glass.
- `ORD_TerminalComponent.c`: aircraft-aligned forward flight camera, articulated sensor origin, consistent tracking look vector. Camera direction now respects the visible gimbal's existing aircraft-relative limits: yaw ±120°, elevation -80° to +35°. Stabilization works within those limits; aircraft movement can push the gimbal against a stop.
- `ORD_AircraftComponent.c`: server observation/tracking rays use the same mounting calculation instead of the old fixed point. Camera position does not depend on renderer bone updates on a headless server.
- `ORD_AircraftVisuals.c`: return the optical unit to neutral forward orientation in flight-view mode.

The existing static exported view markers remain in the asset for compatibility; the active views now use the shared mounting calculation. The Blender inspection did not save or modify any model. Original edited scripts are backed up under `Integration/RC8/Backups/CameraPlacement-20260928`.

## Observed validation

| Check | Result |
| --- | --- |
| Workbench compilation / clean packaging | PASS — Game CRC a9bd4fbf, packaging successful. |
| Packed bytes match current source | PASS — 127 files checked among 194 resources. No test fixture in the clean package. |
| Actual terminal flight view | PASS — camera at requested unit, forward vector `(0,0,1)` with level aircraft. |
| Actual terminal sensor view | PASS — -30° downward view has articulated origin, clear scene image. |
| Panned sensor view | PASS — 65° yaw / -50° elevation, different lens origin and clear image. |
| Return from sensor to flight view | PASS — returns to identical forward mount. |
| Runtime script exceptions during fixture | PASS — none observed; all four camera origin comparisons report zero error. |
| Sustained flight, extreme gimbal positions, banked aircraft, multiplayer | NOT RUN — background fixture holds the aircraft stationary and level. |

Screenshots in this folder are lossless conversions of actual engine captures. The flight image naturally includes the underside of the nose along its upper edge because the camera is physically beneath it. The pilot HUD's existing presentation was not reworked in this change.

Clean packed delivery: `ReleaseCandidates/Orion-E-rc8-camera-placement-packed.zip`. Test bootstrap/capture scripts are source-only `.c.txt` files; they are not included in the addon PAK. Publication excluded.
