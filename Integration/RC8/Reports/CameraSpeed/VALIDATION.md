# RC8 high-speed optical camera fix — 2026-09-28

The camera sampled the aircraft mount in terminal FRAME, before physics advanced the aircraft. The independent camera entity then rendered at the old position. The measured lag followed speed multiplied by frame duration.

## Change

- Added `ORD_OpticalCamera`, which refreshes the mount in camera POSTFRAME and submits the transform with the native `ApplyTransform` API.
- The terminal still processes input and preliminary aim in FRAME. The final optical pose is recalculated after aircraft movement for both flight and sensor views.
- Sensor contact projection runs after camera submission, so boxes use the current view.
- Mount coordinates, gimbal limits and aircraft physics are unchanged. Source backup: `Integration/RC8/Backups/CameraSpeed-20260928`.
- API and engine camera implementations inspected through Enfusion MCP/local PAK tooling.

## Observed tests

Real packed game, local server/client, fresh profiles, background window. Test-only bootstrap acquires a real operator and opens the terminal. The moving fixture starts at altitude, sets velocity to 80 m/s each frame and suppresses angular velocity; physics still advances the aircraft. This is a controlled moving-body regression, not a manual flight acceptance test.

| Check | Result |
| --- | --- |
| Before fix, moving sensor | Reproduced: 13 logged samples, rendered/entity mount errors 0.262–0.759 m at about 288 km/h. |
| After fix, moving flight view | PASS: five logged samples, rendered and entity origin errors both 0 m. |
| After fix, moving sensor view | PASS: eight logged samples, rendered and entity origin errors both 0 m; yaw 25°, elevation -30°. |
| Screenshot review | PASS: flight mount and clear sensor image at displayed 288 km/h. Flight view retains the physical nose along the upper edge. |
| Test completion / script exceptions | `ORD_SPEED_DONE`; no script errors observed. |
| Clean Workbench compile/package | PASS: Game CRC `cb4cf86a`; packaging successful. |
| Packed integrity | PASS: 128 exact source matches among 195 resources. Test scripts excluded. |
| Remote client, network correction, low frame rates, sustained manoeuvres, physical input | NOT RUN. |

The before-run bootstrap selected sensor mode, so its file named SPEED_FLIGHT was also a sensor capture; no before-flight result is claimed. The after fixture explicitly selects pilot mode after bootstrap. Evidence: `before.log`, `after.log`, `FLIGHT.png`, `SENSOR.png`, `build.log`, and `packed-integrity.json`.

Delivery: `ReleaseCandidates/Orion-E-rc8-camera-speed-fix-packed.zip`. Publication excluded.
