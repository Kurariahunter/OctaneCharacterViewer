# Hand palette and fresh mesh checks — 2026-10-20

`compare_hand_relative_palette.py` compares captured first/second index and middle joint skin transforms against the viewer palette after expressing each relative to its Hand transform. This removes parent placement and the surrounding arm animation. File-derived skin associations identify eight bones across both hands.

There are 146 observations from the 73 native world chains. The maximum best-sample matrix difference is 7.091e-6; even the maximum across all 19 viewer samples is only 7.205e-6. This shows close agreement for these eight hand-relative transforms, not an exact synchronized actor/phase comparison. These are transforms at captured matrix boundaries, not observed renderer palette reads. The thumb is excluded.

For an independent mesh check, QuickBMS extracted only `fro_elsa/fro_elsa_0.vbuf` from the installed PC game's `assets/characters/fro_elsa/fro_elsa.zip` into `InstalledGameAssetCheck/FreshWeightAudit`. SHA-256 is `1c5216b91aa8e8085e2e4eb7f2f2c711f00ee4e65a678139498e8ccddf2176b6`.

`audit_fresh_vbuf_weights.py` freshly decodes each OCT primitive's 24-byte skin stream, with direct palette indices (this asset has no influence remap). All **5419** vertices' indices and float32-normalized weights match the viewer data exactly, including stable ordering of combined weights. Fresh 16-byte position streams, after the importer's X reflection, match up to common Y grounding offset -0.0006480248; maximum residual is 8.63e-8. The common offset is an existing import convention, not evidence for an isolated finger correction.

No substantial mapping, weight or geometry discrepancy was found. These results do not resolve the reported visible hand issue and do not justify manual corrections. Remaining useful targets are the thumb's world/palette path and a same-pose close-up from the game showing the specific difference. Actor identity and actual renderer palette consumption also remain unproven. Do not continue changing already matching index/middle operators without new contradictory evidence.

Reports: `ControllerState/hand-relative-palette-comparison.json` and `ControllerState/fresh-vbuf-weight-audit.json`. No viewer pose changes in this step.
