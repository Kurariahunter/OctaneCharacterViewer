# Sideways-right run preview — 2026-10-20

Added pinned PC `grl_bm_runr.oct`, using the serialized WALKRUN `Run Right` group: shared upper-body source at **0.85** and `human_bm_runr_lean_add`. The existing group-aware evaluator and native buffer blend are reused. Startup cache now contains forward, diagonal-right and sideways-right run clips; select **grl_bm_runr_NativePreview**.

Two pipeline gaps were exposed and resolved:

1. Right lower-dress control node 650 uses a component X-scale opcode (6) instead of a full scale vector. Leaf application now supports individual XYZ scale components only on the already validated Transform controls 644/650, preserving other components and existing guards.
2. Composition buffers were zero-initialized. Sideways lean-only rotation produced NaNs when combined against a zero quaternion. Existing live captures show **7405 repeated zero-mask destination-row observations**, all with unit four-component scale and an identity quaternion. The helper now initializes destination and source rows to that native neutral pattern and rejects nonfinite composed rows. A regression case covers lean-only quaternion composition.

Sideways bake passes: 37 frames, 19 samples, 46 source-driven and 16 fallback palette bones; endpoint error 3.65e-6, native matrix/point error 2.38e-7, TRS shear 1.55e-7. Forward and diagonal clips were rebaked with neutral initialization and also pass. No manual pose offsets were introduced.

Release build in `bin/CurrentPreview` passes with zero warnings/errors. Launcher prefers it, retaining older builds as fallback. Generic `--smoke-clip=NAME` tests a selected startup clip; WPF smoke confirms sideways selection, all three available clips, moving skinning and rendering, exit zero. Independent C#/NumPy skinning agrees across three poses × 5419 vertices within 4.44e-16. Screenshot inspected. These checks establish bounded preview operation, not source-game visual parity, collision correctness or dynamic direction selection.

Artifacts: `NativePreviews/native-runr.json`, `NativePreviews/native-runf-neutral.json`, refreshed `native-runrf.json`, three-clip `current-native-run.json`, `sideways-run-preview.png`, `ControllerState/native-empty-row-validation.json` and updated `native-composition-validation.json`.

The open older viewer instance retains its loaded data. Reopen Launch_Viewer.cmd to access the three-clip dropdown. The index-finger issue remains parked.
