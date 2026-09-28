# Current review — I UVs and materials v001

Current masters and relative-link assembly have separate 4K texture sets, preserved approved geometry and numbered checkpoints. Open `../Assembly/Orion_Banderol_Preview.blend`. See `I_MATERIAL_REVIEW.md` for dependencies, ten inspected native renders, UV layouts and actual checks. All four files, four numbered checkpoints and the relocated assembly reopened successfully. UV overlap and image-path checks passed. The rack is still an exterior approximation; combined gear retraction remains unresolved. Game meshes, final high-to-low bakes and engine testing remain Stage J. Earlier sections below are stage history.

---
# Current preview — H compact pylon v009

Open `../Assembly/Orion_Banderol_Preview.blend` for the compact pylon and shorter, closer payload. Current carriage uses independent `../Banderol/S8000_Banderol_VisualFit_Master.blend` (4.4 m artistic fit). Original 5 m Banderol and Orion masters are preserved unchanged. Pylon is a detailed exterior approximation, not authenticated rack hardware.

Default gear-down and complete propeller-sweep checks pass; illustrative gear retraction still intersects the payload. Five inspected `../Previews/H_v009_*.png` renders and fresh/relocated library reopens passed. `H_REVIEW.md` and `H_compact_validation_v009.json` describe results. Numbered compact checkpoint v009 preserves this review state. Three relative libraries are required because the separate scale scene retains the original 5 m model. Future material/game work must explicitly choose the reference-size source or authorized VisualFit variant; do not silently conflate their dimensions.

---
# Current preview — H support v007

Current `../Assembly/Orion_Banderol_Preview.blend` includes a visible editable support under `ASSEMBLY_VISUAL_SUPPORT_APPROXIMATION`, parented with Banderol to the aircraft instance. Both masters remain unchanged. Banderol lowered 0.15 m from v005. Complete propeller sweep and default standing-pose mesh checks show zero unintended contacts. Gear retraction still has conflicts. Support shape/station is a labeled visual approximation; no documented rack or operational compatibility claim.

See `H_REVIEW.md`, `H_support_validation_v007.json` and the four `../Previews/H_v006_*.png` renders (v007 parenting preserves their world geometry). Numbered checkpoint `../Assembly/checkpoints/Orion_Banderol_H_support_v007.blend`. Earlier sections are stage history.

---
# Current preview — H front clearance v005

The current `../Assembly/Orion_Banderol_Preview.blend` moves Banderol rearward and slightly down, preserving both approved masters. Requested front-wing/gear clipping is cleared in default gear-down presentation; zero sampled mesh-surface contacts in that pose. Full illustrative retraction still has contacts and is not accepted as clear. Three inspected `H_v005_*` renders and fresh-process reopen passed. See `H_REVIEW.md`; previous v003 failed-placement notes below are historical.

---
# Current review — H linked assembly v003

Open `../Assembly/Orion_Banderol_Preview.blend`. Default `H_CARRIAGE_DIAGNOSTIC` shows a **failed provisional fit**, not an authenticated installation. `H_SEPARATE_SCALE_REVIEW` compares the independently linked sources. Six native review renders are under `../Previews/H_v003_*.png`; details and opening instructions are in `H_REVIEW.md`.

Approved source masters remain Orion E sensor v007 and Banderol G wings v004, byte-identical before/after H. Same metric axes +Y forward/+X right/+Z up; Banderol is 5 m long, 0.30 m wide with provisional 2.20 m main-wing span and estimated 12-degree sweep. Latest sensor pitch limit is +/-10, superseding historical +/-15.

The tested centreline alignment intersects the gear and deployed wings. Exact R3 carriage, rack and stowed/carried wing pose remain unverified. No rack was invented; amber line is an alignment guide only. Both masters and the relative-link assembly reopened in fresh processes, including a relocated copy. UVs/material bakes, optimized game meshes and engine validation remain later work. Prior notes below are stage history; they do not override current statuses.

---
# Current wing-angle correction — G v004

User R15 illustration (private R15_Banderol_swept_wings.png) requests modest main-wing angle. Both main wings now have an estimated 12-degree rearward leading-edge sweep beyond the root. This is a visual choice from perspective imagery, not a measured real configuration. Provisional tip span remains 2.20 m, length 5.00 m and casing width 0.30 m. Root positions, fairings, body/nose and tail were retained. All other base mesh vertex hashes match G v003.

Current independent master: Banderol/S8000_Banderol_Master.blend. New preserved checkpoint: Banderol/checkpoints/S8000_Banderol_G_wings_v004.blend. Previous files remain historical.

Performed: fresh master and numbered checkpoint reopens, 29 base-mesh manifold/degenerate/positive-volume checks, seven intended casing/root contacts, actual geometry dimensions, original mod asset hashes unchanged. Five curves remain outside base-mesh checks. Four actual renders generated and visually inspected: perspective, front, top and underside. G_validation_v004.json and G_sweep_change_v004.json record results. Game validation NOT ATTEMPTED. Images: Previews/Banderol_G_v004_Hero.png, Banderol_G_v004_Front.png, Banderol_G_v004_Top.png, Banderol_G_v004_Underside.png. Existing scale/evidence limits below remain applicable.

---
# Current separate Banderol — G wings v003

Open Banderol/S8000_Banderol_Master.blend; numbered checkpoint S8000_Banderol_G_wings_v003.blend. See Documentation/G_WING_SIZE_REVIEW.md for corrected straight narrow wings, actual dimensions and uncertainty. The old 0.946 m candidate is superseded by provisional 2.2 m. Orion remains unchanged E sensor v007. Historical descriptions below apply only to their named checkpoints.

---
# Current Banderol — G v002

Open the independent Banderol master; preserved checkpoint Banderol/checkpoints/S8000_Banderol_G_shape_v002.blend. New supplied front/side renders drove shape and visible detail corrections. See Documentation/G_REVIEW.md; its span/proportion decisions supersede historical F values below. Orion E sensor v007 remains approved. Review this revision before further stages.

---
# Current separate sources

Orion E sensor v007 is approved. Banderol F v002 is ready for primary-form review: ../Banderol/S8000_Banderol_Master.blend and ../Banderol/checkpoints/S8000_Banderol_F_primary_v002.blend. See F_REVIEW.md for ten actual views, evidence limitations and completed tests. Banderol's UV/detail/export work and the combined assembly remain pending. Historical statements below that Banderol is empty are superseded by this entry.

---
# Current master: camera correction E sensor v007

Open `../Orion/Orion_Master.blend`; numbered source `../Orion/checkpoints/Orion_E_sensor_fix_v007.blend`. See `SENSOR_REVIEW.md` for current renders and reference decisions. Sensor yaw +/-35 degrees, pitch now +/-10 degrees with a hard driver limit. All non-sensor source mesh vertices match E v005. Earlier Stage E details below remain valid except their sensor description/range/current checkpoint.

---
# Orion_R3 — Stage E v005 review checkpoint

Open `../Orion/Orion_Master.blend` in Blender 5.2.2. Preserved numbered source: `../Orion/checkpoints/Orion_E_exterior_rig_v005.blend`. Both are executed, saved, editable models. Stage E awaits visual review; it is not a finished game asset.

The approved D v012 body, nose and connected wing roots remain intact. All prior mesh vertex arrays match D v012; the fuselage additionally has a retained shallow triangular-vent Boolean. Stage E adds 29 source objects, giving 263 source objects, and a separate 23-bone preview skeleton. Materials and moving-part parents were updated without replacing approved mesh shapes. Original mod files were rehashed and remain unchanged. No old geometry was reused.

## Opening and posing

Use `ORION_GEOMETRY_REVIEW`, frame 1 for the default standing pose. Metres, +Y forward, +X right/starboard, +Z up; identity `ORION_ROOT`; nominal 8 m length and 16 m span. Do not apply transforms after posing.

Select `ORION_ROOT` and use Object Properties > Custom Properties to adjust presentation angles in degrees. `propeller_degrees` rotates blades, hub and spinner. Independent flap, aileron and ruddervator properties have +/-8 degree visual limits. Three wheel properties rotate around their axles. `sensor_yaw_degrees` uses +/-35 and `sensor_pitch_degrees` +/-15 visual limits. These are not real aircraft/sensor specifications. Return all angle properties to zero for rest. `E_controls_v005.json` lists controls.

Gear timeline: 1 standing; 65 main-gear rear swing; 100 inside/open doors; 120 retracted; 160 inspection with extended gear and open doors. Frame 130 opens doors before reverse movement. Gear motion remains `Gear_Retract_Illustrative`; kinematics and door timing are not authenticated. No hide/zero-scale retraction.

## Collections and export status

Standard collections: `00_REFERENCE`, `10_SOURCE`, `20_PRESENTATION`, `30_RIG_HELPERS`, `40_EXPORT`, `50_CAMERAS_LIGHTS`. Source groups include `ORION_GEAR`, `ORION_GEAR_BAYS`, `ORION_SENSOR_R3`, and `ORION_EXTERIOR_DETAILS_R3`. Retained construction cutters are hidden helper collections. `ORION_ASSET` publishes source/helpers without studio or references. Exclude construction cutters and presentation controls from exported geometry.

`ORION_PRESENTATION_CONTROLS` contains rigid pivots and `ORION_EXPORT_ARMATURE`. Bones follow controls, with nested leg/axle/wheel and yaw/pitch relationships. Each source object records its planned export bone. Source meshes remain rigid object-parented: optimized copies, rigid weights, baked clips, FBX basis testing and engine validation are Stage J work. A preview skeleton is not proof of working Reforger animation.

`ORION_PAYLOAD_SOCKET` is unplaced and hidden; it is not a verified carriage location. Banderol and Assembly remain reserved folders without completed models. Do not substitute the old generic missile.

## Dependencies and scope

Private reference images use relative paths under `Support/references_private`. Keep them for private review; redistribution permission remains unresolved. No reference photograph is an asset texture. Current materials are procedural review materials; UVs, decals and texture sets are Stage I. No gameplay-system changes were made.

Executed builders, renderers and validation files under `Support` supplement saved models. Current verification is `verify_E.py` and `inspect_E_checkpoint.py`; historical checks apply to their numbered stages.

See `E_REVIEW.md` for nine actual review renders and controls, `VALIDATION.md` for tests, and evidence/assumptions records for approximations. Master and numbered checkpoint reopened in separate fresh Blender processes; a relocated copy resolved image paths.

After Stage E visual acceptance, next is Stage F: Banderol reference lock and primary geometry. Assembly, final materials, game copies and packaging remain later milestones.




