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
# S8000 Banderol — Stage F v002

Open `S8000_Banderol_Master.blend` independently in Blender 5.2.2. Authoritative editable source; preserved numbered checkpoint `checkpoints/S8000_Banderol_F_primary_v002.blend`.

See [review and evidence limits](../Documentation/F_REVIEW.md) before adopting this reconstruction. Nominal 5 m length / 0.30 m body width; candidate 2.20 m wing span remains provisional. Illustration-supported exterior, not measured blueprint accuracy.

Metres; +Y forward, +X right, +Z up. Root `BANDEROL_ROOT`; `BANDEROL_ATTACH_ROOT` is a scene helper only, unplaced on Orion. Eleven separate editable source meshes and procedural review materials; no linked libraries or external texture dependencies. No weapon internals, functional deployment or release engineering.

Empty export/texture directories reserve later stages. No UV, game rig, LOD, collider or engine validation yet. Support construction was executed and the saved models reopened and rendered; scripts are supplementary to the actual blend assets.



