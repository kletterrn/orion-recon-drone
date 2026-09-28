# Existing-source reuse inventory

Existing files are preserved; hashes are in source_manifest.json. No old mesh
has been appended to the new master at the A/B checkpoint.

| Existing area | Decision | Required comparison before reuse |
|---|---|---|
| Orion fuselage and white nose | Reconstruct | Old exhibition proportions do not govern R3 |
| Old optical turret | Reconstruct | R3 multi-window housing and mount must be traced from photos |
| Old shallow bay recess boxes | Reject | They are not real enclosed gear-bay cavities |
| Old wheel/hub/strut components | Candidate, not accepted | Tire profile, hub recesses, fork and proportions against R3 and compatible P4 |
| Fastener instances and curve hoses | Candidate, not accepted | Positions/types only where visible; no arbitrary complexity |
| Existing wing and tail construction helpers | Technique only | Rebuild profile, transitions and supported divisions against compatible views |
| Existing materials | Starting shader concepts only | R3 neutral grey/white, rubber and optics review |
| Existing inspection cameras | Reference for useful view categories | New camera framing and R3 matching required |
| Exhibition wordmark, airframe numbers, prototype equipment | Exclude | Not justified by selected R3 configuration |
| Existing missile primitive mesh | Reject as authoritative | Approximately 0.46 m body diameter and generic shapes conflict with brief |
| Existing game export script | Convention reference only | Fresh basis, bind-pose and isolated import validation required |

Reference fidelity takes precedence over preserving old geometry. No gameplay
files, materials used by the existing addon, or resource GUIDs are changed.
