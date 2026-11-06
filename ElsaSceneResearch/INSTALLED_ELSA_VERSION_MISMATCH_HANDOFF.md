# Critical asset-version mismatch discovered from live thigh producer

2026-10-17. Live capture octane_20261017_003725_1792211845547151800.json.

## Verified connected producer

The known updating skirt/thigh path validates quaternion copy0x4c83f0 outputs0x1e0732bc/0x1e0734a4 and inputs0x1e06f740/0x1e06ec84. Those input nodes point to producers0x1e07e434/0x1e07e324, vtable live0x2515744(static0x1b35744), execute0x5382f0. Captured descriptors declare8inputs/3outputs.

Static vtable slot2points0x54ad30 returning literal0x1b357b8 = IkLean2LinkProcessor. Slot16points0x5382f0. Constructor0x54ad00 callsbase0x54ac80 then setsvtable0x1b35744 and type metadata0x21bd5dc. Thus the connected live processor is IkLean2LinkProcessor, not the13input/4output0x53b620IK2BRP fixture. Previous broad scan found a different valid IK family; that replay remains valid but did not identify this producer.

## Installed versus downloaded model

Read-only extraction with existing QuickBMS/script into InstalledGameAssetCheck (no installed game files modified):

|Asset|Downloaded research copy|Installed game copy|
|---|---|---|
|fro_elsa.oct bytes|163438|154648|
|SHA256|126ec007bafe36a24799b30e56f57e4d58da15698607dcfc06097c580928f4d2|38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d|
|Leg solver declaration|IK2BRPLengthSquashZConstraint|IkLean2LinkProcessor|
|BENT bytes|41522|65571|
|BENT records|1890|2401|

Installed OCT declares IkLean2LinkProcessor nodes405/411. All6Elsa idle ClipDataBlock payloads differ from downloaded counterparts, not merely OCT wrapper bytes. Active duration remains4.199999809seconds and passive6.166666508seconds, so matching filenames/durations were insufficient to establish asset identity. Installed archive also includes shared biped/class_girl motion dependencies absent from the supplied research ZIP.

The downloaded archive's original platform/build provenance has NOT been established. Do not label it a particular console/version based on this mismatch alone. A version/asset-family mismatch is confirmed, but it is NOT yet proof of the cause of the active skirt bulge in the older asset's own valid pipeline.

## Consequences

Preserve earlier previews and bounded validations as evidence for the downloaded asset family. They do not establish that the installed PC game's full pose must match. The observed passive upper-dress resemblance remains a numerical comparison, not proof the assets were identical. Native lower-dress Aim and particle parameter matches can be reused only with explicit per-asset checks. Old port/node indices must not be applied blindly to the installed graph or clips.

Next: decode the installed graph's ports and actual8input/3output IkLean2LinkProcessor path, then validate against connected live objects. We have sufficient offline assets to start that step. No further identical neutral-stance capture is currently required. The existing inspector has NOT yet been changed to decode this new solver's semantics.

## Files

InstalledGameAssetCheck/fro_elsa/fro_elsa.oct
InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/... (47idle OCTs, including6Elsa-specific)
InstalledGameAssetCheck/Bent/fro_elsa/fro_elsa.bent
installed-elsa-model-graph.json;installed-elsa-bent-decoded.json
installed-elsa-asset-comparison.json;installed-elsa-idle-comparison.json;installed-idle-payload-comparison.json
Scripts compare_installed_elsa_graph.py,compare_installed_motion_payloads.py,compare_installed_idle_versions.py,verify_connected_ik_type.py.

No production importer, mesh, weights or Unity preview replaced. Installed assets and downloaded source archive remain read-only originals.
