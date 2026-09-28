# Orion-E reference exterior — work in progress

This is a separate editable Blender exterior study based chiefly on the supplied ARMY-2022 front-right photograph. It does not replace `ORD_Orion_Recon.blend`, the current FBX/XOB, or the mod prefab.

## Files

- `OrionE_reference_source.blend`: organized source collections and PBR node materials.
- `OrionE_reference_clean.fbx` and `.glb`: selected mesh objects, with moving parts separate.
- `inspect_{front,side,rear,top,three_quarter}.png`: visual inspection renders.
- `Tools/build_orion_e_reference.py` at the repository root: reproducible generator.

## Conventions and observations

Blender uses X right, Y forward, Z up, metres. The existing mod uses Enfusion X right, Y up, Z forward and records an 8 m length and 16 m span. The FBX exporter requests `-Z` forward and `Y` up; the actual import orientation still needs confirmation in Enfusion Workbench. The source is in a gear-down clean reconnaissance configuration, without stores or markings.

The white nose, slim fuselage, nearly straight wings, upright V-tail, underside optical turret, two-blade stationary pusher, and tricycle gear are modeled as individually editable objects. Ailerons and ruddervators have hinge origins; the propeller blades have hub origins. Landing-gear pieces remain separate.

## Approximation and remaining work

The photographs do not establish exact airfoil sections, internal gear mechanics, hidden underside panels, antenna shapes, or sensor internals. These are restrained approximations. The nose/fuselage join, gear doors, wing-root fairings, V-tail sections, prop blade section, and sensor window placement need closer photographic measurement and cleanup. Some intersecting visual components were used for the study; topology and export normals have not undergone a full game-asset audit. UVs are automatic starter UVs. The material colors and roughness are node based; 4096 px authored PBR maps, detailed weathering, LODs, collision geometry, animation rig, damage setup, and in-engine import checks remain outstanding. This asset is **not game-ready**.
