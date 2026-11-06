# Elsa head/neck Unity diagnostic

## What this test represents
A small bind-relative animation test built from Elsa's archived active/passive idle curves. Original curve and convention-2 quaternion routines were sampled in isolated emulation. Two offset multiplication orders are retained, so four diagnostic variants are built: active/right, active/left, passive/right, passive/left. Neither order is declared original-engine-correct.

The graph evaluator supports only the head/neck dependency subset and held-static torso defaults. Unsupported operations fail. Nonzero Euler variant evaluation is deliberately rejected. Evaluated default Head and Neck outputs match the stored graph matrices within 1.65e-7, but those stored transforms differ from the skin bind matrices. To avoid applying that mismatched rest pose directly, the preview uses: skin bind local * inverse(graph default local) * animated graph local. This is an explicit retargeting hypothesis, not a recovered complete animation pipeline.

Missing facial and accessory skin parents are listed as preview approximations; original world bind matrices and skin palettes are preserved. The historical mesh has 24-byte position/normal/index/weight records, a separate 16-byte normal/tangent stream, main-stream UVs at byte 12, and element-based index offsets. UV/color-pair assignments require visual review.

## Review
Use the comparison prefab or the four generated prefabs in Assets/ElsaHeadResearch. Press Play to inspect motion. The body remains static; facial animation, root motion, original layering and the rest of the skeleton animation are not reproduced. Fourteen position/rotation curves animate Head and Neck only. Each variant uses 61 samples per control and linear interpolation; finer sampling may be needed later.

The menu Tools > DI3 Static Converter > Research > Create Elsa Head-Neck Diagnostic creates a new output folder each time. It uses only the bundled research inputs. Existing model imports and prefabs are not overwritten.

Validation results and the exact generated folder are recorded separately after Unity completes its checks. A passing test establishes consistent sampled transforms, finite skin deformation and Animator playback; it does not establish fidelity to the original game.

## Installed result
Ready-made comparison: Assets/ElsaHeadResearch/ElsaHeadNeckPreview/Elsa_Comparison.prefab. Drag into an empty test scene and press Play. Source/header data and textures are supplied, so no manual Elsa extraction is needed. This is an Editor research preview; it has not been validated as a game-build asset.

Validation used Unity 6000.5.8f1 in the isolated test project. Four saved Animator prefabs passed. Maximum skin bind reconstruction error: 2.58e-7; maximum sampled local matrix error: 1.79e-7. Other bone locals stayed unchanged; baked vertices remained finite. Screenshot visually checked. Installed model materials were adapted to the existing URP/Lit shader; live-project URP rendering has not been separately exercised.

## Later result: native offset order
The original UnitRotor3d OffsetPolicy now selects RIGHT (103 direct native tests; 101 discriminating). Earlier statements above treating both orders as unverified are superseded for this processor. Bind-relative retargeting remains experimental. Use Assets/ElsaHeadResearch/ElsaNativeOrderPreview for the two preferred diagnostic prefabs.
