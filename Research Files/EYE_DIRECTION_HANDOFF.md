# PC Elsa native eye direction — 2026-10-22

Update: FOREARM_OVERLAY_HANDOFF.md records the opt-in source paths for the last two palette fallback bones. The eye-only artifact below remains preserved.

Open evaluated animation:

`F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-eye-paths.json`

This opt-in IdleC artifact includes the eight brow/jaw/lip outputs, four lids and two eyes. It evaluates60 of62 palette bones from source paths; Forearm_OL_Right and Forearm_OL_Left still inherit bind offsets from their elbows. This is not complete engine/game parity. Defaults and previous artifacts are unchanged.

## Native operation

PC registration0x501A43 binds ProcessorNode::TransformVectorWithDilation to factory0x4D3700. It calls0x4C36E0, constructor0x4B6B50 assigns vtable0x1B2C3B4, and execute slot+0x40 resolves to0x4D3A50. Execute calls math0x4C37D0. Disassembly is saved in ControllerState/eye-vector-disassembly.txt.

The original PC execute routine runs offline through native_pc_eye_vector.py, with explicit Vector and Dilation runtime type predicates. Tests compare100 seeded random unit rotations, signed uniform scales including zero, and vectors against rotation-matrix algebra. Maximum component error1.0063284010541906e-6. Changing converter translation has exactly zero effect. Vector direction is rotated and scaled, not translated.

Graph processors500 and509 use Vector inputs798/812 and shared Dilation converter268 to produce799/813. The bounded evaluator now executes this native operation and existing downstream graph operations for eyeLeft/eyeRight. Matrix-to-Dilation conversion follows the existing positive-scale graph convention; signed-scale synthetic coverage of the native operation does not establish signed-scale graph reconstruction. No eye position or empirical pose offsets were added.

## Validation and limits

Eighteen finite-matrix smoke checks pass across start/middle/end of specific01,02,03. Those are not continuous game-parity checks. The full specific03 bake has303 simulation frames and152 samples, and passes existing native palette/dress checks with the same limits as the previous eyelid bake.

Comparison with native-idleC-eyelid-paths.json changes exactly eyeLeft and eyeRight in152 samples. All other matrices are identical. Maximum matrix-component difference0.21640099957585335 is neither an angular error nor a live-game error measurement.

The user's visual approval applied to the preceding eyelid preview. The new eye-direction preview still needs visual confirmation. Native operation tests, source graph evaluation and visual parity are distinct evidence.

Reproduce: use the EYELID_GRAPH_HANDOFF.md bake command, change output to the path above and append `--native-eye-paths`. Tests: ElsaSceneResearch/test_pc_eye_vector.py and OctaneCharacterViewer/compare_eye_paths.py. Reports: ControllerState/eye-vector-validation.json, ControllerState/eye-graph-smoke-validation.json, NativePreviews/eye-paths-comparison.json.

Next: visually inspect eye direction together with eyelids, then investigate the remaining forearm overlay paths or extend native idle evaluation to further motions. Automatic state scheduling/default policies and the running finger issue remain separate work.
