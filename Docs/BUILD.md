# Reproducible Windows build

Install Git with Git LFS, Python 3.13+, Node.js, Arma Reforger 1.8.0.13 and matching Arma Reforger Tools. Clone this private repository and run `git lfs pull` before opening the project.

Install external dependencies using their Workshop IDs in ReconDrones.gproj: Propeller Flight Core (69A8A34027DA65C5) and ThermalPostProcessAssets (69623A037A721B91). The initial thermal baseline is 1.0.23. These dependencies and base-game files are not redistributed. Dependency content hashes are recorded in Docs/dependencies.json; different content requires a compatibility run.

Copy `Docs/build.example.json` to `local.build.json` at the repository root and supply local paths. Then run:

```
python Tools/release.py check
python Tools/release.py build --output C:/OrionBuild/baseline
```

The output directory must be outside the addon source tree and initially empty. Staging excludes editor/test code and editable asset sources. Packaging uses Workbench, retains resource GUIDs, and includes the world placement layer, ACP audio projects and SIG resources. The manifest records every staged resource hash and all build logs stay outside the project.

The project can also be opened directly using ReconDrones.gproj. Keep only one active copy of this addon GUID in a Workbench session. Reimport changed FBX/texture sources before packaging. The maintained RC8 exports are Orion_RC8_Game_v010.blend and Banderol_RC8_Game_v003.blend; historical export scripts are not the release entrypoint.

GitHub Actions checks source/resource structure. It does not run the proprietary game or establish gameplay acceptance. A completed release additionally requires the recorded engine and multiplayer acceptance tests. No Workshop publication is performed by the build.
