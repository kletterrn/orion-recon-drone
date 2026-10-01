# Orion operator polish pass - 2026-09-29

Implementation and available validation complete for this bounded pass. Development candidate; production release acceptance remains blocked by the gates below.

## Working state and design

Work directly in RECON DRONES, preserving earlier uncommitted recon/planner changes. No commits, installs, global configuration changes or publication. Baseline source and manifest: C:/Users/david/Desktop/OrionV2Builds/polish-baseline/stage. No applicable ancestor/project AGENTS.md found. Installed Obsidian registry targets the older MCP Arma checkout; its old state was read as history, not current authority. This is the single progress record. Serena is not exposed; Enforce work uses native source/SDK tools.

[BULKHEAD WARDOGS overview](https://bulkhead.com/games/wardogs/) informs the tactical/teamwork brief only. Native Enfusion/Enforce and project-owned/base-game assets throughout.

## Issue inventory and disposition

| Evidence | Component / symbol | Finding and change |
|---|---|---|
| Code defect, engine-tested | Terminal.Pressed | Typing reset edge state; held shortcut fired on blur. Preserve actual down state, consume sensor buttons while map owns focus. |
| Code defect | MissionMap.RecordEdit / OnClick Delete | Unordered Remove scrambled route/history. Use RemoveOrdered. |
| Code defect, engine-tested | Terminal.CloseMissionMap / MissionMap.Open | Reopening discarded draft, selection, history/note and recentered map. Keep session model, release widgets, restore context. |
| Code-supported remote risk | Gateway.ORD_CommandRPC | Global 100ms throttle discarded unrelated commands. Bounded enum and per-command duplicate suppression. Remote test remains separate. |
| Code-supported race, local handler test | ReconReports.ORD_ReportListReply | Untagged old-faction response restored cleared data. Tag/validate faction and preserve valid same-faction cache. |
| SDK-confirmed defect | Terminal.Close / CameraManager.SetPreviousCamera | The native method cycles the camera list rather than restoring history. Save CurrentCamera before sensor creation; restore that exact camera on close/failure, fall back to a registered PlayerCamera if it disappeared, and do not override a different active camera. |
| Code defect | Gateway feedback and consumers | Indefinite stale messages. Five-second lifetime and session/request correlation. |
| Code-supported camera defect | Terminal manual aim / ResetZoomInput | Requests accumulated beyond gimbal stops; focus reset discarded resolved pose. Clamp requested direction and retain camera pose. |
| Observed baseline | SensorHUD.Update / Project | Debug entity identifier, uniform large text, no action hints, ambiguous COASTING. Compact operator identity, clear units, native binding-derived hints, explicit LAST OBSERVED. |
| Source + dynamic engine evidence | ORD_Pitch / installed PFC_FlightModel | W was negative/down and S positive/up. Positive/negative gateway pulses measured +0.185/-0.174 rad/s local nose-up response. Default bindings corrected to W/up S/down; simulation/autopilot signs unchanged. |
| Untested suspicion | Unrelated menu focus | Native priority may already suppress some input. Explicitly suspend continuous/action processing while another menu owns focus; keep heartbeat alive. Physical input check required. |
| Existing failed gate | Docs/ACCEPTANCE.md thermal | Black-hot dawn contrast remains unresolved; no claim of calibration fix. |

## Traced interaction paths

- Terminal -> CLAIM/ValidLink -> local camera/widgets -> frame input -> post-physics camera -> telemetry. Mode request has immediate local acknowledgement, confirmation from aircraft state, duplicate suppression and three-second unconfirmed timeout.
- Report marker -> immutable coordinate -> PointSensorAt -> gimbal. Existing entity path: designation -> TRACK -> LOS/evidence -> TEMP_LOSS / LOST -> reacquire or CLEAR_TRACK. No new detector or live report coordinates.
- Native MapMenu owns cursor/note; closing releases widgets/menu and preserves session draft/note/selection/map view. Complete control exit discards session context.
- Death/control loss/destruction -> Close -> release claim/observer, detach thermal/render targets, delete camera/widgets, restore saved character flags. Server permissions remain authoritative.

## Shared visual and timing values

Editable native Canvas HUD, physical-pixel 1920x1080 reference with anchored panels. Body 20px; hints/secondary labels 18px; 8px spacing multiples; 48px safe inset. Fixed glyph advance stabilizes numbers. Neutral F0F2ED, muted accent B4D1CB, caution E5BE78, critical FF9A8F. Only small identity/sensor panels use 48 percent dark backgrounds. Map/schematic use the same restrained colors. No tracking animation, new sounds, shake, grain or decorative motion.

Camera stays per post-physics frame. Existing 22ms exponential damping retained; relative mouse displacement is not dt-scaled; digital pan 55 degrees/second divided by zoom. Telemetry 10Hz, footprint 4Hz, trail 1Hz/120 samples, reports 0.5Hz. Local notices use a separate cached canvas. Blend plus video retains the known-good schematic fallback. No claimed GPU optimization.

## Conditions and intermediate results

Windows; Ryzen 9 7950X3D; RTX 4090, driver 617.14; Reforger 1.8.0.13. Fresh isolated profiles, native default quality settings, windowed, resolution scale 1, Vsync setting 1; supplied maxFPS caps. Engine settings files are preserved with evidence. No network latency/loss emulation. Fixed-aircraft sensor scene and independently dynamic flight scene are distinct.

Baseline 1080p/120cap four-second samples: EO p95 10.657ms/max19.338ms; IR 11.266/55.943; blend11.224/16.954; EO+wide11.153/15.909. First polish comparison: EO10.584/19.490; IR10.885/55.712; blend10.505/15.388; EO+wide10.651/16.634. Single short samples include screenshot/channel transition overhead, are capped, and are not statistical performance proof or subsystem attribution.

Dynamic Overwatch fixture: 14 checks PASS, 12 seconds, 465.078m displacement, 400.626-457.850m AGL from a one-time 450m/55.56m/s seed. SENSOR/PILOT transitions preserved auto; manual takeover and HOLD recovery accepted. No pose freeze. Altitude was descending late in this short sample; this does not establish sustained orbit/altitude stability. No flight law changed.

Intermediate failures retained: camera fixture compile required matching Enforce override argument names and alphabetical modded-class order; fixed in test only. Same-frame close/reopen collided with native MapMenu HUD deregistration; test now yields before reopening. One-line conditional/return in feedback receiver compiled but failed native assertions; expanded to explicit blocks. Subsequent results below supersede only the checks rerun.

## Validation results

| Status | Check | Actual evidence / limit |
|---|---|---|
| PASS | Native compilation and packing | Clean development package; 206/206 packed resource bytes match manifest; no test/editor scripts. |
| PASS | Recon/planner policy and UI suite | 66 distinct assertions at each of 1920x1080, 2560x1440, 3840x2160, 1920x1200 and 3440x1440. Local engine, 120 FPS cap; no recorded script errors. |
| PASS | Camera/action checks | 13 distinct assertions at 30/60/120 FPS (plus 16 distinct assertions in the final 60 FPS camera/binding/restore supplement): dt-scaled 20x pan, stop/reverse response, pose-preserving focus reset, requested/accepted/timeout modes, stale-gap held-key suppression, three entry/exit cycles at each cap. |
| PASS | Actual tracking state path | 9 assertions: real Cessna ray designation, acquisition, visible overlay, last-position freeze on FOV loss, LOST, no live lost-subject overlay, reacquisition and cancellation. Other visible people remain valid contacts. Loss was induced by repositioning target outside FOV, not a wall. |
| PASS | Dynamic Overwatch | 14 assertions, real physics following one airborne seed. Mode transitions preserve auto; signed pitch and manual takeover/HOLD recovery checked. Only 12 seconds of automatic flight; not sustained orbit acceptance. |
| PASS | Route interaction regression | 15 UI-handler assertions including actual middle Delete/Undo ordering and centering. Local saved presets remain local drafts. |
| PASS | Recovery supplement | Native MapMenu close restores camera state; player flags and owned UI/camera references restored/released. Held Escape across native map closure also passes after keeping the operator input context active on the recovery frame. Final pilot and clean startup results are recorded in final-checks.json. |
| PASS | Captured HUD review | EO foliage/terrain, bright sky and gimbal caution, 40x, white/black hot, experimental blend, wide inset, map and reader. No critical sensor-HUD overlap/clipping observed in reviewed resolutions. Native non-Orion HUD elements may also appear. |
| FAIL (pre-existing acceptance) | Thermal image quality | Black-hot dawn contrast failure remains in Docs/ACCEPTANCE.md; palette captures here prove rendering, not calibration. |
| BLOCKED | Dedicated operator + independent viewer | Existing acceptance record states no second player client is available. No remote client, latency, packet-loss, reconnect, late-join or distant streaming acceptance is claimed. |
| NOT RUN | Physical keyboard/mouse end-to-end latency | Fixtures inject action values or invoke native handlers. No HID-to-displayed-pixel timing. |
| NOT RUN | Full flight/combat/lifecycle endurance | Takeoff, landing, weapons/service, full orbit altitude convergence, natural moving/group targets, death/disconnect and 30-minute leak regression. |
| NOT RUN | Detailed thermal/secondary-feed timing | Dawn signature recalibration, actual moving-image/overlay alignment at capped thermal/blend refresh, isolated sensor CPU/GPU attribution and controlled background-weather matrix. |

All statuses describe the stated conditions only. Ordinary resource/pathfinding/UI diagnostics remain in engine logs; zero recorded script errors does not mean every native diagnostic is clean. Five-resolution captures precede small subsequent lifecycle/label corrections; affected paths were rerun separately. The final clean source manifest is checked independently of fixture packages.

### Responsiveness measurements

| FPS cap | Action to post-physics camera update | Notice to canvas submission |
|---|---:|---:|
| 30 | 4 ms | 27 ms |
| 60 | 1 ms | 17 ms |
| 120 | 1 ms | 10 ms |

These are one scripted onset per run, measured with System.GetTickCount, not percentiles or physical/display latency. All meet the initial 50ms local-feedback target in these runs. The real-time camera path is independent of 10Hz telemetry. Final 60 FPS camera-restoration rerun measured 1ms action-to-camera and 22ms notice-to-canvas; this remains a single onset.

Latest matched 1080p p95: EO **10.657 -> 10.609 ms**, IR **11.266 -> 10.499 ms**, blend **11.224 -> 11.069 ms**, EO+wide **11.153 -> 11.028 ms**. Maximum EO+wide changed **15.909 -> 16.975 ms**; IR transition spikes remained about **55 ms**. No significant optimization or unexplained broad regression is established by these brief capped samples. Raw p50/p95/max and sample counts: [summary.json](PolishEvidence/summary.json).

### Inspectable captures

- [Before sensor view](PolishEvidence/before/ReconEO.png) / [After sensor view](PolishEvidence/game-120-1920x1080/ReconEO.png)
- [4K blend](PolishEvidence/4k/ReconBlend.png), [16:10](PolishEvidence/game-120-1920x1200/ReconEO.png), [ultrawide inset](PolishEvidence/game-120-3440x1440/ReconWide.png)
- [Live track](PolishEvidence/tracking-game-60-1920x1080/PolishTrack.png), [obscured](PolishEvidence/tracking-game-60-1920x1080/PolishObscured.png), [lost](PolishEvidence/tracking-game-60-1920x1080/PolishLost.png)
- [High zoom](PolishEvidence/camera-game-60-1920x1080/PolishHighZoom.png), [gimbal warning / sky](PolishEvidence/camera-game-60-1920x1080/PolishLimit.png), [black hot](PolishEvidence/camera-game-60-1920x1080/PolishBlackHot.png), [closed control](PolishEvidence/final-pilot/PolishDisconnected.png), [pilot view](PolishEvidence/final-pilot/PolishPilot.png)
- [Map with retained draft/note](PolishEvidence/game-120-1920x1080/ReconMap.png), [read-only report view](PolishEvidence/game-120-1920x1080/ReconReader.png)

No capture is a mockup. Earlier same-frame close captures still showed the previous sensor frame; the final closed-control capture waits a second after closing. The final close-state fixture records the original native PlayerCamera, checks its exact restoration across three cycles, and captures the returned ground-level view. Earlier captures exposed the old list-cycling restore bug. The legacy airframe camera can include the aircraft silhouette along the upper edge; its mount was not redesigned. Failed intermediate test logs stay in the external build directories. Initial tracking-overlay assertion incorrectly required zero *all* contacts while another person was visible; corrected to check the lost subject specifically, then rerun successfully. A final held-Escape failure traced to one recovery frame without activating the operator input context: injected/held Escape read 1, 0, 1 across that gap. Activating the context during recovery fixed the repeated exit; the complete recon/reader sequence was rerun successfully. Pilot captures exposed static literal newline marks and a lingering sensor inset; those were corrected and the affected mode path rerun.

Final review also fixed stale-gap key replay, cached native-Escape map position, separated missing-input warning/notice rows, canceled overwrite confirmation on map close and preserved the selected map tool.

## Files changed in this pass

- `ORD_TerminalComponent.c`: focus, bounded gimbal input, mode feedback, session cleanup including explicit original-camera restoration, retained map, binding-aware pilot hints.
- `ORD_SensorHUD.c` and `UI/ORD/Sensor.layout`: layout, semantic state, stable typography, actual sensor-camera projection, contact label overlap suppression and immediate presentation channel.
- `ORD_MissionMap.c`, `ORD_ReconPane.c`: ordered editing, retained context, cached widget references and consistent presentation.
- `ORD_Gateway.c`, `ORD_ReconReports.c`: bounded per-command duplicate filtering, correlated transient replies and faction isolation.
- `Configs/System/chimeraInputCommon.conf`, `keyBindingMenu.conf`: W/up S/down defaults and labels.
- `ORD_AircraftComponent.c`: shared OVERWATCH display name only; no flight-law change. `ORD_SensorDisplay.c`: shared colors and explicit sensor-view hiding/detachment. `UI/ORD/Operator.layout`: remove static decorative pitch/side marks that displayed literal escape text.
- Source-only fixtures and documentation; full runtime hashes in [changed-runtime.json](PolishEvidence/changed-runtime.json).

## Manual release verification

1. Load the candidate with the same dependency versions. Use ORD_Runway, enter the terminal, confirm role/link/flight mode. Rebind Map and Mode; verify both HUD hints and actions. Check W/up S/down against the physical aircraft, then take off and enable Overwatch for a complete orbit.
2. At 30/60/120 FPS scan wide and at 20x/40x, hold each gimbal stop then reverse. Switch EO/WH/BH/blend. Verify no recenter jump. Compare people, vehicles, terrain and building occlusion at dawn/noon/night; record exposure and weather.
3. Designate a visible vehicle, request track, drive behind a solid building, and confirm no live box or updated last-observed coordinate through it. Reappear, reacquire and cancel. Save a report; move the vehicle and confirm the report stays fixed.
4. Open map, edit a route/note, pan/zoom and select a report. Hold Mode/Map while typing; release focus without releasing the key. Verify no command replay. Close via both custom Map binding and native Escape while held; stay in drone camera. Reopen and verify draft/selection/tool/note/view. Open another menu, hold controls for over 250ms, close it and verify no replay or camera motion from stale input.
5. Save to an occupied slot once, close map, wait over five seconds, reopen: first Save must ask again. Apply a route, rapidly request different modes, observe requested vs confirmed and rejected/unconfirmed outcomes without assuming success.
6. On a dedicated server use separately authenticated operator and viewer clients. Test competing claims, faction change with in-flight replies, report visibility, late join, reconnect, death/respawn, drone destruction and 10km remote streaming. Repeat at 100ms latency/1 percent loss using an authorized network test setup. Verify no stale response crosses a session.
7. Run 30 minutes with repeated entry/exit and all optional feeds. Compare identical before/after scene/settings; record frame spikes, CPU/GPU subsystem timings, listener/widget/camera counts and client/server network rates. Release only after remaining gates pass.

Most valuable next work: dedicated multiplayer acceptance and thermal calibration, followed by sustained Overwatch/physical-input flight validation. Map panels still have substantial route-tool density; collapsing secondary planner controls is a separate follow-up, not an untested replacement in this pass.

## Development package

[Orion-E-rc9-operator-polish-dev-packed.zip](../ReleaseCandidates/Orion-E-rc9-operator-polish-dev-packed.zip), 94,365,922 bytes. SHA-256 `61a9ba50242d35d2669f15465233e3400b67808c6ce578e35e0a02a4de82afaf`. Three native files: project descriptor, data.pak, resource database. Archive CRC and extracted bytes checked against native output. Final clean startup PASS (50s, 60 FPS cap, 1080p, zero recorded script errors). [Final checks](PolishEvidence/final-checks.json) include 16 camera/binding/restoration and 35 recon/recovery assertions, archive/source verification and remaining release gates. No install, commit, push or publication performed.
