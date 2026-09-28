# Current H compact pylon v009 — shorter artistic fit and detailed support

User explicitly authorized shortening Banderol and requested a more realistic-looking hardpoint. Current assembly uses the independent `../Banderol/S8000_Banderol_VisualFit_Master.blend`: **4.4 m** actual length, retaining 0.30 m case width, original wing span and component profiles. The central body interval was shortened by 0.60 m; nose, tail and wing component shapes were retained and their stations translated. This is an artistic fit variant, not a revised measured real-world dimension. Original `S8000_Banderol_Master.blend` remains byte-identical and 5 m long.

The shorter instance now sits at (0,-1.26,-0.86) m: 0.49 m forward and 0.36 m closer to the fuselage than v007. Root scale remains one; no squash of the entire missile. Upper tail clearance limited how much further it could be raised. Orion's geometry, gear track and turret are unchanged.

`ASSEMBLY_COMPACT_VISUAL_PYLON` replaces the tall supports with 25 editable exterior meshes: a compact swept fairing, fuselage-conforming saddle, curved case-contact shoe, two side covers, narrow seam seals, small fastener heads and socket marks. Deliberate bevels, edge thickness and subtle paint/metal/rubber differences support close-up viewing. Hidden release hardware and internal mechanisms are absent. Exact real rack geometry remains unverified; this is labeled evidence C.

Four intentional mounting contacts pass. Default gear-down surface checks across seven aircraft groups pass with zero unintended intersections. Both blades/hub/spinner complete a 360-degree sweep with zero payload/pylon contacts. Illustrative retraction still has contacts and is not accepted as clear. Seven variant wing/fairing/tail-to-case contact checks and variant manifold/degenerate/positive-volume checks pass.

Current file `../Assembly/Orion_Banderol_Preview.blend`; numbered checkpoint `../Assembly/checkpoints/Orion_Banderol_H_compact_pylon_v009.blend`. Assembly contains three relative libraries: Orion, original Banderol for the separate scale scene, and the shorter VisualFit master for the carriage preview. All three were tested from a relocated folder. The original scale-review scene deliberately continues showing the nominal 5 m source.

Five v009 native renders visually inspected: `H_v009_Side.png`, `H_v009_Hero.png`, `H_v009_Pylon.png`, `H_v009_Underside.png`, `H_v009_RotorClearance.png` in `../Previews/`. Fresh separate-process reopens passed for original masters, shorter master/checkpoint, assembly/checkpoint and relocated assembly. `H_compact_validation_v009.json` and `Banderol_VisualFit_v001.json` record checks, geometry changes and limits. Stage I UVs/baking and engine validation remain pending.

---
# Current H support v007 — connected visual support and rotor clearance

User requested visible support and complete propeller clearance. Banderol is now at (0,-1.75,-1.22) m, 0.15 m lower than v005. Aircraft and Banderol source masters remain byte-identical. `ASSEMBLY_VISUAL_SUPPORT_APPROXIMATION` contains eight editable meshes: a conforming upper saddle, two closed support cheeks, lower contact shoe and four restrained exterior cover fasteners. The adapter is deliberately an evidence-C visual approximation, not a documented rack, release assembly or engineering interface.

The support sits behind the main gear bays, visibly meets the fuselage and Banderol, and avoids default gear-door intersections. An initial unsaved adapter attempt across the main bays was rejected by collision checks. Upper saddle/fuselage, lower shoe/casing and both support/rail interfaces have tested intentional contact. Base adapter meshes have no manifold/degenerate/negative-volume defects. No hidden mechanisms are invented.

Both blades, hub and spinner were tested at every whole degree through a full 360-degree sweep. Zero payload/adapter surface contacts. The conservative complete swept cylinder also excludes overlapping payload bounds, with a positive radial gap. This is a digital visual clearance check only. Default gear-down checks across seven source component groups also show zero unintended contacts. Full illustrative gear-motion contacts remain and are recorded; animated carriage is not accepted.

The Banderol instance, adapter root and preview helpers are parented to the aircraft instance. A translation test confirmed that they travel with Orion; unchanged world matrices preserve the v006 render result. They remain independently selectable and their source masters remain independent.

Current assembly `../Assembly/Orion_Banderol_Preview.blend`; new numbered `../Assembly/checkpoints/Orion_Banderol_H_support_v007.blend`, with v006 geometry checkpoint preserved. Four actual inspected renders `H_v006_Side.png`, `H_v006_Underside.png`, `H_v006_Support.png`, `H_v006_RotorClearance.png` also represent v007, whose only change is parenting with identical evaluated positions. Records: `H_support_validation_v007.json`, `H_validation_v007.json`. Exact rack/station remains approximate; no source, gameplay or engine resources were changed.

---
# Current H v005 — front-wing/gear clearance correction

User requested a visual placement correction using supplied flight image 84674c9d-6e18-4909-838e-446815e0cc77.png. Banderol instance moved rearward 1.05 m and downward 0.12 m relative to H v003, to root (0,-1.75,-1.07) m. Approved source shapes, wing span, aircraft gear/sensor positions and scales remain unchanged. This supersedes the v003 placement, not its historical evidence limits.

**Gear-down pose: zero sampled surface intersections across the six aircraft groups, including both Banderol main wings, nose gear, main wheels and neutral propeller.** The full 160-frame illustrative gear sweep still reports contacts; this revision clears the requested presentation pose, not the entire animation. Exact station/rack remains a provisional artistic alignment. No physical rack was invented.

Current file `../Assembly/Orion_Banderol_Preview.blend`; preserved `../Assembly/checkpoints/Orion_Banderol_H_front_clearance_v005.blend`. Three native renders reopened/generated/visually inspected: `../Previews/H_v005_Side.png`, `H_v005_FrontClearance.png`, `H_v005_Underside.png`. Fresh-process canonical reopen resolved both libraries, private image paths and linked animation. `H_clearance_v005.json` contains contacts and limitations. v004 was diagnostic because it introduced a rear propeller contact; v005 lowers the instance to remove that default-pose overlap. Prior checkpoints remain preserved.

---
# Stage H v003 — linked scale and failed provisional fit review

2026-09-27. The approved Orion E sensor v007 and Banderol G wings v004 masters are byte-identical to their files before this stage. This checkpoint creates a separate linked preview; it does not modify either model or claim an authenticated carriage installation.

## Files and opening

- `../Assembly/Orion_Banderol_Preview.blend`: current review scene.
- `../Assembly/checkpoints/Orion_Banderol_H_review_v003.blend`: preserved checkpoint. v001/v002 are earlier diagnostic/presentation iterations.
- `../Orion/Orion_Master.blend`: independent authoritative aircraft source.
- `../Banderol/S8000_Banderol_Master.blend`: independent authoritative payload source.

Open the assembly in Blender 5.2.2. Default scene `H_CARRIAGE_DIAGNOSTIC`, frame 1, camera `H_SIDE`. Scene `H_SEPARATE_SCALE_REVIEW` shows the independent models at the same metric scale. Collection instances are independently selectable; detailed component editing stays in the source masters. Libraries use `//../Orion/Orion_Master.blend` and `//../Banderol/S8000_Banderol_Master.blend`; checkpoint paths are remapped relative to their folder.

The diagnostic has cameras `H_SIDE`, `H_UNDERSIDE`, `H_FORWARD_FIT`, `H_RETRACTED`. Frame 80 exposes gear-motion collisions; frame 120 is the approved illustrative retracted state. The saved default includes the side-camera caption. For alternate interactive camera renders, switch the local caption visibility to that camera's caption; the delivered PNGs already do this. No hidden source components are removed to clear the payload.

## Evidence and configuration decision

GUR reports Orion as a carrier but does not document this selected R3 airframe, rack or carried wing configuration: [official Banderol page](https://war-sanctions.gur.gov.ua/en/page-s8000-banderol).

The July 13, 2026 [Defense Express report](https://defence-ua.com/news/rf_pokazala_divnu_detal_na_bpla_orion_iz_jakogo_zapuskaje_s8000_banderol_po_ukrajini-23598.html) republishes a blurred rear-quarter/rear carriage frame. Its [image](https://defence-ua.com/media/contentimages/ed06a547a3feb314.png) was visually inspected in the browser. The underbody region is obscured; rack silhouette, precise payload placement and sensor configuration cannot be recovered. The article suggests an absent sensor, but the inspected blur cannot establish that conclusion. Original footage and the exact airframe configuration remain unverified.

The September 2026 [TWZ exhibition report](https://www.twz.com/air/russias-new-stealthy-lower-cost-air-launched-standoff-weapons-on-display-in-egypt) provides further carriage leads and describes a changed exhibition exterior. It does not justify silently substituting that exterior for the user's approved reconstruction. It is a secondary locator, not new metric authority.

Therefore no detailed adapter is fabricated. The amber line is an abstract alignment guide, expressly **not a rack**. Helpers `ORION_PAYLOAD_SOCKET_PROVISIONAL` and `BANDEROL_ATTACH_ROOT_PREVIEW` are local scene helpers; source helper coordinates remain unchanged.

## Diagnostic alignment and actual result

The single centreline candidate uses Banderol root translation `(0, -0.70, -0.95)` metres, unchanged axes and unit scale. This is a C assumption chosen for a visual feasibility review, not a traced or verified station. The candidate keeps visible extended wings because no accepted stowed/carried configuration is known. It preserves aircraft shape, sensor placement, gear geometry and Banderol dimensions.

**Result: FAILED provisional mesh fit.** At frame 1, the Banderol nose intersects nose-gear strut/link geometry; each main tire intersects the corresponding Banderol main wing. Further intersections occur between moving gear and the Banderol casing during the illustrative gear animation. The tested neutral sensor and static airframe surfaces produced no sampled surface-contact records; that is not proof of full clearance. Retraction endpoint alone would conceal the intermediate and ground-pose failures.

`H_clearance_v001.json` records the unchanged v001-v003 alignment audit: all 160 frames, six aircraft component groups, 3,527 overlapping-bounds triangle-surface comparisons and 1,303 object-pair/frame contact records. These counts are diagnostic records, not 1,303 independent design defects. Surface BVH intersection checks do not prove signed-volume clearance, minimum distance, airworthiness or operational compatibility. Curve details, combined sensor/control extremes and a separate assembly propeller sweep were not tested.

Do not interpret this failed candidate as proof that every real Orion/Banderol configuration is impossible. Unknown rack position, a different carried wing pose and uncertain airframe configuration remain decisive evidence gaps. They will not be resolved by changing approved geometry without references.

## Render evidence

Six native Blender neutral renders, visually inspected:

| File in `../Previews/` | Purpose |
|---|---|
| `H_v003_Scale.png` | Separate metric-scale comparison, no carriage claim |
| `H_v003_Side.png` | Provisional centreline arrangement, gear down |
| `H_v003_Underside.png` | Full underside and extended wings |
| `H_v003_Conflict.png` | Nose gear / payload intersection close-up |
| `H_v003_MotionConflict.png` | Frame 80 gear-motion failure |
| `H_v003_Retracted.png` | Frame 120 endpoint; does not establish animation clearance |

## Validation and next gate

`H_validation_v003.json` records fresh-process reopens of both source masters, the assembly, numbered checkpoint and a relocated folder copy. Both relative libraries and private reference-image paths resolved; linked gear animation evaluated and mesh instances were present. Source SHA256 hashes remain unchanged. Blender background access and native renders were used; interactive GUI modeling inspection and Reforger import were not performed.

Stage H's diagnostic deliverable is available for review. **Authenticated carriage acceptance remains blocked by evidence, and this candidate fails fit.** The separate masters can proceed to Stage I UVs/materials after this review; no combined carriage success or Reforger readiness is implied. A future authenticated assembly requires compatible carriage imagery before any rack, socket or wing-pose revision.
