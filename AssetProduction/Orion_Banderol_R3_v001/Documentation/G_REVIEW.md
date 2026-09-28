# Banderol shape/detail correction — G v002

Current independent master: `../Banderol/S8000_Banderol_Master.blend`. Preserved checkpoint: `../Banderol/checkpoints/S8000_Banderol_G_shape_v002.blend`. F v001/v002 and diagnostic G v001 remain preserved. Orion E sensor v007 was not edited.

## New reference decisions

R12: user front render, private `Support/references_private/R12_Banderol_front.png`. R13: user side render, private `Support/references_private/R13_Banderol_side.png`. Original author/source/date and redistribution permission unresolved. User identifies subject as S-8000 Banderol. These are illustrations, not photographs or measured blueprints; identity/proportions are accepted for this visual revision without upgrading them to photographic proof.

Both refine the casing toward a rounded rectangular section with flatter flanks, rounded shoulders and a flatter lower contour. The nose now continues that section, with fuller shoulders and a longer upper taper to a low point. A separate fine perimeter line represents the inset nose boundary visible in R12. R13 guides the smooth side transition; it does not establish measured cross-sections.

R12's wing span/body-width ratio is approximately 3.1. The F candidate 2.20 m span was inconsistent with this illustration and came from an ambiguous official Size entry. G therefore uses a **provisional 0.946 m deployed span**, while retaining the previously adopted nominal 5.0 m length and 0.30 m casing width. Casing height is now an estimated 0.33 m. These nominal dimensions and new rendered proportions are not a coherent measured blueprint: side-view slenderness is still uncertain. No new dimensions are claimed verified, and no source geometry was rescaled to fit Orion.

Main wings sit at the lower casing edge; paired lateral tail surfaces now sit lower with slight outward/down inclination to match the front illustration. Their depth order and angles remain C interpretations; no folding/stowed mechanism added. The existing top tail fin can explain the thin vertical projection in R12, so no separate unsupported needle antenna is invented.

## Added editable exterior detail

Three fine casing boundaries, inset nose outline, fourteen small exterior fasteners, slimmed root fairings, two rounded wing-root covers, bronze-coloured top loop and its base, and restrained rear underside external cover. Geometry, counts, local placement, colour and hidden completion are C illustration-based choices. The top loop is visual geometry only, without a functional lifting/attachment claim. No lettering, dense rivets, invented internal equipment or guidance/propulsion components.

29 independent mesh objects plus five editable curves in `10_SOURCE`; `BDL_ASSET` still excludes studio/reference content. Review materials remain procedural, with zero external file images. Published metre and +Y forward/+X right/+Z up conventions unchanged. Recorded root dimensions and `G_parameters_v002.json` are documentation properties, not automatic shape controls.

## Actual model views

| View | Image |
|---|---|
| Front, compare R12 | [Front](../Previews/Banderol_G_v002_Front.png) |
| Side, compare R13 | [Right](../Previews/Banderol_G_v002_Right.png) |
| Opposite side | [Left](../Previews/Banderol_G_v002_Left.png) |
| Perspective | [Hero](../Previews/Banderol_G_v002_Hero.png) |
| Rear | [Rear](../Previews/Banderol_G_v002_Rear.png) |
| Top | [Top](../Previews/Banderol_G_v002_Top.png) |
| Underside | [Underside](../Previews/Banderol_G_v002_Underside.png) |
| Nose | [Nose](../Previews/Banderol_G_v002_Nose.png) |
| Rear detail | [Rear detail](../Previews/Banderol_G_v002_Rear_Close.png) |
| Uniform clay | [Clay](../Previews/Banderol_G_v002_Clay.png) |

## Tests performed and outstanding

Fresh master and numbered checkpoint opened in separate Blender processes. All 29 base meshes: zero nonmanifold edges/degenerate faces, positive signed volume. Five curves: finite editable control points; they were not converted for mesh-manifold tests. Seven main-wing/fairing/tail roots intersect the casing at intended interfaces; independent intersecting meshes are not welded skin or engineering interfaces. Nominal length/width checked; original three mod assets rehashed unchanged. Ten actual G v002 renders generated and visually inspected, with no depth of field or blur. G v001 exposed floating crown fasteners and oversized fairings; G v002 seats fasteners on the casing and slims the fairings.

Reports: `G_validation_v002.json`, `G_renders_v002.json`, `Support/review_G_v002.log`. Detailed material/UV approval, baked textures, game meshes, export rig, LODs and engine import are not completed. Stowed poses and exact Orion carriage remain unresolved. No combined scene or carriage clearance test performed. Review revised front/side form before proceeding further.
