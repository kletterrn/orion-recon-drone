# Saved routes and mission editing — 2026-09-29

This development candidate extends the previous planner improvements in the existing RECON DRONES project. It does not close the RC9 thermal, flight or multiplayer acceptance gates in ACCEPTANCE.md.

## New controls

| Control | Behavior |
| --- | --- |
| Undo edit / Redo edit | Restore waypoint and altitude/speed/radius edits, including reversals and loaded drafts; up to 20 undo steps. A new edit clears redo. |
| Reverse route | Reverse the waypoint order while retaining the selected geographic point. Apply is required before the active mission changes. |
| Center aircraft / Center home | Pan to the aircraft or its home position while preserving target zoom. |
| Local slot 1 / 3 | Cycle among three player-profile storage slots. |
| Save draft | Save points, world identity, altitude, speed and orbit radius. Click again within five seconds to overwrite an occupied slot. |
| Load draft | Load a validated preset into the local draft. Review and Apply explicitly; loading never sends flight or weapon commands. Undo restores the replaced draft. |

The profile stores `ORD_RouteSlot1.json` through `ORD_RouteSlot3.json`. These slots are shared across worlds within that profile, but a route from another world cannot be loaded. Saving another world's route into the same slot overwrites it after confirmation. No filenames come from user-entered text. Slots are not synchronized to other players.

Empty routes, more than eight points, unsupported schema versions, missing fields and out-of-range settings are rejected. Loading also checks terrain bounds and the current aircraft-relative planning range using the existing validation policy. The server still validates Apply. Loading does not update the draft's base revision, so a concurrent server change cannot silently bypass revision validation.

Undo history belongs to the open map session and is cleared when accepted server state is loaded. A drag counts as one edit, and selection-only clicks do not create edits. Applying, flying, clearing the live mission and other server commands are not undoable local edits. Save/load/reverse edits are blocked while a submitted draft awaits a server response.

## Evidence

- PASS: 31 distinct headless native checks: 12 existing planner regressions and 19 new history/serialization/validation checks. The 55-second run reached GAME with no script errors.
- PASS: 13 rendered handler checks in the final 1080p run, including saving, overwrite confirmation, loading as a draft, undo/redo, pending-command guards, no live mission change and aircraft centering (4.27 m world-space center error at 0.12 pixels/metre).
- PASS: visual inspection of the planner panels at 1080p and 1440p. The 1440p capture came from the initial handler run; the final isolated centering measurement was at 1080p.
- PASS: clean Workbench build; all 199 packed resources match staged bytes, with no test/editor sources. A sequential 55-second clean headless rerun reached GAME with no recorded script errors.
- PASS: the ZIP's two entries match the verified clean packed addon. Package: `ReleaseCandidates/Orion-E-rc9-route-tools-dev-packed.zip`; SHA-256 `3b5c66a14f744898ad3133412d7c15cbbf6b2ac766379a514c7b3d0fb8a355e4`.

Native-engine and package evidence is retained under `C:/Users/david/Desktop/OrionV2Builds/features-20260929-*`. Machine-readable results are copied into `Docs/RouteToolsEvidence/`.

The native fixtures use the real Enforce code and JSON file serialization. The rendered fixture invokes the real button handlers with test widgets and records engine screenshots; it does not inject physical mouse or controller input. Test files are isolated from the distributable package.

Initial validation found and corrected a reserved Enforce field name (`World`, renamed `WorldPath`). A 25-second headless run reached GAME but ended before its delayed checks; the retained longer rerun is the policy evidence. Early visual checks invoked centering before map initialization; the final fixture waits for map initialization and measures centering separately.

An intermediate centering check drifted under native map input. The final visual fixture removes only native pan/zoom input listeners after initialization and retains the engine registration attribute on its test-only module override. Intermediate versions without that attribute failed to instantiate the native map module; those fixture failures are retained in the external build logs. A concurrent clean smoke run could not bind the shared server port; its sequential rerun passed. Run engine scenarios sequentially on this setup. Final capture: `features-20260929-visual5/game-60-1920x1080/profile/PlannerDraft.bmp.bmp`.

The release has no map-input override. Extract the development ZIP into a separate addon directory; keep only one active copy of the Orion addon GUID and retain the existing external dependencies. No Workshop publication was performed.

Physical mouse/controller operation, full piloted flight, dedicated multiplayer, profile persistence across an ordinary user session restart and prolonged performance remain unverified. Existing thermal limitations remain unchanged.

## Reproduction

Use new empty output directories outside the source tree and configure `local.build.json` as described in BUILD.md.

```powershell
python Tools/release.py build --output C:/OrionBuild/route-policy --fixture Tools/Tests/ORD_RouteToolsProbe.c.txt --fixture Tools/Tests/ORD_MissionPlannerProbe.c.txt
python Tools/run_game.py --build C:/OrionBuild/route-policy --seconds 55 --headless --expect 'ORD_TEST_DONE route-tools' --expect 'ORD_TEST_DONE mission-planner'
python Tools/release.py build --output C:/OrionBuild/route-visual --fixture Tools/Tests/ORD_RC7OperatorProbe.c.txt --fixture Tools/Tests/ORD_MissionPlannerVisualProbe.c.txt
python Tools/run_game.py --build C:/OrionBuild/route-visual --seconds 55 --expect 'ORD_TEST_PASS visual-center-aircraft' --expect 'ORD_TEST_DONE planner-visual'
python Tools/release.py build --output C:/OrionBuild/route-clean
node Tools/verify_package.mjs C:/OrionBuild/route-clean
python Tools/run_game.py --build C:/OrionBuild/route-clean --seconds 55 --headless
```
