# Camera/turret correction — E sensor v007

This checkpoint addresses the user's supplied close-up, registered as R11. It supersedes the E v005 turret; the approved aircraft nose/body/wing-root meshes remain unchanged. Master: `../Orion/Orion_Master.blend`. Numbered editable source: `../Orion/checkpoints/Orion_E_sensor_fix_v007.blend`.

## What changed

The old narrow mounting post and separate rectangular side bars were replaced by a broad underside saddle fitted directly to the fuselage, a short collar and a connected upper bridge. The turret sits 0.12 m closer to the body. The casing uses editable shaped stations and subdivision: narrow crown, full cheeks and rounded lower belly. Side cheeks now have a curved lower contour. Seven optical ports are individually recessed along the curved casing normals, with separate rims, glass and backing. There is no flat plate covered in painted circles.

The new supplied image supports the mounting relationship, curved side housing, rounded lower casing and aperture arrangement. R3 remains the selected aircraft appearance; R11 exhibition lettering, straps, cables and ground restraints are not carried into the aircraft. Metric depths, hidden surfaces and exact optical sizes remain visual estimates. No sensor capabilities are inferred.

## Actual model renders

- [Reference-side oblique](../Previews/Sensor_v007_Photo_Angle.png)
- [Front ports](../Previews/Sensor_v007_Front.png)
- [Side housing](../Previews/Sensor_v007_Side.png)
- [Body connection](../Previews/Sensor_v007_Connection.png)

These are neutral Cycles renders of the saved model. The oblique camera illustrates the same visible side but is not a calibrated photographic match. Both masters and checkpoints remain editable, with prior revisions retained.

## Controls and limitations

Select `ORION_ROOT`: yaw remains +/-35 degrees; pitch is now limited to +/-10 degrees in both the property interface and driver. The prior +/-15 setting caused internal mounting interference; the tested +/-10 range avoids that. These are visual limits, not real sensor specifications. Yaw/pitch pivots and corresponding preview-bone rest locations were raised with the housing. Source meshes remain object-parented; game weighting/export validation remain later work.

The mount and collar intentionally enter the aircraft attachment region; this makes a continuous visual connection. Such attachment contacts are recorded separately from unwanted camera/gear collisions. Hidden mount surfaces are conservative completion, not engineering interfaces.

See `SENSOR_validation_v007.json`, `SENSOR_final_validation_v007.json` and `SENSOR_joint_validation_v007.json` for performed checks. Earlier sensor v001-v006 are diagnostic checkpoints, not the accepted final revision. Finished textures/UVs and engine tests remain pending. This correction awaits user visual review before proceeding.
