# Reconnaissance suite validation — 2026-09-29

Development candidate for Arma Reforger 1.8.0.13. These are native-engine and scripted rendering checks, not full gameplay or multiplayer acceptance.

## Verified

- Native Workbench compilation and packaging succeeded. All **206 runtime resources** in the clean PAK match staged source bytes. No test or editor scripts are included.
- **23 distinct reconnaissance checks passed at both 1920x1080 and 2560x1440**, with no recorded script errors. Checks cover frozen coordinates, JSON roundtrip and faction filtering, empty-faction exclusion, ordered newest-16 retention, invalid category/faction rejection, persistent map-point focus, four-corner footprint and sky clearing, save rate limiting, authoritative optical surface hit, server rejection of sky/invalid rays, map opening and pointing, note focus and shortcut suppression, report recall, trail recording, unchanged saved position, and opening/closing the reader without aircraft control.
- Inspected actual captures at both resolutions: map and report panels, EO, IR, blended view, wide video with zoom rectangle, and schematic fallback. Text entry is visible. The map's “Invalid report” message in the fixture capture is the expected result of the intentional invalid-ray test immediately before opening the map.
- EO/IR compositing uses an independently rendered daylight image and the existing thermal main image. Captured central-region color-channel measurements distinguish the blend from monochrome IR; these are rendering checks, not thermal-calibration measurements.
- The wide video image and zoom rectangle render correctly. Selecting video while blending uses the labeled schematic fallback. This avoids the missing-HUD-glyph artifacts observed when both secondary scene renders were active together. Returning to EO restores video.
- The archive passed ZIP integrity checks, and every archived file matches the native clean packed output. It includes `ReconDrones.gproj`, `data.pak` and the native `resourceDatabase.rdb`.

The 31 distinct mission-planner and route-tools regression checks also passed in a sequential 55-second headless run, with no recorded script errors. `regression-results.json` retains the results. The clean packed addon also reached GAME state in a sequential 55-second headless startup check, with no recorded script errors (`clean-startup.json`). Final source hashes still match the clean build manifest.

Engine logs retain non-script UI/resource/pathfinding diagnostics, and Workbench logs include resource diagnostics at packer shutdown. The result above means no recorded script errors; it is not a claim that every engine diagnostic is clean.

## Rendering-cost prototype

The fixture holds the aircraft at a fixed airborne transform and takes sequential four-second samples. The process was configured with a 240 FPS cap. The extra daylight render uses half resolution at up to 30 FPS; wide video uses its small inset resolution at up to 15 FPS. The schematic does not render another scene.

| Display | 1080p average FPS | 1440p average FPS |
| --- | ---: | ---: |
| EO, inset off | 236.9 | 237.0 |
| IR, inset off | 234.3 | 232.0 |
| Experimental blend with schematic fallback | 234.8 | 233.2 |
| EO with wide video | 235.4 | 235.5 |

These short samples are close to the configured cap and include transition/screenshot overhead. They do **not** resolve isolated GPU cost, establish a significant performance difference or predict performance during flight, combat or multiplayer. Both extra views remain opt-in; the schematic remains the default. Raw frame counts, durations and image metrics are in each resolution's `render-metrics.json`.

## Evidence and reproduction

Final source fixtures: `Tools/Tests/ORD_RC7OperatorProbe.c.txt` and `Tools/Tests/ORD_ReconSuiteProbe.c.txt`. They use a real player character, the ownership gateway, sensor raycasts, actual UI handlers and native render targets. They hold the aircraft still only inside the isolated test package. They do not inject physical keyboard/mouse input or simulate a remote network client.

- `1080p/` and `1440p/`: seven engine captures, `engine-results.json`, `render-metrics.json`.
- `packed-integrity.json`: complete runtime byte-match inventory.
- `package.json`: archive hash, size and integrity result.
- External builds/logs: `C:/Users/david/Desktop/OrionV2Builds/recon-suite-accepted-test`, `recon-suite-release`, `recon-suite-regression`.
- See [RECON_SUITE.md](../RECON_SUITE.md) for reproducible build/run commands and controls.

During implementation, tests caught reserved Enforce names, a handler parsing issue, unordered array removal during eviction, a display layer behind the scene, and unsuitable secondary-camera alpha/exposure behavior. Ordered removal, a visible display layer, a dedicated HDR material and weighted additive compositing resolved those issues. The dual-render HUD issue is handled by the explicit schematic fallback; it is not claimed fixed for simultaneous video and blending. Intermediate builds remain outside the addon tree and are not the release.

## Remaining acceptance

Two-client delivery, late join, reconnects, faction changes across the network, physical mouse/controller operation, sustained flight and long-session GPU/cleanup behavior remain unverified. Existing RC9 flight and thermal dawn-calibration gates remain open. Reports are mission-local and bounded, not persistent across restarts. Image thumbnails remain deliberately deferred: local whole-window screenshot support does not validate sensor-only capture or multiplayer image transport. No Workshop publication was performed.

## Development package

`ReleaseCandidates/Orion-E-rc9-recon-suite-dev-packed.zip` — 94,363,626 bytes.

SHA-256: `c03e6d1032f60aee428568245317948d16b8360d9c0824d003182c731586b28b`

Extract into its own addon directory, enable only one copy of the Orion addon GUID, and keep the existing Propeller Flight Core and ThermalPostProcessAssets dependencies installed. This development candidate includes the previously implemented route tools.
