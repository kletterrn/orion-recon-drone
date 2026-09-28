# 1.0.0-rc8 — 2026-09-28

- Integrate the approved Orion and 4.4 m VisualFit Banderol meshes as native skinned model resources, with four LODs, collision proxies, attachment helpers and converted materials.
- Add presentation animation for Orion gear, doors, wheels, propeller, control surfaces and optical turret, plus illustrative Banderol wing deployment after visual clearance.
- Place the carried Banderol and projectile at the same centreline socket; keep the pylon on Orion after launch.
- Add synthetic spatial engine/projectile audio, gear and deployment cues, and a quieter local operator feed.
- Preserve the existing flight, targeting, HUD, thermal, launch and damage logic. See VALIDATION_RC8.md for checks and remaining live-test limits.

# 1.0.0-rc7 — 2026-09-27

- Add a separate transparent sensor HUD matching the supplied reference composition, with fixed-width white text, outlined native geometry and a smoothly scrolling LOS azimuth tape.
- Bind horizontal ground speed, ocean-referenced altitude, terrain clearance, actual camera FOV/elevation, elapsed simulation time, native map grid and optical-axis slant range.
- Project visible entity bounds each frame; retain the existing bounded, occlusion-tested detection scan. Give contacts stable local IDs and replicate only the selected entity identifier needed for accurate client presentation.
- Keep pilot/map displays and flight, Overwatch, camera input, zoom, thermal and tracking behavior intact. Distinguish coasting/lost tracks and clear the overlay on exit.
- See VALIDATION_RC7.md for actual engine screenshots and verification limits.

# 1.0.0-rc6 — 2026-09-27

- Isolate flight altitude/speed arrow bindings from sensor arrows; use explicit up/down/left/right camera input signs.
- Build the sensor camera transform directly from bearing/elevation, correcting the swapped native camera axes and contact projection.
- Carry and reload one Banderol missile on the existing left station. A successful launch leaves zero mounted stores and no ammunition.
- Replace the small rocket impact with the native large TNT visual and sound. Game-balanced damage: 300 direct, 120 blast, 25 m obstructed blast radius.
- Replace the sine-tone engine samples with original layered piston/propeller loops; high-load selection follows throttle as well as speed.
- Correct contact widget positioning and sizing, draw full green rectangular outlines, refresh at 10 Hz, and show separate personnel boxes outside group-tracking mode.
# 1.0.0-rc5 — 2026-09-27

- Isolate relative sensor mouse actions, consume deltas once, reset aim/zoom on mode changes and gaps, and keep native map input separate. Add explicit Y targeting-mode selection.
- Restore offline operator commands where placed entities have no replication ID. Remove a duplicate aircraft controller in the runway scenario.
- Correlate route acknowledgements with submitted requests; retain rejected drafts and wait for accepted replicated state. Synchronize radius and remote sensor direction.
- Correct navigation heading and bank direction, add turn-lift compensation and altitude/speed trim, and guide loiter with a tangent and radius correction.
- Improve final game-projectile steering and use tracked vehicle velocity for the moving-target lead.
- Enable remote visual/projectile ticks and projectile relevance; add service failure feedback and typed weapon validation.
- Validate background packed-engine flight, zoom, map and weapon integration with real operator ownership. See VALIDATION_RC5.md for measured results and outstanding hands-on/multiplayer acceptance.
# 1.0.0-rc4 — 2026-09-26

- Repair animated bind-space offsets and authored flap/aileron hinges; separate suspension contact bones from visual wheel bones.
- Unify missile mount/launch hardpoints and sensor camera/server trace origin.
- Correct heading axis and sensor camera direction; reversible 1–40× zoom with signed wheel normalization, one-time wheel consumption and lifecycle resets.
- Native terrain map with eight-point local drafts, atomic validated submission, revision checks, server snapshots, continuous routes, loiter and resume.
- Authored Banderol game mesh, typed targets, server projectile movement, swept collision, armor-aware direct/blast damage, effects and cleanup.
- Correct zero terminal collider mass found during runtime testing.
- Add isolated engine regression fixtures and explicit acceptance report. Multiplayer and full piloted acceptance remain required.

# Changelog

## 1.0.0-rc3 â€” 2026-09-25

- Fixed sensor and map zoom input so held keys change magnification continuously and mouse wheel movement is applied on each input update.
- Added numpad plus/minus bindings, a prominent sensor zoom readout outside the crowded telemetry block, and a Flight-camera prompt to switch to the zoomable Sensor view.
- Calculated sensor field of view from the requested optical magnification rather than dividing degrees directly. The rendered 40Ã— view still needs interactive confirmation.

## 1.0.0-rc2 â€” 2026-09-25

- Restored the requested S-up/W-down pitch keys and matching on-screen/keybinding labels.
- Added an overhead mission-map crosshair, visible numbered waypoint and loiter markers, preflight waypoint selection, independent map zoom, and route activation without overwriting selected points.
- Extended the sensor camera to 40Ã— zoom.
- Restyled camera telemetry and contact corners in white, and clustered nearby visible personnel into counted boxes.
- Added a server-validated missile shot at the visible reticle point, with HUD launch/rejection status. Actual missile flight, impact and damage remain to be tested in-game.

## 1.0.0-rc1 â€” 2026-09-25

- Mapped W to nose-up and S to nose-down in the drone flight input and keybind labels, following the latest release request. Physical response still requires an in-game flight test.
- Preserved an active Overwatch/autopilot mode when switching from Sensor back to Flight. Manual movement input remains the explicit takeover path.
- Hardened terminal camera startup and release checks during interrupted sessions.
- Made the operator HUD distinguish measured ground speed from airspeed, removed a false recording indicator, and added explicit target-loss feedback.
- Filtered contact brackets for characters parented under vehicles, lifted vehicle sample points above their origin, and kept full brackets inside the visible screen.
- Disabled periodic demo-world aircraft diagnostics by default.
- Retained the previously requested missile code as experimental; no weapon behavior is accepted for v1 without gameplay validation.

Earlier development work added the camera overlay, zoom/pan bindings, point and entity tracking, group tracking, contact brackets, and the missile prototype. Those features were compiled and packaged previously, but most remain unverified in interactive play.


