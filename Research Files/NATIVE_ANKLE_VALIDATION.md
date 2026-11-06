# Native ankle validation — 2026-10-22

The exact-target test had rejected turn90r and walklb. Independent forward kinematics using the original PC executable's solver quaternion outputs and native compose/concatenate/point routines reproduces the residual. This is a validation correction, not an animation or pose correction.

For every sampled simulation frame with unit solver stretch and a rigid root, compare the evaluated ankle to this independent native endpoint at the existing 1e-5 threshold. Also verify both paths agree on the target coordinate. Preserve target distances separately as max_endpoint_error and per-frame target_residual. They are not decoder-error measurements. Nonunit solver stretch keeps the original target check; nonrigid roots fail the independent witness rather than silently proceeding.

* turn90r: 37 frames, 62/62 bones; largest target residual 1.28746575562e-05; largest native-output discrepancy 4.27440324486e-07.
* walklb: 49 frames, 62/62 bones; largest target residual 1.26096496521e-05; largest native-output discrepancy 5.75575318385e-07.

Both complete bakes pass matrix, shear, dress and full-palette checks. The regression reproduces the failing turn frame, checks both ankles against native FK, demonstrates a deliberately displaced ankle exceeds tolerance and rejects a nonrigid root. The evaluator's hard failure compares against the native witness. No vertex, bone angle, animation curve or tolerance was adjusted.

Restart Launch_Viewer.cmd. Turns now contains all six 45/90/180 left/right source motions. Backward walks now contains backward, backward-right and backward-left. The separate bin/AnkleValidationPreview build passes with zero warnings/errors; the hidden combined pack/import/skinning smoke test exits 0, loading six turns and three walks with 62 source bones and no fallback.

These are bounded PC Elsa source previews. Numerical agreement does not establish full in-game controller, collision, actor-yaw or visual parity. Finger research remains parked.
