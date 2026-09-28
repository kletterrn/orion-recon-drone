# RC9 development candidate: acceptance incomplete

The private repository and packaged development candidate are deliverables, not a claim that the requested release is complete. Two-client acceptance is blocked: the user confirmed no second player client is available. Engine fixtures exercise specific behaviors; they do not establish physical-input flight, distant multiplayer streaming, or a 30-minute gameplay regression.

## Recorded checks

- PASS: RC8 source baseline cloned from GitHub, runtime LFS assets retrieved, Workbench compilation, packing and clean startup. Baseline tag v1.0.0-rc8-source-baseline. GitHub Actions also fetched LFS and passed resource checks.
- PASS: native-engine observation evidence timing, brief interruption pause, longer-loss reset, no immediate reacquisition and independent classification size gate.
- PASS: actual vehicle observation and equal effective geometric detail at 20x/40x in a native scene.
- PASS: real concrete obstruction at ray fraction 0.989827 blocks observation; the final two percent is not treated as clear.
- PASS: elevated stationary point lock at 1080p at 30/60/120 FPS, 1x/5x/20x/40x (12 combinations). Peak 0.0066 pixels at 40x in this isolated fixture.
- FAIL (historical): the close-ground 40x fixture had a 14.27-pixel peak (RMS 0.79).
- PASS (after correction): four bounded lens-origin refinements reduced the close-ground 40x peak to 3.9831 pixels and RMS to 0.5966 at 60 FPS; all four zoom settings passed that rerun. The historical failure remains in the evidence.
- PASS: independent RC9 checkout compiled and packaged; 198/198 packed resource bytes match the manifest with no fixture/editor sources.
- PASS: thermal mode activation and return to daylight without script errors. Image-quality calibration is a separate gate.
- PASS: 27 EO/WH/BH captures across clear/rain/fog and dawn/noon/night, with actual weather values recorded and no script errors.
- FAIL: full thermal image-quality acceptance. Black-hot dawn remains low contrast despite limited clipping. The tested automatic-gain alternative was rejected because it over-brightened white-hot.
- NOT RUN: moving aircraft mount error, physical-input response timing, dedicated multiplayer/latency/loss/respawn/competing claims, 10 km terminal separation and actual distant meshes, physical-input flight/landing/service/weapon regression, 30-minute leak/performance session, sensor p95 CPU measurement, matched before/after videos.

Machine: Windows, AMD Ryzen 9 7950X3D, NVIDIA RTX 4090. Engine 1.8.0.13; dependency content pinned in dependencies.json, thermal 1.0.23. JSON records are in validation/. No Workshop publication was performed.

## Required follow-through

1. Measure moving mount/lock errors and manual response using physical input at all requested FPS/zoom settings.
2. Resolve low-contrast thermal cases using the recorded weather/time matrix and validate person/vehicle signatures; verify 30 Hz imagery independently of camera/HUD and verify digital zoom with image detail comparisons.
3. Run a dedicated server plus operator and observer clients. Exercise distant streaming, late join, reconnect, death/respawn, competing claims, 100 ms latency and 1 percent loss. Verify observer restoration and session cleanup on every path.
4. Complete the real-input flight/planning/service/weapon regression and 30-minute leak/performance run. Record acquisition logs, frame/network costs, sensor p95 and matched before/after captures.
5. Rebuild from the tagged source with recorded dependency hashes, verify packed bytes, and promote only after every required acceptance gate passes.

Optional, outside this release: engine warm-up/cooling, extra palettes, manual gain, controller support, target-signature packs and cosmetic detailing.

The additional native AutomaticHistogramEq comparison also clipped broad runway/vegetation regions in both polarities and was rejected. The delivered profile remains CustomMinMax; low-contrast dawn is an unresolved acceptance failure.
