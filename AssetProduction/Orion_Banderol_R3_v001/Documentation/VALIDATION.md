# Current UV/material validation — I v001

Performed: eleven 4K texture sets; base UV face-area and bounds checks; zero native selected overlap loops across all atlases; preserved approved vertex/index geometry and component rest transforms; ten native renders visually inspected; nine fresh-process reopens of four sources, four numbered checkpoints and a relocated relative-link assembly, with no missing textures. See `I_MATERIAL_REVIEW.md`, `I_validation_v001.json`, `I_shape_preservation_v001.json`, `I_build_v001.json`, `I_pylon_v001.json` and `I_renders_v001.json`.

Earlier failed UV-check scripts and a temporary tail material-slot bake warning were repaired and the affected work rerun. Source-surface normal maps are not final high-to-low export maps. Evaluated-modifier UVs, game mesh UV efficiency/mip behaviour, AO and engine material conversion remain later checks. Combined gear retraction remains failed as recorded in H; default gear-down/propeller clearance is preserved by unchanged geometry. No engine test or new interchange export was attempted in I.

---
# Current compact pylon validation — H v009

Performed: actual VisualFit length 4.4 m and case width 0.30 m; original master hashes unchanged; variant base topology/positive volumes; seven intended wing/fairing/tail case contacts; 25 pylon base meshes checked; four intended support contacts; zero default unintended contacts across seven aircraft groups; complete 360-degree propeller surface sweep clear; five native renders visually inspected; seven fresh-process reopens including all masters/checkpoints and relocated assembly with three relative libraries.

Record `H_compact_validation_v009.json`. v008 geometry was adjusted cosmetically in v009 by narrowing cover borders within the same collision envelope and making new library paths relative. Earlier unsaved compact layouts that crossed the nose bay or upper tail were rejected. Full 160-frame illustrative gear sweep remains failed (contacts recorded), engine import and UV baking not attempted. Artistic 4.4 m length is user-authorized and is not claimed to be a real measurement.

---
# Current support and rotor validation — H v007

Performed: unchanged master hashes; eight editable adapter base meshes with zero manifold/degenerate/volume defects; six intentional interface contacts; full propeller sweep at one-degree increments and conservative radial-envelope exclusion; zero unintended default-pose contacts across seven aircraft groups; adapter/payload aircraft-parenting translation test; four native renders visually inspected. Fresh-process source/assembly/checkpoint/relocated reopens are recorded in `H_validation_v007.json`; detailed geometry checks are `H_support_validation_v007.json`.

Remaining failed check: intermediate illustrative gear poses intersect the payload. Carried wing pose, real rack and exact selected-airframe installation remain evidence-limited. No engine validation performed. v006-v007 have identical rendered world geometry; v007 changes parent hierarchy only. Initial unsaved saddle across bay openings was rejected; final support relocated behind bays. Previous records remain historical.

---
# Current front clearance — H v005

Performed: requested placement-only correction, source SHA256 preservation assertion, six-group evaluated surface intersection check at gear-down (zero contacts), full 160-frame illustrative gear check (contacts remain), canonical fresh-process reopen with two resolved relative libraries/no missing images, three native renders visually inspected. See `H_clearance_v005.json`, `H_reopen_v005.log` and `H_REVIEW.md`. Default visual clipping fixed; complete animated clearance and authentic carriage are not claimed. v004 was diagnostic and introduced a propeller contact removed in v005. Earlier records below are history.

---
# Current assembly validation — H v003

**Performed:** six native neutral renders and visual inspection; sampled evaluated surface checks across all 160 illustrative gear frames; source SHA256 preservation; separate fresh-process reopens of Orion, Banderol, assembly, numbered assembly and relocated assembly. Relative library paths and private image dependencies resolved. Linked mesh instances and gear motion verified. See `H_validation_v003.json`, `H_clearance_v001.json` and `H_REVIEW.md`.

**Failed:** proposed centreline visual alignment collides with nose gear and main wheels at gear-down, plus moving gear/casing contacts during retraction. This is one assumed candidate, not a real-world compatibility verdict.

**Blocked:** authenticated R3 carriage, adapter geometry and carried wing pose lack adequate evidence. **Not attempted:** combined sensor/control extremes, curve-volume/minimum-distance checks, combined propeller sweep, engine import, UVs/baking and game exports. The assembly is a diagnostic review deliverable; carriage acceptance has not passed. Source-stage verification history remains below.

---
# Current wing-angle correction — G v004

User R15 illustration (private R15_Banderol_swept_wings.png) requests modest main-wing angle. Both main wings now have an estimated 12-degree rearward leading-edge sweep beyond the root. This is a visual choice from perspective imagery, not a measured real configuration. Provisional tip span remains 2.20 m, length 5.00 m and casing width 0.30 m. Root positions, fairings, body/nose and tail were retained. All other base mesh vertex hashes match G v003.

Current independent master: Banderol/S8000_Banderol_Master.blend. New preserved checkpoint: Banderol/checkpoints/S8000_Banderol_G_wings_v004.blend. Previous files remain historical.

Performed: fresh master and numbered checkpoint reopens, 29 base-mesh manifold/degenerate/positive-volume checks, seven intended casing/root contacts, actual geometry dimensions, original mod asset hashes unchanged. Five curves remain outside base-mesh checks. Four actual renders generated and visually inspected: perspective, front, top and underside. G_validation_v004.json and G_sweep_change_v004.json record results. Game validation NOT ATTEMPTED. Images: Previews/Banderol_G_v004_Hero.png, Banderol_G_v004_Front.png, Banderol_G_v004_Top.png, Banderol_G_v004_Underside.png. Existing scale/evidence limits below remain applicable.

---
# Current Banderol — G wings v003

Actual geometry measured: length 5.000 m, casing width 0.300 m, main-wing span 2.200 m. Last is a provisional interpretation, not an authenticated drawing. Master/checkpoint reopened independently in fresh Blender processes. 29 base meshes have no manifold/degenerate/negative-volume defects; five source curves remain outside base-mesh checks. Seven intended wing/fairing/tail casing contacts passed. Ten new renders generated and visually inspected. No external file images. Original three mod asset hashes unchanged; Orion master SHA256 unchanged before/after. See G_WING_SIZE_REVIEW.md, G_validation_v003.json and G_Orion_preservation_v003.json. Engine/exports/carriage/stow tests NOT ATTEMPTED. G v002 0.946 m span is superseded.

---
# Current Banderol — G shape/detail v002

Separate master and numbered checkpoint reopened in fresh Blender processes. 29 base meshes: zero nonmanifold/degenerate defects, positive volume. Five curves have finite control points; curve mesh manifold checks not performed. Seven wing/fairing/tail root intersections retained intentionally. Nominal 5 m length / 0.30 m body width checked; estimated height 0.33 m and provisional span 0.946 m. Original three mod files rehashed unchanged. Ten actual G v002 renders generated and visually inspected. See G_REVIEW.md and G_validation_v002.json. Source curves remain editable, not game-ready topology. Engine/UV/export/assembly tests NOT ATTEMPTED. G v001 was diagnostic; v002 corrects floating fasteners, root fairing scale and front framing. Orion remains approved E sensor v007.

---
# Current Banderol checkpoint — Stage F v002

Performed 2026-09-27: independent editable master and numbered checkpoint freshly reopened in separate Blender processes. Eleven source meshes have zero nonmanifold edges and degenerate faces, all positive volume. Nominal model length 5.000 m, body width 0.300 m, provisional wing span 2.200 m. Seven wing/fairing/tail surfaces intersect body at intended root interfaces; separate mesh contacts are not welded topology/engineering proof. No external material file images. Original three mod asset hashes unchanged. Ten actual v002 model renders generated and visually inspected, including six directions, nose/rear close-ups, perspective and uniform clay. Evidence F_validation_v002.json, F_renders_v002.json and Support/review_F_v002.log.

Initial v001 render loop failed on an unretained clay material after nine renders; repaired and completed. Initial vertical/rear camera framing cropped geometry; v002 camera checkpoint corrects framing without geometry changes. Clay override and underside fill were refined in the review renderer. v001 remains preserved historical checkpoint.

NOT ATTEMPTED: Reforger import, exports, LOD/collision validation, stowed/deployment poses, combined assembly, carriage clearance or relocated-package test. UVs and production materials deferred. Approximate dimensions and illustration-supported sections do not authenticate real exterior metrics. Review F_REVIEW.md before Stage G.

Approved Orion remains E sensor v007; its historical tests below are not new tests performed this stage.

---
# Current review — camera correction E sensor v007

Performed: fresh master and numbered-checkpoint reopens succeeded; file-image paths resolved; non-sensor source vertex arrays equal restored E v005. Evaluated sensor meshes: zero nonmanifold/degenerate/negative-volume defects. Main optical housing against airframe/gear: zero contacts over 45 sampled frame/yaw/pitch combinations. Complete sensor against gear: zero contacts over all 160 gear frames. Moving sensor assembly against airframe/gear: zero unexpected contacts at the tested 18 combinations; 36 intentional collar/top-bridge attachment contacts retained explicitly. Housing against yoke, bridge, collar and fixed saddle: zero contacts at five pitch samples in the +/-10 range. Preview bone matrices match controls. Four actual v007 model renders generated and visually inspected.

Pitch +/-15 was rejected due to upper-mount interference; both property range and driver clamp now enforce +/-10. Limits and retraction remain illustrative. Engine validation NOT ATTEMPTED. Tests concern digital samples and surface intersections, not real-world compatibility or arbitrary combined poses.

Reports: `SENSOR_validation_v007.json`, `SENSOR_final_validation_v007.json`, `SENSOR_joint_validation_v007.json`. Original three mod assets were rehashed unchanged during correction. No gameplay/Banderol work. Prior checkpoint review images are historical.

Internal recovery note: an iteration inadvertently saved under the E v005 checkpoint filename. E v005 was restored from its previously verified relocation copy before final comparison; source vertex comparisons and dependency checks passed. Corrected save destinations remain in the support files. Sensor v001-v006 are superseded diagnostics.

---
# Current checkpoint — Stage E v005 (2026-09-27)

Status: Blender exterior/presentation checkpoint complete for user review. Engine validation NOT ATTEMPTED. Fresh master, numbered checkpoint and relocated copy opened successfully in separate Blender processes. All file-image dependencies resolved. Original three mod asset SHA256 hashes unchanged.

Performed: all prior mesh vertex arrays match approved D v012; source meshes closed/positive/nondegenerate; selected evaluated Boolean body/intake/forward-fairing meshes closed with zero degenerate faces. All driven controls visibly changed matrices at sampled nonzero angles. Sampled control-surface/sensor/propeller obstacle tests: zero contacts. Gear versus new exterior meshes: zero contacts in all 160 frames. Bone target matrix errors: zero at rest and additional propeller/sensor pose. Nested export preview hierarchy has 23 bones, source collection 263 objects.

Nine actual E v005 renders were generated and inspected, including neutral clay and the combined presentation pose. Reports: `E_validation_v005.json`, `E_checkpoint_reopen_v005.json`, `E_controls_v005.json`, `E_renders_v005.json`; additional intake image comes from the checkpoint inspection. Gear body/bay/door checks remain recorded in D validation; current E specifically rechecked gear against new exterior geometry. Tests do not establish all arbitrary control combinations or continuous physical clearance.

Not attempted/deferred: optimized meshes, UV baking/final textures, skinning game copies, interchange export, engine import, clips/TXA, real carriage assembly and Banderol. No engine-ready claim. Earlier E v001-v004 retained as superseded diagnostics. Historical sections below apply to their own checkpoints.

---
# Validation — production checkpoints

## Current D v012 wing-root correction — 2026-09-27

- Fixed the user-reported exposed inner wing-root faces. Two replacement closed fairings extend from +/-0.06 m to +/-1.02 m, with inner caps entirely buried in the evaluated fuselage and a tapered saddle into each wing. The trailing extent retreats before the moving flap starts.
- Only `ORION_WING_ROOT_BLEND_L/R` mesh vertex arrays changed relative to D v010. Nose, body, wing-tip span, all other source meshes, gear/bays/sensor and presentation actions are retained.
- Fresh-process root mesh checks: zero nonmanifold edges, zero degenerate faces, positive volume. Each of 128 inner-cap sample vertices is inside the evaluated body; maximum signed distance is approximately -0.01106 m for both sides. Intentional overlap attaches the fairings while keeping editable aircraft components separate.
- Checked all 160 frames for gear-to-new-fairing surface intersections: zero. Bay/door meshes and both flap meshes against the new fairings: zero surface intersections in the standing rest pose.
- Current master and v012 checkpoint reopened in separate Blender processes; all relative image dependencies resolved. Original project asset hashes remain unchanged. No export or engine test was repeated for this local source correction.
- Real before/after renders generated. Forward, three-quarter and top views inspected. Underbody render is an additional review view. No claim of an authentic measured root fillet or welded export topology is made; the root shape remains a restrained class C visual reconstruction.

Reports: `D_wing_root_change_v012.json`, `D_wing_root_validation_v012.json`, `D_wing_root_clearance_v012.json`. v011 is a diagnostic revision with a partially exposed inner cap; v012 supersedes it. Visual review is pending; Stage E has not begun.


## Historical Stage D v010 — 2026-09-27

**Technical checkpoint passed; visual acceptance pending.** The full asset, final textures/export skeleton and engine validation remain incomplete.

Performed in actual Blender 5.2.2 processes:

- Saved editable master and numbered checkpoint; 234 source objects. Reopened current master and a relocated copy in fresh processes. All file-image paths resolve relative to the packaged structure.
- Compared all 25 primary C mesh vertex arrays to the approved C v007 file: unchanged. The three retained cavity modifiers add openings locally without rescaling the airframe.
- All source base meshes: closed, positive-volume, no degenerate faces. Evaluated Boolean fuselage and optical housing: zero nonmanifold edges and zero degenerate faces, positive volume.
- Checked every integer frame 1-160: zero gear surface intersections against evaluated fuselage, bay liners/roof supports, door shells and optical housing. Also checked left/right main-gear mesh pairs through all 160 frames: zero intersections.
- Checked housing at nine combinations of yaw -35/0/+35 and pitch -15/0/+15 against body, nose and gear: zero surface intersections. This is a sampled visual range check, not exhaustive swept-volume or engineering validation. Intentional joints/bearings within assemblies are excluded from clearance claims.
- Original detailed Orion, game Orion and missile file SHA-256 hashes remain unchanged.
- Generated 17 real review renders: hero, forward detail, sensor, nose/main gear, bay interiors/underside, gear inside with doors open, retracted, inspection, and six neutral clay directions.

Reports: `D_validation_v010.json`, `D_final_validation_v010.json`, `D_construction_v010.json`, `D_renders_v010.json`. Earlier D diagnostic revisions found surface contacts and a cutter-transform/render artifact; these were corrected before v010 and are retained as history.

Unverified: authentic wheel-well structure, real retraction/door sequence, exact sensor identity and hidden housing details. Retraction remains labeled illustrative. Export skeleton, UVs/bakes, LODs, FBX and Workbench import: **not attempted at D**. Banderol and assembly: **not yet built**. Visual approval of this checkpoint is the next gate.


## Historical C v007 shared body/nose profile — 2026-09-27

- Applied the user's same-shape instruction throughout the fuselage, removing
  the former elliptical aft/mid-body profile and forward-only blend.
- Saved current master and numbered v007; retained prior checkpoints.
- Fresh-process master/checkpoint validation passed: 25 closed primary meshes,
  no degenerate faces, positive volume, identity root, 8 m/16 m bounds,
  resolved relative paths and unchanged original project asset hashes.
- Independently checked all 70 editable body rings against the normalized
  nose-join section. Maximum normalized-coordinate difference: 1.16e-7.
  Evidence: C_shared_section_v007.json and C_validation_v007.json.
- Exact hidden geometry remains approximate. Shape was approved by the user before D;
  detailed gear/bays/sensor and export work remain paused.
- Eleven actual v007 renders generated. Visually inspected front close-up,
  three-quarter close-up, complete hero, R3-like perspective, left profile and rear.
  C_renders_v007.json lists output paths. No photographic camera calibration claimed.

## Historical C v006 nose cross-section refinement — 2026-09-27

- User requested further shape refinement from the new frontal-oblique R10 photo.
- Executed Blender builder and saved master plus independent v006 checkpoint;
  all earlier checkpoints retained.
- Refined the crown/lower-cheek/base profile, forward section blending,
  intermediate white-nose widths and mating-boundary inclination.
- Fresh Blender process reopened both master and v006. All 25 primary meshes
  passed finite-coordinate, closed-manifold, face-area and positive-volume checks.
  Evaluated dimensions remain exactly 8 m / 16 m.
- Relocated fresh-process master resolves the five existing relative references;
  old project asset hashes are unchanged. R10 copy hash matches its supplied file.
- No detailed gear, bays, optical windows, rigging or export work performed.
- C_validation_v006.json records technical results. Photographic calibration and
  authentic hidden cross-sections remain unresolved. User visual acceptance pending.
- Generated eleven real model renders, including isolated front and three-quarter
  nose/forebody close-ups. Visually inspected those two, the side profile and R3-like
  perspective, plus the private R10 comparison board. Close-up cameras are created
  by the executed review renderer; the master retains its existing review cameras.
- C_renders_v006.json records render output paths. No generated reference imagery used.

## Historical C v005 nose correction — 2026-09-27

User rejected v002 for an enlarged nose/forward silhouette. Visual acceptance
is still pending; the earlier technical pass did not validate its proportions.

- Rebuilt and saved master plus separate v003/v005 checkpoints, preserving v002.
- Shortened white nose from 1.50 m to 0.90 m; reduced forward section at its
  join from 0.92 m to 0.69 m wide, and 0.95 m to 0.685 m high.
- Changed forward fuselage to taper gently; lowered the nose upper contour and
  retained its nearly level underside. Root scale and overall length/span remain unchanged.
- Extended sensor-mount and nose-strut envelopes to meet the revised underside;
  sensor center, gear axles, wing/tail and propeller positions were not moved.
- Fresh-process validation passed for master and v005: all 25 primary source
  meshes closed, finite, positive volume and without degenerate faces; 8/16 m bounds.
- Relative reference paths resolved from both saved locations and a relocated
  fresh-process master. Original source hashes remain unchanged.
- Four new supplied reference copies verified by hashes in additional_reference_manifest.json.
- R3-like viewpoint remains uncalibrated. Gear/sensor are unfinished envelopes;
  no stage D implementation or new engine/export testing was performed.

Evidence: C_validation_v005.json and C_geometry_parameters_v005.json.
Nine final v005 renders were generated; the final nose profile and perspective
were visually inspected after removing the intermediate revision's upturned tip.
Intermediate v003/v004 are retained as iteration records, not accepted geometry.

## Historical C v002 technical result — visual shape rejected

Primary geometry is saved and technically checked; visual acceptance remains pending.
The A/B record below is historical and describes the preserved B checkpoint.

- Executed the C builder in Blender 5.2.2 LTS; saved master and numbered v001/v002 checkpoints.
- Reopened master and C v002 without saving; 25 source meshes have finite coordinates,
  zero nonmanifold edges, zero faces below 1e-10 square metres, and positive signed volumes.
- Evaluated source bounds: 16.000 m span and 8.000 m length. Identity root and metric scale checked.
- Export collection is empty; gear/sensor proxies and studio are outside the published asset collection.
- Five relative reference dependencies resolve in both master and checkpoint.
- A relocated temporary package reopened in another fresh Blender process and resolved reference paths.
- Three original Blender assets retain their recorded hashes.
- Nine actual v002 renders were produced and visually inspected: six directional clay views,
  neutral hero, R3-like perspective and nose profile. No dramatic lighting or depth of field.
- Resolved v001 cap-subdivision scalloping at the nose boundary using preserved endpoint creases.
  Fixed the backwards nose inspection camera. Enlarged the floor to remove its visible edge.
- Machine evidence: C_validation_v002.json, C_renders_v002.json and C_geometry_parameters_v002.json.

Limits: R3 perspective is approximate, not a solved camera or quantitative overlay.
Technical closure does not establish authentic hidden sections. Primary component interfaces
intentionally overlap at roots/collars; no complete assembly intersection certification was performed.
Detailed bays, gear, sensor apertures, animation, UVs, final textures, exports and engine tests
are not yet implemented. Interactive Blender UI inspection was not performed.

## Historical A/B setup result

Date: 2026-09-27. Blender: 5.2.2 LTS.
Result: setup integrity checks passed; **not** aircraft geometry acceptance.
Stage A baseline is recorded; Stage B setup is ready for the user review gate.

## Performed and passed

- Executed the scene builder in actual Blender; saved Orion_Master.blend and
  the numbered Orion_B_reference_scale_v001.blend checkpoint.
- Reopened both saved files in a fresh Blender process without resaving them.
- Confirmed metric unit scale 1, identity ORION_ROOT and exact 8 m / 16 m guide
  endpoint distances. These validate setup values, not physical aircraft dimensions.
- Confirmed six directional cameras plus an initial R3 perspective camera and
  photo backdrop. The camera is explicitly unsolved.
- Confirmed source/export collections remain empty and private audit image
  planes are absent from the future ORION_ASSET assembly-link collection.
- Verified five relative image dependencies from both saved file locations;
  all five copies match the supplied originals' SHA-256 hashes.
- Reopened both files from a separately relocated temporary package using fresh
  Blender processes; all five relative image paths resolved. Temporary copies
  were removed after the test. No assembly file exists yet to test its links.
- Rendered and decoded two 2400 x 1200 PNGs: scale setup and private reference
  audit. Visually inspected both. Corrected clipped scale-preview title/footer,
  rerendered and visually inspected the corrected result.
- Confirmed recorded SHA-256 hashes of the three existing Orion/game/missile
  source assets remain unchanged.

Machine-readable evidence is in AB_validation.json and source_manifest.json.

## Failures resolved during creation

- Empty factory scene had no world datablock: added an explicit setup world.
- Relative image paths set before first save invalidated image dimensions:
  retained absolute loading paths until the master existed, then saved relative
  dependencies and checked them from both file locations.
- Initial top-camera framing clipped text: widened the orthographic frame and
  offset its center. Final captures show the complete labels.

## Pending or not attempted

- Actual aircraft silhouettes, nose/wing/tail station geometry and R3 camera
  matching: stage C, not attempted before the specified review gate.
- Gear/bay interiors, sensor details, rig, animation and collision clearance:
  stages D/E, not attempted.
- Banderol reference lock, independent master, poses and combined scene:
  stages F/G/H, not attempted.
- UVs, authored PBR maps, bakes, optimized meshes and LODs: stages I/J, not attempted.
- FBX export, TXA, skeleton basis test, channel diagnostic and Workbench import:
  not attempted. No Reforger-ready claim.
- Original carriage footage and exact R3 adapter/configuration: unresolved
  evidence, not concealed by a provisional socket at the origin.
- Interactive Blender UI inspection: not performed. Fresh-process background
  opens, data checks and real saved renders were performed.

## Review gate

The approved plan explicitly requests delivery of the first A/B checkpoint
before detailed modeling. No further asset production stage has been marked
complete. The next stage is Orion primary silhouette geometry after review.


Final visual inspection performed: v010 hero, forward detail, sensor, main-bay interior, front clay and underside clay; the corresponding v009 nose/main gear and retracted/nose-bay views were inspected before the final bearing-cap-only correction. All v010 views were rendered after that correction. The numbered v010 checkpoint also reopened in a fresh Blender process with all relative images resolved (`review_D_checkpoint_hero.log`). Hero was reframed at 40 mm to include the wing tips. No saved geometry changed during these renders.


The v012 underside root render was also visually inspected after generation; source correction remained local to the two fairings.




