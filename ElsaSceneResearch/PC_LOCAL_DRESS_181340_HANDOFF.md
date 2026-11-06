# PC local dress Transform matches live capture

2026-10-17. Capture: octane_20261017_181340_1792275220781381600.json.

## Local transform evidence

All4local paths were captured for240samples each without per-sample errors. Previously connected updating dress chains0x1e07fdd0and0x1e07fe74provide195left/198right completed-frame samples,393total.87snapshots fail the completed-frame condition and are excluded by stamp criteria, not output error.305of the393also match the separately captured dynamics frame stamp pair.

`validate_pc_local_dress_transform.py` applies original native inverse-point to the captured root particle position and anchor Transform, then original native compose with that computed local translation, captured local quaternion and source stored unit Scale4/Unscale4. Captured components do not supply the primary predicted translation or fit aggregate values. The source local compose has no scale/unscale component inputs, which is checked in the live records.

All393local Transform payloads match exactly numerically: maximum inverse-root translation error0.0, maximum aggregate component error0.0. A separate compose using captured component translation also matches0.0. Payloads retain quaternion/translation/uniform/Scale4/Unscale4 semantics; they are not flat matrices.

This isolates root-to-local translation and Transform composition. It uses the captured quaternion; previous separate particle/Aim closed-loop validation remains distinct. Read-window equality is not atomicity, and duplicate observed frames are counted as snapshots rather than independent updates. No world-transform or final skin-matrix equality is claimed.

Results: LocalDress181340/pc-local-dress-transform-validation.json. Source/capture hashes and per-sample predictions are retained. Canonical files are in F:/DisneyInfinityPortalTest/ElsaSceneResearch and mirrored into the Unity research notes.

## Why world discovery failed, and correction

All67recognized world-concatenation candidates were rejected by the tool's minimum table-offset check. Retained examples show offset0x1C, input count2, output count1. The native instruction at0x57e252reads the unsigned16-bit offset from processor+0x18, then uses processor+offset as the pointer table. There is no native0x20minimum; a compact table can start immediately after the4-byte layout header at0x1C.

The Python discovery incorrectly required>=0x20. It now permits>=0x1Cfor this exact known world-chain layout, while retaining the upper bound,2/1dimension checks, execute validation and output producer alias. Diagnostic table reading uses the same corrected lower bound. Synthetic tests now accept the compact0x1Ctable and reject an overlapping0x18table, in addition to existing path/stamp/error checks.

Two retained inactive-chain rejected headers contain precisely the expected local/anchor input pairs and corresponding output references. This supports the diagnosed offset issue but does not validate their output aliases or prove live active world paths: those payloads/aliases were not recorded by the rejected branch. Active-world examples are outside the first64retained rejected examples. We will still require full link checks on the next scan.

## Next capture

Run the same OctaneLiveInspector/Capture Dress Skin Transforms.cmd with Elsa active. The corrected offset check should allow discovery of these compact world chains; this remains pending live verification. Local-only fallback and diagnostics remain enabled if any other boundary appears. Next compare captured world Transform against native concatenation of predicted local Transform and captured anchor. Final Matrix4x4nodes remain outside this capture increment.
