# Current wing-angle correction — G v004

User R15 illustration (private R15_Banderol_swept_wings.png) requests modest main-wing angle. Both main wings now have an estimated 12-degree rearward leading-edge sweep beyond the root. This is a visual choice from perspective imagery, not a measured real configuration. Provisional tip span remains 2.20 m, length 5.00 m and casing width 0.30 m. Root positions, fairings, body/nose and tail were retained. All other base mesh vertex hashes match G v003.

Current independent master: Banderol/S8000_Banderol_Master.blend. New preserved checkpoint: Banderol/checkpoints/S8000_Banderol_G_wings_v004.blend. Previous files remain historical.

Performed: fresh master and numbered checkpoint reopens, 29 base-mesh manifold/degenerate/positive-volume checks, seven intended casing/root contacts, actual geometry dimensions, original mod asset hashes unchanged. Five curves remain outside base-mesh checks. Four actual renders generated and visually inspected: perspective, front, top and underside. G_validation_v004.json and G_sweep_change_v004.json record results. Game validation NOT ATTEMPTED. Images: Previews/Banderol_G_v004_Hero.png, Banderol_G_v004_Front.png, Banderol_G_v004_Top.png, Banderol_G_v004_Underside.png. Existing scale/evidence limits below remain applicable.

---
# Banderol wing/size revision — G v003

Current master: `../Banderol/S8000_Banderol_Master.blend`; preserved checkpoint `../Banderol/checkpoints/S8000_Banderol_G_wings_v003.blend`. G v002 and earlier files preserved. Orion master SHA256 before/after is identical; see `G_Orion_preservation_v003.json`.

## Size findings

Rechecked GUR's English, Ukrainian and Russian pages on 2026-09-27. [Primary Ukrainian page](https://war-sanctions.gur.gov.ua/page-s8000-banderol) explicitly lists length approximately 5 m, casing diameter 30 cm, and another entry labelled “Розмір” (size), approximately 2.2 m. The label is not unambiguously wingspan in any checked locale. Several secondary descriptions interpret it as span; this is not independent measured confirmation. No measurement was inferred from a truck tire or launcher.

| Dimension | Actual Blender geometry | Evidence status |
|---|---:|---|
| Overall length | 5.000 m | Matches adopted approximate GUR nominal value, not measured exact geometry |
| Main casing width | 0.300 m | Matches reported casing diameter; rectangular section shape remains reconstruction |
| Extended main-wing tip span | 2.200 m | Provisional interpretation of official Size entry; not authenticated metric drawing |
| Casing height | Approximately 0.330 m | Illustration-estimated, not published verified diameter in this direction |

Metre units, unit scale 1.0 and existing +Y forward/+X right/+Z up convention preserved. No nonuniform root scale applied. No export/import scale validation claimed.

**Correction:** G v002's 0.946 m span was inferred too directly from a rendered front-view ratio. That ratio could depict a different pose, perspective or incomplete extension; it was not sound evidence of deployed metric span. G v003 restores the stronger 2.2 m nominal candidate and records the uncertainty explicitly. Previous 0.946 m shape is retained only in its numbered historical checkpoint.

## R14 photograph and geometry decision

User attachment `codex-clipboard-e72beb45-8fa7-4664-8122-f9e470700cff.png`; private copy `Support/references_private/R14_Banderol_wings_photo.png`. Original photographer/date/permission not established. Visually matching imagery appears in reports on a suspected ground-launched Banderol display, including [Army Recognition locator](https://www.armyrecognition.com/news/army-news/2026/russia-moves-to-expand-s8000-banderol-cruise-missile-strike-options-with-a-suspected-mobile-ground-launcher). That is a provenance lead, not authenticated primary attribution, and does not prove exact air-carried variant compatibility.

Use visible narrow, near-straight main-wing outline and approximate midbody relationship. The photographed body/nose and rear details differ from prior renders, so they are not silently blended into this wing-only correction. Perspective, launcher angle and pose prevent exact metric tracing or proof of fully deployed wings.

Rebuilt two independent editable wing meshes: 2.2 m nominal span, low sweep, slimmer chord and restrained thickness. Root leading station now Y +0.30 m, chord approximately 0.35 m; these local dimensions are C. Fairings and rounded root covers moved to accompany the wings, preserving connected embedded interfaces. Body/nose, top loop and tail geometry retained from G v002. No mechanism, stowed transition, internal system or physical rack created.

## Actual images and validation

Ten new renders generated from fresh-opened G v003 and visually inspected:

- [Perspective](../Previews/Banderol_G_v003_Hero.png)
- [Front](../Previews/Banderol_G_v003_Front.png), [Rear](../Previews/Banderol_G_v003_Rear.png)
- [Left](../Previews/Banderol_G_v003_Left.png), [Right](../Previews/Banderol_G_v003_Right.png)
- [Top](../Previews/Banderol_G_v003_Top.png), [Underside](../Previews/Banderol_G_v003_Underside.png)
- [Nose](../Previews/Banderol_G_v003_Nose.png), [Rear detail](../Previews/Banderol_G_v003_Rear_Close.png)
- [Clay](../Previews/Banderol_G_v003_Clay.png)

Master and preserved checkpoint reopened in separate fresh Blender processes. 29 base meshes: zero nonmanifold edges, zero degenerate faces, positive volume. Seven wing/fairing/tail roots show intended casing contact, not welded skin or engineering verification. Five editable curves retained outside those mesh checks. No external file-image material dependencies. Original three mod asset hashes unchanged. Actual geometry length/width/span measured, not inferred from root metadata.

Reports: `G_validation_v003.json`, `G_renders_v003.json`, `G_parameters_v003.json` and `Support/review_G_v003.log`. Engine, exports, carriage clearance, stowed poses and relocated-package tests NOT ATTEMPTED. Review this revision before advancing. Blender scale is established; complete real-world dimensional accuracy remains evidence-limited.

