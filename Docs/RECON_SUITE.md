# Sensor-linked reconnaissance suite — RC9 development

Implemented directly in the existing RECON DRONES project. This extends the saved-route tools; it does not change the remaining RC9 flight, thermal-calibration or multiplayer acceptance gates.

## Operator controls

- Open the operator map with **M**. Its default click action now points the sensor at the clicked terrain position. Select **Route**, **Loiter** or **Weapon target** to use those existing tools, or **Point sensor** to resume camera pointing.
- The muted interaction accent shows the aircraft and camera direction. The muted blue trail retains up to 120 one-second samples from the current operator session, including pilot mode. The matching outline estimates the four corners of the camera's view using surface raycasts, updated four times per second.
- The footprint is an estimate, not proof that every object inside is visible. It is hidden if a corner reaches sky or exceeds sensor range. Camera movement respects the existing gimbal limits. Manual sensor movement, recentering and tracking commands release map-point focus.
- Aim at a surface, open the map, enter an optional note (160 characters maximum), select an **estimated** category and choose **Save current sighting**. Saving uses the current optical ray, not the map cursor. There is a two-second save interval.
- Click a report marker or select it with **Previous / Next**. **Show observation** centers the map and, for the active operator, aims at the saved coordinate. The camera does not reacquire or follow the original object automatically.
- Any living player with a faction can use **Review faction reconnaissance** at a terminal to open the report map without claiming the aircraft. Only that player's faction reports are returned. Reports refresh every two seconds while the map is open.
- **N** cycles EO, white-hot, black-hot and experimental EO/IR blending. The map's **Blend** button toggles the experimental mode directly.
- **Inset** cycles the default map schematic, experimental wide video and off. Insets appear at 5x zoom and above. The video rectangle represents the main sensor's narrower field of view; the wide view stays between 1x and 4x. The default schematic uses no additional scene camera. Blended mode automatically substitutes the schematic when video is selected: simultaneous extra views caused HUD rendering artifacts in testing. Video resumes when blending is disabled.

## Observation semantics and limits

Each card contains an immutable position, native map grid, server simulation timestamp, elapsed age, operator name, note and user-selected estimated category. It stores no entity reference and never updates its position after creation. **LAST OBSERVED** is always shown. Categories are human estimates, not automatic identification.

The server validates aircraft ownership, link, sensor mode, faction, direction length, category and note length, then traces the surface from the aircraft's optical mount. A miss does not create a report. Clients cannot submit a saved position, timestamp, author or faction. Owner-only replies carry the newest 16 reports for the current faction, with a global 128-card bound. Cards last for the current mission; they are not persistent intelligence records. Faction changes clear the local display before the next refresh.

There are **no image thumbnails**. Engine evidence captures whole application screenshots locally. That does not establish a suitable sensor-only capture and multiplayer thumbnail transport path. Those remain deferred pending a separate capture test.

EO/IR blending and the extra video inset are experimental mod display features, **not confirmed Orion capabilities**. They use the existing simulated thermal presentation; they are not radiometric temperature measurements. Blending attenuates the main thermal image and adds a weighted daylight render at half resolution, capped at 30 FPS. The wide video target is capped at 15 FPS; rapid movement can reveal update latency. The extra views reserve local camera slots 30 and 31 while operating. Closing the terminal, opening the map or entering pilot view detaches the render targets. Other mods using those slots need compatibility testing.

## Interface references

- [QGroundControl video display](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/fly_view/video.html): integrated map/video context and switching inspired the sensor-linked map workflow.
- [L3Harris WESCAM MX-15](https://www.l3harris.com/all-capabilities/wescam-mx-15-air-surveillance-and-reconnaissance): documented EO/IR blending is inspiration for an experimental display, not evidence about Orion equipment.
- [Enfusion RenderTargetWidget API](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/interfaceRenderTargetWidget.html): native render targets, refresh limits and compositing controls.

## Validation

Final build results, rendering evidence, cost samples and remaining acceptance limits are recorded in `ReconSuiteEvidence/validation.md`. Test fixtures belong only in isolated packages, never in the distributable addon.

```powershell
python Tools/release.py build --output C:/OrionBuild/recon-test --fixture Tools/Tests/ORD_RC7OperatorProbe.c.txt --fixture Tools/Tests/ORD_ReconSuiteProbe.c.txt
python Tools/run_game.py --build C:/OrionBuild/recon-test --seconds 80 --fps 240 --expect 'ORD_TEST_DONE recon-reader'
python Tools/release.py build --output C:/OrionBuild/recon-clean
node Tools/verify_package.mjs C:/OrionBuild/recon-clean
python Tools/run_game.py --build C:/OrionBuild/recon-clean --seconds 55 --headless
```

Use fresh output directories and run game scenarios sequentially. The fixture holds the aircraft at a fixed airborne pose to isolate camera geometry and rendering; it does not validate flight. Two-client delivery, late join, disconnects, physical input and sustained GPU profiling need live acceptance.
