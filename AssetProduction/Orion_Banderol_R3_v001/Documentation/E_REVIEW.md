Current camera correction: see SENSOR_REVIEW.md and Orion_E_sensor_fix_v007.blend. Views below show the earlier E v005 turret.

# Stage E v005 — exterior and presentation rig review

The approved nose/body/wing roots are preserved. Added dorsal fairings, left forward panel outline/fasteners, triangular vent, shallow rear intake, two forward underside apertures, tip-light housings, tip projections and propeller tip paint. Exact dimensions and hidden completion are restrained approximations.

Master: [Orion_Master.blend](../Orion/Orion_Master.blend). Numbered source: [Orion_E_exterior_rig_v005.blend](../Orion/checkpoints/Orion_E_exterior_rig_v005.blend).

## Actual rendered inspection views

These nine images were rendered from saved E v005 and visually inspected. No generated reference replacement or retouching was used.

| View | Purpose |
|---|---|
| [Whole aircraft](../Previews/E_v005_Hero.png) | Rest silhouette and exterior placement |
| [Forward exterior](../Previews/E_v005_Forward_Exterior.png) | White nose, forward panel, sensor and gear |
| [Dorsal/panel](../Previews/E_v005_Dorsal_Panel.png) | Fairing base, continuous projected seal, vent |
| [Rear/propeller](../Previews/E_v005_Rear_Propeller.png) | Two blades, tip paint, spinner and paired tail |
| [Rear intake](../Previews/E_v005_Rear_Intake.png) | Shallow opening/backing, no invented machinery |
| [Left tip](../Previews/E_v005_Left_Tip.png) | Separate housing and lens |
| [Presentation pose](../Previews/E_v005_Rig_Pose.png) | Control surfaces, propeller and sensor posed together |
| [Neutral clay](../Previews/E_v005_Clay_Hero.png) | Geometry without material differences |
| [Forward underside](../Previews/E_v005_Underside_Apertures.png) | Recessed apertures distinct from turret |

Use `ORION_ROOT` Object Properties > Custom Properties for angle controls. Reset all angles to zero before comparison. Gear timeline: 1 down, 120 illustrative retracted, 160 inspection. The skeleton follows these pivots; source rigid weighting and engine clips are deferred to game copies. See `ASSET_README.md` for operation.

## Performed checks and limits

Fresh master/checkpoint opens succeeded; relocated paths resolved. Prior vertex arrays match D v012. Source and selected evaluated Boolean meshes passed closedness, volume and degenerate checks. Every driven control moved in sampled angles. Sampled control-surface, propeller and sensor contacts against selected obstacles were zero; all 160 gear frames had zero contacts against new exterior meshes. Bone matrices matched control targets at rest and in an additional propeller/sensor pose. These digital checks cover listed samples, not arbitrary combined-pose clearance or real-world specifications.

UVs, finished textures, verified markings, LODs, collision proxies, exports and Workbench tests remain incomplete. Evidence limits tiny/hidden details. This checkpoint is ready for visual review, not completed Reforger integration.

Next after acceptance: Stage F Banderol reference lock and primary form. Its evidence-limited reconstruction status and unresolved rack/configuration remain explicit.
