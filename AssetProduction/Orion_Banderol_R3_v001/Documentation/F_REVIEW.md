# Banderol — primary exterior review F v002

2026-09-27. Separate editable Blender 5.2.2 source: [master](../Banderol/S8000_Banderol_Master.blend), preserved [checkpoint](../Banderol/checkpoints/S8000_Banderol_F_primary_v002.blend). Approved Orion E sensor v007 was not edited in this stage. Review this primary form before Stage G detailing.

## Geometry and evidence decision

Eleven independent closed source meshes: changing-section body, wedge-profile nose, lined rear cowling, separate rear rim, two main wings, two root fairings, and three tail surfaces. The rear recess has a closed backing; no internal systems are represented. Deployed illustration pose only; no unsupported stow animation or folding mechanism.

[GUR](https://war-sanctions.gur.gov.ua/en/page-s8000-banderol) reports approximately 5 m length and 0.30 m housing diameter. Modeled nominal extents are 5.000 m and 0.300 m. These reported approximate values do not prove exact silhouette or station dimensions. The page's ambiguous 2.2 m “Size” entry is retained as a **provisional 2.20 m wing-span candidate**, not a verified wingspan.

The official interactive illustration was visually inspected through its browser interface, without downloading/extracting a third-party model. R5 is visually compatible with that illustration but remains an unattributed render. R4 remains excluded: its identity was not established and its geometry differs materially.

A rear photograph attributed to GUR and republished by [TWZ](https://www.twz.com/air/new-small-russian-cruise-missile-captured-by-ukraine-intelligence) was inspected: it shows a round rear opening, upper fin and two lateral tail surfaces. Original primary image retrieval remains unresolved. Photograph cropping/damage does not prove the absence of a fourth surface. This checkpoint models the three visible directions; tail dimensions/sections and hidden completion are C approximations. Wreck damage is not copied.

Nose/body cross-sections, main wing placement, span, sweep and local fairings are C illustration-based reconstruction. They are not measured geometry. This is an evidence-limited visual exterior, awaiting form review. No detailed seams, markings or micro-hardware have been invented.

## Opening and editing

Scene `BANDEROL_GEOMETRY_REVIEW`; root `BANDEROL_ROOT`, identity transforms; metres, +Y forward, +X right, +Z up. `BANDEROL_ATTACH_ROOT` is an unplaced visual alignment helper. No Orion socket placement, rack, assembled carriage or clearance test is present yet.

Collections: `00_REFERENCE`, `10_SOURCE`, `20_PRESENTATION`, `30_RIG_HELPERS`, `40_EXPORT`, `50_CAMERAS_LIGHTS`. `BDL_ASSET` publishes source and helpers without studio/reference material. Export collection is empty. Meshes remain separately editable; roots intersect the body intentionally to avoid detached surfaces. Separate meshes are not welded into a single skin.

`F_parameters_v002.json` and root properties record nominal/provisional dimensions; they do not automatically regenerate geometry. Revise editable station geometry or retained support construction before final rigging/baking, and preserve a new numbered checkpoint. Do not distort the root with nonuniform scale to fit Orion.

Procedural review materials only; no external material image dependencies, linked Orion libraries or reference photographs in the master. UVs, detailed textures, optimized copies, LODs, collision, export rig and engine import remain later stages. No Reforger-ready claim.

## Actual review images

Ten renders generated from the fresh-opened v002 model and visually inspected. Orthographic views expose proportions; close-ups expose shell and root transitions. No depth of field or motion blur.

| View | Image |
|---|---|
| Perspective | [Hero](../Previews/Banderol_F_v002_Hero.png) |
| Front | [Front](../Previews/Banderol_F_v002_Front.png) |
| Rear | [Rear](../Previews/Banderol_F_v002_Rear.png) |
| Left | [Left](../Previews/Banderol_F_v002_Left.png) |
| Right | [Right](../Previews/Banderol_F_v002_Right.png) |
| Top | [Top](../Previews/Banderol_F_v002_Top.png) |
| Underside | [Underside](../Previews/Banderol_F_v002_Underside.png) |
| Nose/root close-up | [Nose](../Previews/Banderol_F_v002_Nose.png) |
| Rear close-up | [Rear](../Previews/Banderol_F_v002_Rear_Close.png) |
| Uniform clay | [Clay](../Previews/Banderol_F_v002_Clay.png) |

## Performed validation and limits

Master and numbered checkpoint opened in separate fresh Blender processes; standalone Banderol root present, Orion root absent. All 11 source meshes: zero nonmanifold edges, zero degenerate faces, positive signed volume. Seven wing/fairing/tail-to-body surface intersections confirm intentional embedded root interfaces. This does not establish welded topology or real attachment engineering. Reported nominal dimensions checked, original three mod asset SHA256 hashes unchanged, zero external file images.

Evidence: `F_validation_v002.json`, `F_renders_v002.json`, `Support/review_F_v002.log`. Initial v001 render pass stopped at an unretained clay review material; repaired. v001 top/underside and rear framing were inadequate; corrected cameras preserved in v002. Additional underside fill and clay override are renderer-local review settings. Both numbered geometry checkpoints remain preserved.

Not attempted: engine import, exported animations, relocated-package test, stowed pose, combined assembly or digital carriage clearance. Photography insufficient to authenticate exact R3 carriage. Stage G may proceed only after this form review; authentic-carriage status remains held for Stage H evidence.
