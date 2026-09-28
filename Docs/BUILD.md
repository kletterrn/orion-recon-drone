# Reproducible Windows build

Install Git with Git LFS, Python 3.13+, Node.js, Arma Reforger 1.8.0.13 and matching Arma Reforger Tools. Clone this private repository and run `git lfs pull` before opening the project.

Install external dependencies using their Workshop IDs in ReconDrones.gproj: Propeller Flight Core (69A8A34027DA65C5) and ThermalPostProcessAssets (69623A037A721B91). The initial thermal baseline is 1.0.23. These dependencies and base-game files are not redistributed. Dependency content hashes are recorded in Docs/dependencies.json; different content requires a compatibility run.

Copy `Docs/build.example.json` to `local.build.json` at the repository root and supply local paths. Then run:

```
npm ci --prefix Tools --ignore-scripts
python Tools/release.py check
python Tools/release.py build --output C:/OrionBuild/baseline
node Tools/verify_package.mjs C:/OrionBuild/baseline
```

The output directory must be outside the addon source tree and initially empty. Staging excludes editor/test code and editable asset sources. Packaging uses Workbench, retains resource GUIDs, and includes the world placement layer, ACP audio projects and SIG resources. The manifest records every staged resource hash and all build logs stay outside the project.

The project can also be opened directly using ReconDrones.gproj. Keep only one active copy of this addon GUID in a Workbench session. Reimport changed FBX/texture sources before packaging. The maintained RC8 exports are Orion_RC8_Game_v010.blend and Banderol_RC8_Game_v003.blend; historical export scripts are not the release entrypoint.

GitHub Actions checks source/resource structure. It does not run the proprietary game or establish gameplay acceptance. A completed release additionally requires the recorded engine and multiplayer acceptance tests. No Workshop publication is performed by the build.

## Isolated engine checks

Add `--fixture Tools/Validation/ORD_ObservationProbe.c.txt` or another documented fixture to a new build. Never distribute fixture builds: they contain TEST_ONLY.txt. Run `python Tools/run_game.py --build <build-directory> --seconds 80 --fps 60` (add `--headless` only for non-rendering checks). Runs retain the engine console and a JSON result; each FPS/resolution needs a fresh profile. A zero exit code establishes startup and absence of recorded script failures, not every acceptance gate.

The stabilization fixture pins an elevated aircraft pose and measures actual submitted camera direction against a stationary point. It is not flight/input validation. The observation scene uses a spawned UAZ and a real concrete wall near the end of the ray. The thermal fixture requires the RC7 operator bootstrap plus ORD_ThermalProbe and captures EO, both polarities, and return to EO. Fixtures must remain outside release scripts.

server.json configures rendering and network streaming independently to 5000 m. Engine/platform limits still apply. See the official [server configuration](https://community.bistudio.com/wiki/Arma_Reforger%3AServer_Config). Dedicated acceptance requires a server and two separately controlled clients; the local scripted fixture cannot substitute for that test.
