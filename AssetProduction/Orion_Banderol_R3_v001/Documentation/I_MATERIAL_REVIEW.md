# I v001 — UV and material review checkpoint

Executed in Blender 5.2.2 LTS. Approved source shapes, component transforms and parenting are preserved, including the compact exterior pylon and 4.4 m artistic VisualFit version. Original 5 m Banderol remains a separate independent master. This checkpoint is ready for material review; optimized exports and engine validation are still Stage J.

## Files

- `../Orion/Orion_Master.blend`; numbered `../Orion/checkpoints/Orion_I_uv_materials_v001.blend`.
- `../Banderol/S8000_Banderol_Master.blend`; numbered `../Banderol/checkpoints/BDL_Reference_I_uv_materials_v001.blend`.
- `../Banderol/S8000_Banderol_VisualFit_Master.blend`; numbered `../Banderol/checkpoints/BDL_VisualFit_I_uv_materials_v001.blend`.
- `../Assembly/Orion_Banderol_Preview.blend`; numbered `../Assembly/checkpoints/Orion_Banderol_I_materials_v001.blend`.

Masters depend on their adjacent `textures/I_v001/` folders. Assembly uses its own pylon textures and three relative source libraries; the separate scale scene accounts for the original-size library. Private image references require the existing `Support/references_private/` directory and remain reference-only.

## Texture and shading work

Eleven separate 4096 x 4096 sets, four PNGs per set: lighting-free BaseColor, Roughness, Metallic and tangent Normal. Base color uses sRGB; scalar and normal maps use Non-Color. Orion: Airframe, Wing_L, Wing_R, Tail_Rear, Gear_Bays, Sensor. Two sets each for reference-size and VisualFit Banderol: Body and Appendages. One additional set for Assembly_Pylon.

UV_Asset is independently packed across every mesh sharing an atlas, with no intentional stacking. Actual base-loop layouts are exported as `../Previews/I_UV_*.svg`; the checker render is generated from the real saved UVs. The layout is a source-asset baseline. Export UV efficiency, mip behaviour and final density still require the optimized mesh pass. Current approximate density is 499 px/m for wings, 563 airframe, 594 gear/bays, 1022 tail/rear, 1795 sensor, 1178 original Banderol body, 1433 VisualFit body, 1949 appendages and 3195 pylon. These are base-mesh local-area estimates, not measured screen-space guarantees.

Paint stays nonmetallic and restrained; white nose, bay finish, rubber, seals, exposed sliding metal, hardware and optics retain distinct shaders. No invented lettering, baked directional lighting, photo textures or generalized chipped/rusted edges. Editable curves retain their procedural materials. Their later mesh conversion is part of game preparation.

Current normal maps are Blender source-surface bakes, not high-to-low transfers for a finished game mesh. AO, final high-to-low projection, DirectX normal conversion, TIFF conversion, Enfusion packing and engine material testing remain Stage J. These PNGs are not proof of Reforger compatibility.

## Actual checks

- Source mesh vertex/index hashes, local rest transforms and parenting match the approved pre-material checkpoints for all four files (`I_shape_preservation_v001.json`).
- No collapsed base-mesh UV faces or coordinates outside 0–1 in any of eleven sets (`I_build_v001.json`, `I_pylon_v001.json`).
- Blender's native UV overlap selection found zero selected overlap loops in each shared atlas (`I_validation_v001.json`). Evaluated modifier UVs and future optimized meshes are outside this base-map test.
- Nine fresh Blender processes successfully opened four current files, four numbered checkpoints, and the assembly from a relocated package. Texture files resolve, including the linked sources' relative paths.
- Ten actual Cycles renders were created and inspected: sensor, nose gear, main gear, bay inspection, UV checker, clay, original Banderol, assembly, pylon and side. Bay inspection uses an additional direct fill to expose the inner walls. `I_renders_v001.json` lists the images.
- Early verification attempts used obsolete UV-selection accessors; these failed checks were repaired using the installed Blender API and rerun. A temporary tail-bake material override warning was fixed and that set rebaked. Rejected maps are kept under Support, not used in the masters.

## Remaining limits

The rack remains a detailed exterior visual approximation. Exact configuration authenticity is not established. Previous default gear-down and complete propeller sweep clearances remain applicable because geometry and rest transforms did not change. The combined illustrative gear retraction still intersects Banderol and is not accepted as clear. No operational interface, release mechanism or engineering compatibility is represented.

No new exports or engine import tests were performed in this stage. Next checkpoint is Stage J: separate optimized copies, final bake targets, export skeleton, LOD/collision preparation and isolated import testing after this review.
