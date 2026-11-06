# PC local/world dress Transform capture validated

2026-10-17. Capture: octane_20261017_184512_1792277112145413500.json.

## Live discovery

The corrected0x1Cminimum array-table offset admits4unique complete local/world paths, with no discovery boundaries. All4chains have240downstream samples and0field errors. Only the previously connected updating chains0x1e07fdd0and0x1e07fe74are used for the numeric comparison. Their completed-frame counts are193left/197right,390total;90snapshots are excluded by stamp criteria.291accepted snapshots also match the separately captured dynamics read-window frame pair. Observations can repeat game frames and are not390independent integration updates.

## Native comparison

`validate_pc_local_dress_transform.py` now accepts explicit --capture/--output-dir, checks capture executable identity, and writes per-sample predictions. The same original native inverse-point and compose path from the earlier local comparison matches all390localTransform payloads exactly.

Original native ConcatenateChainTransform0x57e240then combines predicted local with captured anchor. All quaternion, position, uniform scale, Scale.xyz and Unscale components match. The sole raw difference in every accepted snapshot is index11, Scale.w: predicted1.0versus observed0.9997882843017578. Maximum raw component difference0.0002117156982421875is retained in the report; raw concatenation alone is not reported as byte-for-byte equality.

Disassembly supplies the explanation without a fitted correction: native point routine0x4c4350loads the uniform float atTransform+0x1Cat0x4c435Band writes it toScale.wat+0x2Cat0x4c435E, before multiplying the point. Thus consuming a Transform materializes this repeated scale value. The native point adapter now optionally returns its post-call Transform payload while retaining the existing point-only default API. No field is manually copied in the validation.

After this original native point call, every one of the390predictedworldTransform payloads matches the live payload exactly numerically. Independently, transformed origin,3unit-axis points and1mixed-axis point match live-world point results exactly:1950point comparisons, maximum coordinate error0.0. This demonstrates the observed raw cache-field difference does not change these transform results. It does not establish which particular game consumer populatedScale.win each live snapshot; the identified native routine is one proven producer of the observed state.

## Limits

Captured quaternion, anchor/root and external scene state remain inputs. The earlier closed particle/Aim feedback test is separate evidence. This pass verifies local/world propagation, not a new fully closed whole-actor graph. Captures remain non-atomic despite unchanged/completed stamps. Accepted snapshots may repeat frames. The final live Matrix4x4variant nodes and actual renderer palette consumption have not been captured or compared. This is not a universal animation reader.

## Artifacts and next step

- WorldDress184512/pc-local-dress-transform-validation.json: hashes, per-sample local/raw/materialized world predictions and five-point errors.
- validate_pc_local_dress_transform.py: CLI supports new captures without overwriting older result folders.
- native_pc_transform_scale.py: optional point(return_state=True), original point-only API unchanged.

Next: discover and capture the final Transform-to-Matrix variant output on these verified world nodes, with exact producer/output aliases and frame checks. Compare native world-to-matrix and correct PC skin association/palette binding. No new Unity preview was generated or modified in this validation pass.
