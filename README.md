# Orion-E Reconnaissance Drone

Arma Reforger 1.8.0.13 source project and **1.0.0-rc9-dev development candidate**. Publication is excluded. See [Docs/ACCEPTANCE.md](Docs/ACCEPTANCE.md) for current results and blockers; historical RC8 evidence remains in VALIDATION_RC8.md. a successful compile is not gameplay acceptance.

## Installation

Open `ReconDrones.gproj` in Enfusion Workbench. Dependencies: Arma Reforger (`58D0FB3206B6F859`), Propeller Flight Core (`69A8A34027DA65C5`), ThermalPostProcessAssets (`69623A037A721B91`). Dependency files are not redistributed. Open `Worlds/ORD/ORD_Runway.ent` and play; select the USSR spawn and operate the nearby terminal.

Extract the packed candidate into a separate addon folder outside this source workspace. Never put another active `ReconDrones.gproj` inside this project: Workbench can select the duplicate packed project instead of your edited source. Fully restart the game after changing input configuration. Use a fresh test profile.

## Controls

| Control | Action |
| --- | --- |
| H | Switch flight / sensor |
| M | Open / close native terrain mission map |
| Esc | Close map, then terminal |
| I | Engine toggle |
| S / W, A / D, Q / E | Nose up / down, roll, rudder |
| Shift / Z, Space | Throttle up / down, brake |
| Mouse / arrows | Sensor aim: ↑ up, ↓ down, ← left, → right |
| Wheel, + / -, numpad + / - | Sensor 1–40× zoom |
| N | Day / white-hot / black-hot |
| Tab / T | Select point / track acquired entity |
| G / X / B | Personnel group / recenter / contact brackets |
| Y | Choose Sensor point / Tracked vehicle weapon mode |
| V / F | Arm-safe / fire selected weapon mode |
| R / J / C | Return home / fly route / clear route and hold |
| O | Service at a nearby service point |

Takeoff and landing remain manual. Switching to sensor mode enables hold when necessary; it does not take off automatically. Link loss or operator death safes weapons and retains return-home behavior.

The sensor view uses a transparent, white Orion-inspired reconnaissance HUD with live flight and camera readings. This is a game interface, not an authenticated real-world replica. Qualifying observations receive stable local C- identifiers after two seconds. Vehicle/person classification requires four/six seconds and sufficient optical detail; the actual selected vehicle/person gets stronger brackets. CONTACTS counts the currently presented contacts (up to eight). B toggles brackets. Occluded and dead contacts are excluded; coasting and lost tracks are explicitly labeled. Existing group tracking remains available, with individually visible members displayed rather than a guessed group perimeter.

GS is horizontal velocity; ASL is world height minus the engine's ocean reference; AGL is terrain clearance. Azimuth and heading use the native map's positive-Z north / positive-X east grid convention. SIM is elapsed world simulation time. OBS GRID and GEO RNG always describe the present camera-axis surface hit, including an intervening obstruction, and show -- for a sky/no-hit view. Coordinates use the native map converter at one-metre resolution; they are not latitude/longitude. The aircraft's scenario entity name is displayed where present. OVERWATCH labels the existing automatic orbit/hold mode; ROUTE, RETURN HOME and MANUAL remain separate.

Point/vehicle tracking intentionally turns the camera to hold the target; manual aim releases tracking. Free aim consumes each mouse delta once. Point-lock geometry resolves after physics; manual aim uses short damping and zoom-scaled sensitivity. The sensor distinguishes requested aim from its mechanical limits. See Docs/THERMAL.md for the thermal simulation profile.

## Mission map

Choose **Route**, click to add or select, drag to move, and use Delete / Move earlier / Move later. Maximum eight points. Map pan and zoom are independent of sensor zoom. Configure altitude 150-2,000 m AGL, cruise 30-65 m/s (shown in km/h), and radius 250-1,500 m. **Apply route** submits the complete draft; **Fly route** starts a repeating circuit. Editing does not change the active mission until applied. Applying a replacement active route commands hold until Fly route.

Choose **Loiter**, select a map position, then **Loiter here**. **Resume route** returns toward the interrupted waypoint. Clearing a route holds at the current position. Prepare routes on the ground, then take off manually before executing them. Accepted coordinates, settings, next waypoint and flight mode are server-authoritative and restored when reopening. Tight loiter protects airspeed with a 50 m/s minimum and permits up to 55 degrees of bank; measured orbit radius and altitude fluctuate during turns (see validation report).

## Banderol game weapons

One authored 4.4 m VisualFit Banderol uses the Orion centreline visual hardpoint, with matching mounted/projectile geometry. The separate 5 m reference master remains editable. These are game assets with explicitly fictional gameplay tuning, not a real-world weapons simulation.

* **Sensor point:** aim at a visible surface; V arms and F fires at the server-traced point.
* **Tracked vehicle:** acquire a vehicle with the sensor and engage tracking with T, choose Tracked vehicle with Y; F launches against that tracked vehicle. Lost tracking falls back to its last observed position.
* **Map coordinate:** choose Weapon target, select a coordinate, Arm, then Launch at target. Clicking the map never launches. Map targeting does not require sensor line of sight.

Server checks enforce ownership, airborne state, safe/armed state, ammunition, 1.5 s cooldown and 100-5,000 m range. Ammunition is consumed only after a projectile and its logic are created. A stopped aircraft at the service point reloads one missile and safes the weapon. Flight traces, damage and cleanup run on the server; state and effects replicate.

Current tuning: 150 m/s cruise, 45 s lifetime, 300 direct damage, 120 blast damage over 25 m with obstruction checks; vehicle damage multiplier 20 before native armor reduction. These are exposed attributes and require multiplayer balancing.

## Editable assets and validation tools

`Assets/ORD/Models/RC8` contains the native Orion and Banderol models, LOD exports and textures. `Integration/RC8/GameSources` contains the editable game-asset Blender files; `Integration/RC8/Blender` contains numbered motion/rig checkpoints. `AssetProduction/Orion_Banderol_R3_v001` retains the separate reference masters. Reimport changed FBX files through Workbench before packing. The older `OrionE_Game` files and build tools remain for historical RC7 work; the RC8 prefabs point to the new models.

`Tools/enfusion-local.mjs` adapts the installed Enfusion MCP package to this game's current PAK layout. Set `ENFUSION_MCP_PACKAGE` if installed elsewhere. Machine game/tools paths live in `~/.enfusion-mcp/config.json`. Test overrides in `Tools/Validation/*.c.txt` belong only in isolated test copies, never the release. `Tools/stage_model_runtime.py` excludes editor sources and Workbench handlers from runtime staging.
