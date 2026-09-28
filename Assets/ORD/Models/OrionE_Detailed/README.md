# Orion-E detailed exterior

Open **OrionE_Detailed.blend** in Blender. Revision 04 includes nine inspection cameras, studio lighting, editable materials and the custom outlined ORiON-e wordmark. Five distinct supplied photographs are packed into hidden viewport reference objects for personal reference. Earlier models and generators are preserved in `Revision_01`, `Revision_02` and `Revision_03`.

## Revision 04: high-resolution photographic reference

The latest 5184 x 3456 photograph supersedes the small exhibition image for proportions and surface details. The white nose is longer (boundary Y = 1.18 m), with a more gradual crown, flatter underside and graphite accent near the lower tip. The forward grey fuselage is longer and the main wing leading edge has moved aft to Y = -0.95 m. Main gear positions and struts follow this revised arrangement.

At the user's explicit request, the optical camera **remains ahead of the nose gear**: turret Y = 2.52 m and nose axle Y = 1.45 m. This intentionally differs from the large rearward underbody pod in the latest photograph.

The primary aircraft name is no longer a system font. `ORION-e_vector_wordmark.svg` is an editable hand-drawn geometric reconstruction of the double-line ORiON-e logo, including the small i, outlined broad O's and lower-case e. The same paths are applied as thin surface-conforming mesh ribbons. The original font file was not available, so this is a visual reconstruction of the lettering, not a claim to have identified its original typeface.

Close-up details include rounded flush access seals, recessed screw heads and slots, red/white equipment tabs, caution and datum symbols, flatter main gear legs, brake lines, a cast nose fork, a pale ventilated nose-wheel rim, tread grooves, suspension damper and coil, safety pin and streamer, dorsal hatches, an amber beacon, fine cooling slots and ventral antenna housing. Incorrect oversized rivets, hatch-like rectangular borders and prominent hinge bubbles were removed. Detail is concentrated where it appears in the reference rather than represented by arbitrary polygon count.

Final renders: `Hero`, `Nose_Detail`, `Reference_Angle`, `Logo_Detail` and `Gear_Detail` are 3840 x 2560. `Side`, `Top`, `Forward_Profile` and `Rear_Detail` are 1920 x 1280. The perspective reference view intentionally crops the far wing tips, similarly to the supplied photograph; the full aircraft is visible in the hero/top views.

## Revision 03 silhouette changes

The latest small exhibition photograph is now the primary overall-shape reference. The model has a broader, fuller forward body, a blunter sloping nose and a flatter belly. The aft fuselage is slimmer. The white radome extends aft to Y = 2.08 m. Main wings are straighter and less tapered, with their roots raised to Z = 1.78 m to follow the new view. The V-tail spreads farther outboard (tip X = +/-1.72 m) and uses narrower chords. A small rear ventral antenna fairing has been added.

Surface seams, lettering, wingtip details and root fillets were repositioned with the new geometry. The optical turret remains ahead of the nose gear. `Reference_Angle.png` provides a lower, opposite-side view for comparing the silhouette with the latest photograph. Perspective and limited image resolution mean this remains a visual interpretation rather than a measured reconstruction.

## Revision 02 corrections

- Optical turret center is at Y = 2.52 m; nose-wheel axle is at Y = 1.78 m. +Y points towards the nose, so the turret is forward of the gear. Validation checks the entire turret envelope against the entire nose-gear assembly.
- White radome extended aft to Y = 2.40 m, with a fuller crown and flatter lower contour based on the new side photograph.
- Wing roots lowered and fillets reduced; V-tail height and propeller diameter reduced for a more restrained silhouette.
- Turret rebuilt with an upper shroud, bearing caps, a pale lower ball and conformal dark optical windows.
- Tyres rebuilt with a broad rounded crown, shallow tread channels and sidewall seams. Hydraulic hoses simplified and cylinder cap shading corrected.
- Smaller panel seals and latches, skin-conforming ORION-E lettering, revised aerials and a relocated pitot support.
- Added a dedicated `Forward_Profile.png` render to make the turret/gear relationship directly inspectable.

## Contents

- Smooth fuselage and white radome; airfoil-section wings and V-tail.
- Separate flaps, ailerons, ruddervators and twisted pusher blades.
- Surface-following service hatches, seams, fasteners, vents and aerials.
- Tricycle gear with rounded treaded tyres, rims, hub bolts, oleos, torque links, suspension coil and hydraulic hoses.
- Multi-aperture optical turret with bezels, coated windows and trunnions.
- ORION-E identification and small service markings.
- Nine PNG inspection renders, including five at 3840 x 2560.

Collections separate airframe, wings, tail, landing gear, optics, details, markings, studio and references. Tiny fasteners share mesh data. Materials use procedural surface grain and need no external texture files. Major surfaces have starter automatic UVs. Units are metres, X across the span, +Y towards the nose, +Z up. Approximate display dimensions: 16 m span and 8 m fuselage class.

## Scope and accuracy

This is an artistic exterior reconstruction from five distinct perspective photographs. Revision 04 prioritizes the latest high-resolution export-display view, with the user's requested forward-camera exception. Hidden details, exact airfoil profiles, mechanisms and tiny unreadable stencil text remain interpreted. It is not an engineering replica. Materials are procedural, not photographic PBR texture maps. Parts are editable but not animation-rigged. No game LODs, collision, damage setup, texture atlas or Enfusion import validation are included. Existing mod assets are untouched.

Research: the [Kronshtadt Orion-E brochure](https://kronshtadt.ru/assets/files/productfiles/Orion_eng.pdf), as indexed during this revision, specifies 16 m wingspan, 8 m length and 3 m height. Direct PDF retrieval timed out, so no unseen drawings were used. These establish a scale reference rather than exact measured station positions. The user photographs provide the visible geometry evidence; distances assigned to individual parts remain visual estimates.

The packed user reference photographs are not asserted to be licensed for redistribution; remove the reference collection/images before sharing the source publicly.

Rebuild using `Tools/build_orion_e_detailed.py` with Blender in background mode. Keep `Tools/orion_exhibition_details.py` alongside it; that file contains the photo-specific details and vector lettering. `asset_statistics.json` records generated geometry counts and `validation.json` records file and render checks.
