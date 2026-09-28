# Assumptions and unresolved decisions

Current status: I v001 UV/material checkpoint awaiting review; approved source shapes retained. Historical stage notes below remain evidence/uncertainty records, not current review status. Hidden geometry and rack hardware remain visual approximations.

I-material assumption: clean, restrained paint and material-class values are plausible visual interpretations, not measured manufacturer paint/glass specifications. Authored source textures contain no reference photo pixels or invented markings. Curves remain procedural. Automatic source UV packing and source-surface normals form a Blender review baseline; final game UVs, mip checks and high-to-low bakes are deferred. See I_MATERIAL_REVIEW.md for measured approximate density and actual tests.

| ID | Objects/area | Current decision | Evidence/status | Revision trigger |
|---|---|---|---|---|
| A01 | ORION_ROOT | Origin at provisional longitudinal midpoint, centerline z=0 | C working datum; no measured station table | Selected variant measurement or corrected photo alignment |
| A02 | ORION_NOMINAL_LENGTH_8M / SPAN_16M | 8 m / 16 m nominal dimensions | Published family values, not R3 precision measurements | Reliable selected-variant dimensions |
| A03 | ORION_CAM_R3_INITIAL | Approximate 60 mm perspective camera; R3 backdrop | Unsolved; not a calibrated matched camera | Image-landmark calibration with compatible views |
| A04 | Nose, equipment, markings | R3 alone governs primary appearance | Direct visible evidence; full airframe identity unknown | Compatible original views establishing unseen features |
| A05 | Wings/tail/rear | Compatible R2 details only; paired canted tail; two-blade baseline | B layout, C detailed geometry | Compatible front/rear/top and R3 installation views |
| A06 | Gear bays | Closed 3D lining with restrained sparse supports | C invisible interiors | Photographs revealing the actual interior |
| A07 | Gear/door rig | Gear-down rest; illustrative motion unless documented | C; no rig created yet | Usable retraction sequence or unavoidable geometric conflict |
| A08 | Sensor | R3 aperture layout; separate yaw/pitch pivots | Visible A; hidden C | Compatible reverse-side and mounting views |
| A09 | Banderol body | About 5 m and 0.30 m nominal; no geometry yet | P3 published; illustration proportions unresolved | Attributable exterior evidence resolving discrepancy |
| A10 | Banderol ends/poses | R5 lower-left nose and upper-right rear as provisional interpretation | C; subject/provenance not locked | Reliable photo/footage disagreement |
| A11 | ORION_PAYLOAD_SOCKET | Hidden origin placeholder, expressly unplaced | No documented R3 station/rack | Usable original carriage evidence |
| A12 | Future assembly | Single provisional under-fuselage arrangement only if review supports placement | Reported carrier relationship; not authenticated R3 assembly | Rack/configuration imagery or scale/clearance conflict |
| A13 | Texture and LOD budgets | Approved starting allocations; no textures or LODs created | Practical targets, not measured performance | Real close-up defects, profiling or engine tests |

No geometry may be distorted to resolve assembly conflicts. Do not move the
sensor, reduce missile dimensions, widen gear or invent a mounting station.
Do not call the setup reference-faithful finished geometry or Reforger-ready.
No existing flight, Overwatch, thermal, HUD, tracking or weapon behavior is in scope.
# Stage C implemented approximations — revised v005

The primary station arrays are recorded in C_geometry_parameters_v005.json and
on ORION_FUSELAGE/ORION_NOSE_WHITE. They reproduce the selected visible contour
interpretation; hidden cross-sections are not measured. Nominal 8 m/16 m bounds
are validated, not independent measurements of the photographed R3 aircraft.

ORION_WING_ROOT_BLEND_L/R are restrained approximations. Wing airfoil sections,
exact flap/aileron stations, tail cant, rear collar/spinner and blade twist remain
C where photographs do not uniquely determine them. No aerodynamic claim is made.

All objects in ORION_LAYOUT_ENVELOPES_NOT_FINAL are placement proxies. Tire profiles,
gear articulation, bay openings and optical window layout are not accepted final details.
The sensor's generic volume must be replaced in D, not retained as the finished housing.
ORION_CAM_R3_INITIAL remains an approximate comparison viewpoint, not photographic calibration.

User review rejected the swollen forward shape in v002. R6–R8 photographs and
R9 illustration were supplied for correction. Forward body width now reduces
toward the nose, rather than increasing. The white shell begins at y=3.10 m
and ends at y=4.00 m; its length is 0.90 m rather than the rejected 1.50 m.
Join height is approximately 0.685 m instead of 0.95 m. These are visual
estimates, not measured reference dimensions. R6 exhibition equipment and
aft sensor configuration are excluded from the chosen R3 layout.
## R10 cross-section refinement — v006

The new 547x365 frontal-oblique exhibition photo corroborates a narrower crown
and wider lower corners. It is insufficient for precise station measurements.
The editable forward cross-section now shifts its widest region below the
mid-height and flattens the base, blending smoothly from y=1.70 to 3.10 m.
White-nose intermediate widths were refined; overall 8 m length and 16 m span
and the 0.90 m nominal white-shell length remain unchanged.
The mating boundary is inclined slightly (45 mm maximum top-to-bottom offset)
as a visual interpretation of the photographed seam. Hidden sections and this
seam inclination remain C approximations. The selected R3 equipment layout is
retained; R10 exhibition markings/equipment were not transferred.
Detailed gear, bay and sensor modeling stays paused for user shape review.
## Shared nose/body cross-section — v007

User explicitly requested the body have the same shape as the nose. The
previous v006 profile blend from y=1.70 to 3.10 m is superseded: all body
station rings now use the nose's normalized crown/cheek/base profile.
Station widths and heights still vary along the fuselage; overall dimensions,
white-nose contour and equipment positions are unchanged. Rear taper leads
into the separate propeller collar; hidden sections remain visual estimates.
The same-profile condition was checked on all 70 saved body rings against
the white-nose join ring, with normalized residual below 2e-6.

## Stage D v010 — gear, bays and sensor

The C v007 shape was approved before this work. Its 25 primary mesh vertex arrays are unchanged. Three retained Boolean cutters add real underside openings; they do not rescale or reshape the nose or body away from those openings.

**Class A/B:** overall three-wheel stance, visible main-strut rake, nose external coil, fork/hub character, R3 forward multi-window housing and visible side cover. Local dimensions and fastener placement remain approximate.

**Class C:** bay locations/lengths/roof height, liners, sparse supports, hinges, door division, exact gear mounting brackets, unseen sensor rear casing and optical-window depths. The upper gear attachment points were reconstructed inside the bays; the down wheel centres and airframe scale were preserved. These are visual art decisions, not measured interface positions.

Retraction is explicitly `Gear_Retract_Illustrative`. Main legs swing rearward before folding upward, with compensated wheel orientation. This sequence establishes a coherent digital pose path; it does not assert actual Orion kinematics. Door timing and closed flush presentation are inferred. No component is hidden or scaled to zero to simulate movement. Frame 120 is the illustrative retracted state; frame 160 is an inspection presentation with open doors and extended gear. The return path opens doors and reverses the two phases.

The bay liners are actual enclosed volumes with a roof, side/end walls, lips and door skin thickness. Exact unseen interior structure remains unverified. The turret has seven separate recessed optical surfaces arranged from R3, a fixed mount and separate yaw/pitch pivots. Presentation limits of yaw +/-35 degrees and pitch +/-15 degrees are visual limits only. Do not treat those as sensor performance.

Stage E full presentation controls/export skeleton, final UVs, finished texture sets, LODs and engine import are still future work. No Banderol geometry or carriage assembly is delivered at this checkpoint.

## Wing-root correction v012

The two wing-root fairings now physically overlap the fuselage instead of ending at an exposed outboard cap. Their inner caps are buried at +/-0.06 m; outer lofts return to the wing at +/-1.02 m. The closed lower root remains above the bay roofs until outside their width. Trailing coverage reduces before the flap begins, preserving the control-surface boundary. The topology is editable and the aircraft components remain separate. Exact fillet radius/section is class C; this is a visual connection correction, not engineering reconstruction. Nose/body proportions and the 16 m span are unchanged.

## Stage E v005 exterior assumptions

Visible dorsal dome, low cover, short red blade, left panel, triangular vent and forward underside apertures are based on compatible R3/R7 views. Presence/visible contour is A or B; exact metric placement, fastener count, shallow hidden backing and conformal fairing mounting completion are C. The dome's hidden support and vent/intake interiors are conservative closed surfaces, not authentic machinery.

Rear dorsal scoop follows R7 compatible exterior views; unseen internal shape is C. Tip housings/projections use compatible R2/R7 photographs; right-side green lens is a conventional visual approximation, not directly proven for this airframe. Yellow blade-tip paint follows R7; precise paint boundary is estimated. Do not import 01/03 markings, aft sensor pods or test probes.

Presentation limits (+/-8 control surfaces, +/-35 yaw, +/-15 pitch) are clearance-reviewed visual ranges, not operational specifications. Gear remains an illustrative reconstruction. The 23-bone hierarchy follows presentation controls but game weights and baked engine clips are deferred. Opposite-side service-panel duplication was not invented. Exact minor markings and further seams require legible compatible evidence and belong to later material/detail review.

## Camera correction E sensor v007

R11 refines compatible turret appearance only. The camera sits 0.12 m closer to the fuselage; actual datum is estimated from photographs, not measured. Fixed saddle follows the existing underside directly. Collar/top bridge overlap the aircraft attachment region intentionally and are not physical engineering interfaces. Hidden mounting completion remains C.

Seven separately recessed ports follow the curved casing; optical coatings are restrained colour approximations with no inferred specifications. The opposite cheek is conservatively symmetric. R11's exhibition marking/straps are excluded. Yaw +/-35 and pitch +/-10 are clearance-tested presentation ranges. The earlier +/-15 pitch conflicted with mounting geometry and is superseded by a clamped +/-10 driver. Game weights/engine clips remain deferred. E sensor v001-v006 are diagnostic, v007 is the review candidate.

## Banderol Stage F v002

5.000 m model length and 0.300 m body width are nominal choices from approximately reported values, not measured accuracy. A 2.20 m wing span is a provisional candidate from the ambiguous official Size entry; reject or revise if clearer span evidence appears. Root properties and F_parameters_v002.json record parameters but are not live geometry controls.

BDL_NOSE and BDL_BODY changing sections are C illustration-based reconstruction. Wing locations, sweep, thickness, root fairings and tail metrics are C. BDL_TAIL_TOP/L/R represent three visible directions in the attributed rear photo plus compatible illustration; the lower cropped/damaged view does not prove there is no fourth fin. No unsupported fourth fin added. Rear lip/recess presence is photographic; pristine dimensions, closed backing and interior finish are restrained C. No propulsion internals.

Only illustrated deployed wings exist; stowed configuration, transition and functional mechanism are unresolved and omitted. Banderol and Orion remain independent; no carriage placement/rack or mesh-clearance result yet. No aircraft, sensor or gear reshaping to fit a payload. F is a reference-limited exterior checkpoint, not final source fidelity or engine readiness.

## G v002 supersedes F shape/span candidate

R12/R13 illustration-based body height 0.33 m, flatter-sided casing, revised fuller nose; nominal length 5 m and width 0.30 m retained. Front-render span/width ratio ~3.1 gives provisional 0.946 m span, superseding unverified F 2.2 m candidate. Side slenderness/nominal dimensions remain uncertain rather than claiming all render ratios verified. Tail positions and dihedral, fine seams, fastener count and top-loop geometry/colour are C. Existing top fin interpreted as thin front projection; no additional needle antenna. No functional mount/deployment claims. This is a visual revision, not photographic authority or final engine asset.

## G v003 — wing span correction supersedes G v002

Prior 0.946 m render-ratio span was not a reliable deployed metric estimate. Actual model wings now span 2.20 m, using the provisional interpretation of GUR Size 2.2 m entry; Ukrainian/Russian labels also generic Size, so measured span remains unverified. Overall geometry remains 5 m long and 0.30 m casing width, matching approximate reported values; casing height 0.33 m is estimated. R14 photograph supports straight narrow wing outline and approximate midbody location, not exact dimensions or confirmed deployed pose. New root leading station +0.30 m and chord ~0.35 m are C. No nose/body variant substitution, stowed mechanism or engineering interface. See G_WING_SIZE_REVIEW.md.

## R15 main-wing sweep correction G v004

User supplied render a810d03d-e8ad-4d6f-a2ea-457548f0a73e.png, private R15_Banderol_swept_wings.png. Authorship/date/rights unresolved. Compatible visual wing-sweep cue only, not metric or hidden mechanism proof. Estimated 12-degree rearward sweep added to the two main wing surfaces. All other base meshes retained. Provisional 2.20 m span unchanged; latest renders G v004.

## H provisional assembly — failed candidate, not approved carriage

**Current override, H compact v009:** user permits a shorter payload for appearance and requests realistic exterior hardpoint detail. New independent VisualFit master is 4.4 m (12 percent shorter than nominal source), derived by shortening central case stations, with component silhouettes retained. Original 5 m master remains available and unchanged. Placement (0,-1.26,-0.86) m and compact swept pylon are artistic choices, not documented real stations/rack dimensions. Pylon exterior seams/covers/fasteners are C completion; no functional release hardware. Tail and gear bays constrained placement; their shapes were not altered. Default pose/full rotor checks pass, complete illustrative gear movement remains unresolved. See H_REVIEW.md.

**Latest override, H support v007:** user requested a visible holder and rotor clearance. Lowered the payload to (0,-1.75,-1.22) m and created independent evidence-C visual support behind the main bays. Saddle, two cheeks, lower shoe and cover fasteners are conservative exterior completion, not authenticated rack hardware or release engineering. Explicit later visual-support authorization supersedes the earlier decision to display only an abstract alignment guide. Guide is hidden; real editable support geometry now joins the models visually. Both approved source files remain unchanged. Full rotor envelope/default-pose checks pass; illustrative gear movement still has contacts. Parent hierarchy travels with Orion. See H_REVIEW.md.

**Latest override, H v005:** user explicitly requested a clipping-free front-wing presentation. Assembly placement changed to (0,-1.75,-1.07) m while both source shapes/dimensions remain unchanged. Default gear-down surface checks pass; full illustrative retraction contacts remain. This is an authorized visual adjustment, not evidence of authentic station/rack position. v003 candidate described below is historical. Supplied image 84674c9d-6e18-4909-838e-446815e0cc77 is a compatible visual lead; original attribution/variant remain unresolved.

`BANDEROL_LINKED_PROVISIONAL` uses root translation (0,-0.70,-0.95) m and unchanged axes/unit scale. C visual assumption, not established from the blurred carriage frame. Visible extended wings retained; their real carried configuration is unknown. `ORION_PAYLOAD_SOCKET_PROVISIONAL`, `BANDEROL_ATTACH_ROOT_PREVIEW` and `ALIGNMENT_GUIDE_NOT_RACK` are local alignment helpers, not engineered interfaces or rack geometry. Original source helpers, geometry and sensor remain unchanged.

The candidate fails digital fit at gear-down and intermediate illustrative gear poses. Do not fix this by resizing payload, moving sensor, changing gear track or hiding parts. Clear compatible carriage imagery must establish configuration/position and wing pose before a future attachment revision. Inspection of a blurred rear frame cannot prove sensor absence. No claim that the failed candidate disproves all real carriage configurations. Stage I can treat the separate sources independently while authenticated assembly remains blocked. Detailed result H_REVIEW.md.
