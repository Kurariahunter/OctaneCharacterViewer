# Live PC dress matrix outputs match native conversion

2026-10-17. Capture: octane_20261017_190233_1792278153395797300.json.

## Discovery and accepted evidence

The bounded consumer scan completed with4verifiedlocal/world/matrixpaths, no discovery boundaries, and0downstream field errors across all4x240samples. Matrix converters consume the exact verified worldTransform outputs and their output node producer aliases point back to the converters. The output payloads are12floats atnode+0x40, as established from the installed executable.

Only the previously connected updating chains0x1e07fdd0and0x1e07fe74are used for numeric comparison.183left+193right=376completed-frame snapshots pass;104fail the completed-frame condition and are excluded by timing criteria. Accepted evidence represents360distinct chain/frame pairs, not376independent simulation updates.238accepted snapshots also match their separately captured dynamics read-window stamp pair. The other two discovered paths are inactive/template-shaped and are not pooled into the result.

## Results

validate_pc_local_dress_transform.pywith this explicit capture/output directory reports:

- Native inverse-root-to-anchor translation and local compose: maximum component error0.0.
- Native world concatenation: the same sole rawScale.wcache difference as before, maximum0.0002117156982421875. Retained in report.
- Original native point consumer materialization of uniform intoScale.w: maximum full worldpayload error0.0.
- Native world point comparisons:1880points, maximum coordinate error0.0.
- Native TransformToMatrixconverter0x55da50from predicted worldTransform:376of376matrixoutputs match exactly numerically; maximum component error0.0.
- Separate native matrix conversion from capturedworldTransform: maximum component error0.0.

Thus the rawScale.wcache difference does not affect the matrix output here. All4512compared matrixfloat components agree numerically. This is not a claim of bitwise signed-zero identity.

The report retains capture SHA256, executable SHA256, per-sample local/world/matrix predictions, raw versus materializedworld errors, frame IDs and matrix errors. The validator's mismatch exit checks passed.

## Provenance and scope

The previous source audit pins the correctPCmodel SHA25638ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d. SkinInfluence associations link world699->matrix698to dressLeftStart andworld715->matrix714to dressRightStart. Native type registration/factory/constructor tracing establishes that0x55da50is the original TransformToMatrix4x4VariantProcessor, not a guessed matrix formula.

This comparison uses captured root, anchor and local quaternion to isolate transform/matrix propagation. The earlier carried particle/Aim feedback replay remains separate evidence; this is not one long fully autonomous whole-actor animation run. Frames are read non-atomically and may still contain races despite unchanged/completed stamps. Discovering converter output aliases plus source skin associations does not independently capture the actual renderer palette upload/consumption. It is now valid to claim live matrix-converter equality on this accepted dataset, not universal animation decoding or renderer parity for every character.

## Files and next practical step

- MatrixDress190233/pc-local-dress-transform-validation.json.
- validate_pc_local_dress_transform.py.
- native_pc_skin_matrix.py.
- pc-dress-matrix-source-audit.json.

Reproduce from F:/DisneyInfinityPortalTest:

    python ElsaSceneResearch/validate_pc_local_dress_transform.py --capture OctaneLiveInspector/Captures/octane_20261017_190233_1792278153395797300.json --output-dir ElsaSceneResearch/MatrixDress190233

No Unity assets changed. The practical next step is use this verified native packed-matrix conversion in the existing file-driven PC exporter, compare it against the existing point-derived skin world matrices/inverse binds, and produce a separate reviewable Unity clip/preview. That advances file-to-Unity reproducibility without requiring another identical capture. Original clip/control coverage, actor layer blending and cross-character validation remain separate tasks.
