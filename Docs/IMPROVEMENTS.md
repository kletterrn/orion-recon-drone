# Orion improvement priorities

The starting point is RC9 development source, commit a61d72b. Existing RC9 acceptance failures and untested gameplay remain recorded in ACCEPTANCE.md.

## Implemented: mission planning feedback

- Route planning now shows horizontal circuit distance and estimated time at the draft's selected cruise speed. The estimate includes the last-to-first leg. It excludes the aircraft's approach, climb, wind and curved turns; it is not a fuel/endurance prediction or a measured arrival time.
- Empty, single-point and coincident routes show no circuit estimate. The map explains when another waypoint is needed.
- The summary labels applied, unapplied and pending drafts, and warns when the server has a newer route revision.
- The live waypoint field is blank when no route is being flown. Its number refers to the accepted mission, including while a replacement draft is edited.
- Selecting an existing waypoint preserves its coordinate. A drag begins only after more than four screen pixels of movement, avoiding unintended edits from clicks and small hand movement.

## Sensor-linked reconnaissance

The 2026-09-29 follow-up implements the sensor-linked map, frozen faction reconnaissance cards, experimental EO/IR composition and an optional wide inset. See [RECON_SUITE.md](RECON_SUITE.md) for controls and [validation](ReconSuiteEvidence/validation.md) for evidence and the simultaneous-render fallback.

## Next useful improvements

The 2026-09-29 follow-up adds three persistent route slots, undo/redo, route reversal and map centering. See [ROUTE_TOOLS.md](ROUTE_TOOLS.md) for controls and validation.

1. **Thermal contrast calibration.** Resolve the recorded black-hot dawn failure with comparison captures of personnel, vehicles and background across the existing weather/time matrix. Keep the daylight return and white-hot regression gates.
2. **Operator flight warnings.** Add restrained fuel, terrain-clearance and link-margin advisories to the flight and sensor displays. Use sustained thresholds and recovery hysteresis so messages do not flicker. Derive thresholds from the game's flight model and test taxi/takeoff/landing separately.
3. **Extend saved mission presets.** Three numbered local slots are implemented. A later pass can add custom names, separate per-world libraries and import/export after testing the current profile persistence during ordinary play.
4. **Multiplayer session reliability.** Exercise operator death, reconnect, competing terminal claims and late join with two clients. Verify camera restoration, weapon safing, remote visibility and cleanup. The current acceptance record says a second player client is unavailable.
5. **Performance and controller pass.** Measure sensor CPU cost and object/handler counts during a 30-minute session before optimizing contact drawing. Add controller bindings with actual device testing and clear on-screen prompts.

## Verification

The isolated native-engine fixture is `Tools/Tests/ORD_MissionPlannerProbe.c.txt`. It checks circuit geometry, time formatting and waypoint click/drag behavior without injecting physical input. Build it only into a separate fixture package; never distribute that package. Compilation, clean packaging and fixture results are recorded separately from rendered UI and physical-input acceptance.

Recorded on 2026-09-28 with Arma Reforger 1.8.0.13:

- PASS: all 12 distinct native-engine planner checks; no recorded script errors during the 25-second fixture run. The scenario invokes the fixture on two terminals, so the log contains two copies of each check.
- PASS: 1080p rendered map inspection. The summary shows the expected 1.2 km / 0:30 triangular draft, fits inside its panel and leaves the existing controls accessible. This scripted capture does not establish physical mouse behavior.
- PASS: clean Workbench packaging and 198/198 packed resource byte matches, with no test/editor sources.
- PASS: clean packed startup reached GAME state with no recorded script errors during a 20-second smoke run.
- NOT RUN: physical mouse/controller acceptance, full flight regression, multiplayer and other display resolutions. Existing RC9 thermal and multiplayer gates remain open.

Machine-readable results are in `Docs/PlannerEvidence/`. Native logs and screenshot are retained in `C:/Users/david/Desktop/OrionV2Builds/`: `planner-fixture-02`, `planner-visual` and `planner-release`. The first fixture compilation failed because a test variable used the reserved name `map`; the corrected fixture compiled and all checks passed.

The distributable development package is `ReleaseCandidates/Orion-E-rc9-planner-dev-packed.zip`. Extract it into a separate addon directory and keep only one active copy of the Orion addon GUID. Existing external dependencies remain required. The package is not Workshop-published.

Reproduce the checks using new empty output directories outside the source tree:

```powershell
python Tools/release.py build --output C:/OrionBuild/planner-test --fixture Tools/Tests/ORD_MissionPlannerProbe.c.txt
python Tools/run_game.py --build C:/OrionBuild/planner-test --seconds 25 --headless --expect 'ORD_TEST_DONE mission-planner'
python Tools/release.py build --output C:/OrionBuild/planner-visual --fixture Tools/Tests/ORD_RC7OperatorProbe.c.txt --fixture Tools/Tests/ORD_MissionPlannerVisualProbe.c.txt
python Tools/run_game.py --build C:/OrionBuild/planner-visual --seconds 40 --expect 'ORD_TEST_DONE planner-visual'
python Tools/release.py build --output C:/OrionBuild/planner-clean
node Tools/verify_package.mjs C:/OrionBuild/planner-clean
python Tools/run_game.py --build C:/OrionBuild/planner-clean --seconds 20 --headless
```

