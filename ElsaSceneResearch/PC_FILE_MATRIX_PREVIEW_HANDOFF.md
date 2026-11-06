# File-driven PC native-matrix Unity preview delivered

2026-10-17. This is a separate preview using original PC idle files. It is not a live-capture animation recording or universal character importer.

## Open in Unity

Scene: C:/Users/Kurar/Disney Reloaded/Assets/DI3PCMatrixDressPreview/Generated/Elsa_PC_MatrixDress_Preview.unity.

Left is activeidle, right is passiveidle. Play once; each clip holds its final pose when finished. Stop/play restarts. Active duration4.199999809seconds, passive6.166666508seconds. Clips have127/186poses at30Hz. Existing previews and original rig/mesh/materials were preserved.

The delivered folder also contains two AnimationClips, AnimatorControllers, individual preview prefabs, comparison prefab, README and a C#Editorbuilder with its poseJSON. The builder menu is Tools/DI3 Static Converter/Research/Create PC Elsa Matrix Dress Preview. The existing Generatedfolder is deliberately protected against silent rebuilding. Keep or move it explicitly before a rebuild.

## File-to-matrix path

bake_pc_matrix_dress.pyreads the same correct hash-pinned PCmodel and original active/passive idleOCT payloads as the gravity preview. Source controls drive the existing verified graph, native8/3IK, scale compensation and native particle/Aim feedback. Native skin-world Transform outputs now pass through original TransformToMatrixconverter0x55da50. Its packed12float output is expanded using the orientation/layout verified against native points and live converter data, then reflected into the existing Unity basis.

27sourceTransformpaths use the new converter.4sourceDilationpaths retain their existing evaluator, for31source-driven bones total. The remaining31weighted palette bones inherit their explicit bind offsets. No new facial/finger decoding or actor-layer blending was added. The62weighted bones remain an independent preview palette to preserve native world transforms without Unity parent-scale multiplication; this is not a Humanoid/retargetable gameplay rig.

Native dress still uses measured gravity[0,-9.8100004196167,0],60Hzsimulation,30Hzexport,120initial-pose warmup ticks perclip, correct authored particle configuration and no capsule scene. Timing/warmup are explicit synthetic preview choices, not a recreation of the captured moving performance. Initial state, collisions elsewhere, full actor update order and seamless looping remain outside scope.

## Verification

- 16848native packed-matrix versus native point-derived affine comparisons pass; max component error2.775341272354126e-07.
- 1248ankle checks pass; maximum endpoint error5.729481366449266e-07.
- 1248timeline dress checks pass; rooterror0, maximum segment-length error6.863347462582325e-08. Warmup checks also pass.
- All62palette matrices remain finite and TRS-representable; maximum orthogonality residual1.4679059115038418e-06.
- 19406exported palette matrices compared with earlier gravity preview; maximum difference2.4355695849020975e-07. Expected visual parity: this advances converter provenance, not animation coverage.
- IsolatedUnitybuildpasses. Clips have620bindings each, reconstruct source samples within6.03497e-07active/1.046807e-06passive, retain finite skinned vertices, and savedAnimators show head and knee motion.
- Sixposed stills rendered with temporaryCPUskinning/materials for isolated-project visual inspection. Checked poses show no obvious earlier shin-through-hem gap. Passive skirt remains broad, consistent with the earlier preview; no vertex/weight edits were used.
- Fresh scene saved with original material references. Temporary renderer helper/materials were not delivered.13referenceGUIDs checked with no missing references.

The assets were built and rendered in the isolated validation project, then copied as a new folder into the user's project with metadata intact. Production Unity itself was not launched or its current scene changed.

## Artifacts

Canonical research: F:/DisneyInfinityPortalTest/ElsaSceneResearch.

- bake_pc_matrix_dress.py/native_pc_skin_matrix.py/native_pc_transform_scale.py.
- pc-matrix-dress-animation.json/pc-matrix-dress-validation.json.
- pc-matrix-vs-point-preview-comparison.json.
- pc-matrix-dress-unity.log/pc-matrix-dress-render.log.
- pc-matrix-dress-delivery-validation.json.
- pc-matrix-dress-preview-0.png through5.png.

Research and reports are mirrored under C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DressResearch.

## Next useful step

Review the delivered scene inUnity. This now provides a reproducible original-file-controls-to-Unityclip path for the tested PCidles with live-verified Transformmatrix conversion. Next expand original clip/control coverage or test a second PCcharacter using explicit source signatures and graph mapping. Do not present it as a generic all-character animation reader or assume unknown graph operators will decode automatically.
