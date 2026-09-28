# Reference evidence — Orion_R3 / Banderol

Status: Stage D v010, 2026-09-27. C v007 silhouette approved by the user. Detailed gear, three enclosed bays and optical housing are authored. Stage D component photographs P4/P5 were retrieved and visually inspected; hidden interiors and gear motion remain class C.

## Supplied reference matrix

| ID | Source | Subject/variant | Useful features | Reliability | Conflicts | Decision |
|---|---|---|---|---|---|---|
| R1 | User-supplied drawing; author/date unknown | 03 Orion illustration | Side layout, fairing leads | Low for measurement | Nose and projected surface overlap differ | Supporting projection; exclude nose and airframe number |
| R2 | User-supplied photograph; original credit unknown | Airframe 01 | Wing underside, gear, rear openings, canted tail | Visible photographic features; compatibility conditional | Pointed nose, aft equipment and projecting test-style items | Compatible structure only; exclude conflicting equipment and markings |
| R3 | User-supplied ramp photograph; credit/date unknown | Selected grey airframe, white nose, forward turret | Nose boundary, contours, windows, gear and visible surface finish | Primary visible appearance; perspective limits dimensions | Incomplete rear/top/bay coverage | Governs the new Orion configuration |
| R4 | User-supplied render; original source unknown | Unidentified missile | Conflict identification | No authority for actual Banderol geometry | Faceted broad body and different appendages | Excluded from modeling authority |
| R5 | User-supplied render; original source unknown | Banderol-like illustration | Candidate orientation and exterior layout | Illustration only | Provenance and dimensions unresolved | Comparison lead only; never average with R4 |

Private originals are preserved without image editing in Support/references_private.
source_manifest.json records original paths, SHA-256 hashes and local paths.
The private audit scene includes these images for review; it is not a public package.

## Attributable public-source register

| ID | Publisher/source | Publication/date status | Supports | Limitations and reuse |
|---|---|---|---|---|
| P1 | [GUR Orion](https://war-sanctions.gur.gov.ua/en/page-orion) | Live page examined in prior planning pass | Published 8 m length / 16 m span; family component leads | Not measured station coordinates for R3; redistribution permission not established |
| P2 | [Kronshtadt Orion-E brochure](https://kronshtadt.ru/assets/files/productfiles/%D0%9E%D1%80%D0%B8%D0%BE%D0%BD_new/%D0%9E%D1%80%D0%B8%D0%BE%D0%BD-%D0%AD%202%20%28eng%29%20%282%29.pdf) | Indexed text inspected; direct PDF retrieval failed | Independent nominal 8 m / 16 m dimensions | Unseen PDF imagery not adopted; no permission to copy material inferred |
| P3 | [GUR Banderol](https://war-sanctions.gur.gov.ua/en/page-s8000-banderol) | Live page and interactive illustration inspected in planning | About 5 m / 0.30 m; reported Orion carrier | Illustrated geometry is not photographic proof; ambiguous English Size value not a verified span |
| P4 | [GUR nose support photograph](https://war-sanctions.gur.gov.ua/en/components/part/4973) | Component page showed 03.11.2025 | Additional nose-gear exterior comparison | Compatibility with exact R3 assembly requires visual comparison |
| P5 | [GUR optical housing photograph](https://war-sanctions.gur.gov.ua/en/components/part/4997) | Component page showed 03.11.2025 | Multi-window housing comparison | Exact R3 installation and specifications not established |
| P6 | [GUR propeller photograph](https://war-sanctions.gur.gov.ua/en/components/part/4958) | Component page showed 03.11.2025 | Two-blade baseline | Exact R3 blade profile remains unresolved |
| P7 | [Secondary carriage research lead](https://wsem.ru/publications/krylataya_raketa_s8000_banderol_s8000_banderol_rossiya/) | Date reliability limited; original footage not retrieved | A pixelated television frame; lead toward original footage | Not rack or clearance evidence; article speculation excluded |
| T1 | [Bohemia FBX Import](https://community.bistudio.com/wiki/Arma_Reforger:FBX_Import) | Official wiki inspected via available Enfusion tool in planning | Blender +Y forward, Enfusion +Z forward; LOD naming | Exact exporter and skeleton basis still require live test |
| T2 | [Bohemia Textures](https://community.bistudio.com/wiki/Arma_Reforger:Textures) | Official wiki inspected in planning | TIFF source, suffix profiles, DirectX normals | Channel diagnostic test required before material conversion |
| T3 | [Enfusion Blender Tools](https://community.bistudio.com/wiki/Arma_Reforger:Enfusion_Blender_Tools) | Bundled add-on source also inspected | Export/baking tooling; Blender compatibility baseline | Not enabled/tested in 5.2 during A/B |

No public-site 3D asset or third-party texture has been downloaded, extracted or used.

## Major-feature evidence and later implementation gates

A = directly visible photographic feature; B = compatible corroboration;
C = restrained visual approximation or illustration-only support.
Source attribution of the supplied photos remains unresolved, even for A entries.

| Planned component | Class | Basis | Modeling constraint / next evidence |
|---|---|---|---|
| ORION_FUSELAGE / ORION_NOSE_WHITE | A visible; C hidden sections | R3 | Curved upper profile, broad shoulders, flatter underside; no generic hemisphere |
| ORION_WING_L/R / root transitions | B visible layout; C exact section | R2, R3 | Match compatible views; do not treat R1 as a blueprint |
| ORION_FLAP_L/R / AILERON_L/R | B/C pending divisions | R2 | Confirm exact compatible divisions before cutting surfaces |
| ORION_TAIL_L/R / ruddervators | B layout; C exact cant/profile | R2, published family images | Paired canted tail; obtain rear/front corroboration |
| ORION_PROPELLER / rear housing | B blade-count baseline; C local profile | P6, R2 | Two blades, independent hub pivot; verify R3 rear installation |
| ORION_GEAR_NOSE / MAIN_L/R | A exposed parts; C hidden attachments | R3, compatible R2/P4 | Match stance first; inspect both sides before asymmetry assumptions |
| ORION_BAY_NOSE / MAIN_L/R | C interiors and hidden openings | Partial visible photo leads | Actual closed liners; sparse supports; no invented machinery |
| ORION_GEAR_DOORS / motion | C until sequence found | R2 partial openings | Illustrative timing/path; preserve supported exposed areas |
| ORION_SENSOR_MOUNT / YAW / PITCH | A visible face; B comparison; C hidden side | R3, P5 | Recessed separate optical surfaces; no exact sensor specification claims |
| ORION_SMALL_APERTURES | A | R3 underside nose | Separate from large optical turret |
| ORION_ANTENNAS / lights / panels | A visible; C unseen side | R3 | No R2 prototype equipment or unrelated airframe markings |
| BDL_BODY / NOSE / WINGS / TAIL / REAR | C currently | P3 illustration, R5 comparison | Full reference lock after Orion geometry review; R4 excluded |
| BDL_STOWED_POSE | Unresolved | Additional footage required | Do not invent mechanism; omit unsupported pose |
| ORION_PAYLOAD_SOCKET / adapter | Unplaced; C candidate | P3 carrier report; pixelated P7 lead | Carrier report is not proof of this R3 rack or configuration |

## View acquisition backlog

Orion: both sides, front/rear, top/underside, nose transition, wing roots and
trailing divisions, rear/propeller, both main assemblies, bay doors/lining,
retracted state and compatible sensor reverse side. All still require comparison
or additional evidence; the setup cameras do not supply missing references.

Banderol: exterior photos or attributable footage confirming nose/rear,
cross-section, tail count, wing configuration and carriage. Original carriage
footage/timestamps have not been established. Proceed only with explicitly
labeled evidence-limited reconstruction if these remain unavailable.
# Additional user references — nose correction, 2026-09-27

| ID | Source | Subject/variant | Useful features | Reliability | Conflicts | Decision |
|---|---|---|---|---|---|---|
| R6 | New supplied high-resolution exhibition photo; original attribution unknown | Aircraft 03, exhibition configuration | Nearly side-on forward contour, body/nose proportion | Direct photo, perspective limits | Aft pod, display equipment, markings differ from R3 | Compatible contour only; no equipment/markings transfer |
| R7 | New supplied ramp photo; original attribution unknown | Three grey/white-nose aircraft, compatible with R3 appearance | Forward taper, short white shell, wing-root relationship | Direct photo, perspective limits | Different airframes cannot establish identical hidden details | Main new corroboration for R3 nose proportions |
| R8 | New supplied airborne photo; attribution unknown | Grey/white-nose Orion | Whole silhouette and side outline | Direct photo, low resolution | Detail cannot be resolved | Broad proportion support only |
| R9 | New supplied transparent-background illustration/render; author unknown | Orion-like rendering | User-indicated side-shape comparison | Illustration only | May contain inaccurate geometry/equipment | Supporting comparison; not independent proof |

Copied unchanged as private R6–R9 images; hashes and paths recorded in
additional_reference_manifest.json. Attribution/redistribution rights remain unresolved.
The revised geometry is not yet user-accepted; prior technical mesh checks were
not a substitute for reference fidelity.
## R10 — additional nose view, 2026-09-27

User-supplied frontal-oblique exhibition photograph, 547x365 pixels. Original
publisher/date and exact airframe identification are unresolved. Direct visible
silhouette supports comparison of the narrow crown, fuller lower sides and
flattened base; low resolution and perspective prevent precise cross-section
measurement. Use alongside R3/R7 and the compatible side silhouette, not as
authority for hidden geometry, exhibition equipment or markings.
Preserved unchanged at Support/references_private/R10.png; SHA-256 and reuse
status are in R10_reference_manifest.json. Private reference only.


## Stage D references and limitations — 2026-09-27

- P4: GUR nose-gear component photograph, https://war-sanctions.gur.gov.ua/en/components/part/4973 . Retrieved image preserved privately as `Support/references_private/P4_NoseGear.webp`. Visually inspected. Corroborates external coil, fork, wheel/hub and visible links; absolute dimensions and exact R3 compatibility remain unverified.
- P5: GUR optical-housing component photograph, https://war-sanctions.gur.gov.ua/en/components/part/4997 . Retrieved image preserved privately as `Support/references_private/P5_OpticalHousing.webp`. Visually inspected. Corroborates rounded housing, multi-aperture face and large side cover. The R3 face pattern governs this model; no exact sensor identity or specification is inferred.
- R3/R7: primary visible gear stance and forward turret placement; exact cavity stations and retraction sequence cannot be recovered from these photographs.
- The nose cavity and separate left/right main cavities are conservative lined reconstructions, not authenticated wheel-well measurements. The main doors use an inferred central hinge arrangement. Hidden roof supports are deliberately sparse.
- Reference pictures remain private, with unresolved redistribution permission. No photo is used as a delivered texture. No third-party geometry was extracted.


## Stage E v005 feature evidence register

| Feature / object prefix | Evidence | Classification and decision |
|---|---|---|
| DORSAL_WHITE_DOME / DOME_BASE | R3, R7 compatible ramp photographs | A visible fairing; C exact dimensions and conformal base completion |
| FORWARD_LOW_DORSAL_COVER / RED_DORSAL_BLADE | R3, R7 | A shape/placement; C dimensions; no function claim |
| LEFT_FORWARD_PANEL / LEFT_PANEL_VISIBLE_FASTENER | R3, R7 | A contour lead; C fitted positions/count; no invented mirrored right panel |
| LEFT_TRIANGULAR_VENT | R3, R7 | A visible triangular shape; C shallow closed interior |
| REAR_DORSAL_INTAKE / AFT_SHORT_DORSAL_AERIAL | R7 compatible rear area | A/B visible silhouette; C depth and hidden completion |
| FORWARD_UNDERSIDE_APERTURE | R3 | A two separate apertures; C metric dimensions and backing; distinct from optical turret |
| WING_TIP_LIGHT / SMALL_PROJECTION | R2 compatible wing structure, R7 | B housing arrangement; C exact size/right lens colour |
| PROPELLER_TIP_PAINT | R7 | A yellow tips; C exact boundary |
| Rig and 23-bone preview hierarchy | Model construction, no reference mechanism claim | C presentation ranges; gear motion illustrative; engine clips untested |

No new public-source retrieval or rights grant occurred in Stage E. Private references remain subject to earlier attribution/reuse limits. Prior mesh shapes are preserved; fuselage receives a retained shallow local vent cut. Review material colours are provisional pending Stage I neutral-material approval.

## R11 — supplied camera/mount close-up (2026-09-27)

Source: user attachment `C:/Users/david/AppData/Local/Temp/codex-clipboard-31fef8df-c60e-44f8-b67f-5ce133c7785b.png`, private copy `Support/references_private/R11_sensor_mount.png`. Original photographer/date and redistribution rights unresolved. Photographic exhibition airframe marked 03, not proof that every installation matches the selected R3 airframe. Use only compatible forward turret shape and mounting relationship, corroborated by R3; exclude lettering, restraints and temporary ground cables.

A: turret meets underside; broad curved side housing, rounded lower casing, large optical window, smaller differently coloured windows. B: compatible forebody turret placement and multi-aperture construction from R3/R11. C: metric dimensions, invisible rear/inner surfaces, exact port depths and angular motion. Source objects `ORION_SENSOR_*` record evidence status. E sensor v007 replaces flat-face optics and disconnected bars with native editable components.

## Stage F Banderol exterior lock — 2026-09-27

| ID/source | Inspection and supported features | Reliability / decision |
|---|---|---|
| P3 https://war-sanctions.gur.gov.ua/en/page-s8000-banderol | Page and interactive exterior visualization inspected; approximately 5 m length, 0.30 m housing diameter; Orion reported carrier | Official reported approximate dimensions. Illustration is C for geometric sections/placement; ambiguous 2.2 m Size is not verified span |
| P8 https://www.twz.com/air/new-small-russian-cruise-missile-captured-by-ukraine-intelligence | GUR-attributed rear photograph visually inspected via browser; circular rear rim/opening, top and two lateral tail directions | Conditional photographic evidence, primary source retrieval unresolved. A for visible features within attribution limits; C metric reconstruction. Cropped/damaged lower region cannot prove fourth fin absent |
| P9 GUR infographic republished in P8 / official interactive illustration | Wedge nose, long rounded body and illustrated appendage layout | Attributable reconstruction, not photographic/measured authority; C. No third-party model extraction |
| R5 supplied white-background render | Visually compatible with P9 illustration | Original authorship remains unresolved, no independent metric authority; retained comparison lead |
| R4 supplied sky-background render | Identity not established; different body/appendage geometry | Excluded, never averaged with R5 |

Primary release lead: https://gur.gov.ua/en/content/warsanctions-hur-mo-ukrainy-rozkryvaie-detali-novoi-krylatoi-rakety-rf-s8000-banderol . English retrieval returned 403. Original Facebook imagery link temporarily blocked. These were not bypassed and full primary-image access is not claimed. TWZ attribution was used to locate/inspect the rear photo, not to import models/textures. No downloaded third-party media were packaged this stage; no reuse permission granted.

See F_REVIEW.md for object-specific evidence and current v002 views. No exact R3 carriage configuration authenticated; no attachment geometry constructed.

## R12/R13 — supplied Banderol front and side renders, G v002

User attachments 7cb4e50e-f2eb-4fb7-a47d-0aee45b4c628 and 6d111b77-1321-4fd8-a564-09abd2e93577 identify S-8000 exterior. Private copies R12_Banderol_front.png and R13_Banderol_side.png. Source authors/date/rights unresolved; illustrations remain C geometric evidence. Rounded rectangular casing, fuller nose, lower main wings, fine inset nose perimeter, small external hardware and top loop guide revision. Tail projection interpreted conservatively; no needle antenna invented. See G_REVIEW.md. No third-party render redistributed as asset texture; no model extracted.

## R14 and refreshed size references — G v003

User supplied inclined-launcher photograph, private R14_Banderol_wings_photo.png. Original author/date/reuse unknown; matching imagery located in reporting on suspected ground launcher, not independently authenticated exact variant. Visible main-wing outline supports near-straight narrow visual surfaces; perspective/pose prevents direct span measurement. See G_WING_SIZE_REVIEW.md for locator URL. No photograph redistributed as texture. GUR Ukrainian https://war-sanctions.gur.gov.ua/page-s8000-banderol and Russian https://war-sanctions.gur.gov.ua/ru/page-s8000-banderol refreshed: 5 m approximate length, 30 cm diameter, generic Size 2.2 m. Last value remains a provisional span interpretation, not verified primary wingspan. Earlier render-derived 0.946 m span superseded explicitly.

## R15 main-wing sweep correction G v004

User supplied render a810d03d-e8ad-4d6f-a2ea-457548f0a73e.png, private R15_Banderol_swept_wings.png. Authorship/date/rights unresolved. Compatible visual wing-sweep cue only, not metric or hidden mechanism proof. Estimated 12-degree rearward sweep added to the two main wing surfaces. All other base meshes retained. Provisional 2.20 m span unchanged; latest renders G v004.

## H carriage evidence refresh — 2026-09-27

P10: July 13, 2026 Defense Express report, https://defence-ua.com/news/rf_pokazala_divnu_detal_na_bpla_orion_iz_jakogo_zapuskaje_s8000_banderol_po_ukrajini-23598.html . Published frame https://defence-ua.com/media/contentimages/ed06a547a3feb314.png visually inspected in browser: rear-facing aircraft, gear visible, underbody heavily blurred. Cannot establish payload silhouette, rack, wing pose, exact station or selected R3 sensor compatibility. Suggested sensor absence in reporting is not proven by the inspected blur. Secondary locator; original footage unverified. Reference-only, no third-party image downloaded or packaged and no redistribution permission established.

P11: September 8/9, 2026 TWZ exhibition report, https://www.twz.com/air/russias-new-stealthy-lower-cost-air-launched-standoff-weapons-on-display-in-egypt . Carriage social-post leads and changed exhibition exterior described; not proof of exact R3 configuration or authority to replace the approved model. P3 GUR carrier relationship remains distinct from authenticating an installation. H geometry placement is C, adapter absent. See H_REVIEW.md.
