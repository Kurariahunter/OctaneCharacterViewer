# Native scalar and local finger replay — 2026-10-21 20:14:39

Capture `ce_idletransition_20261021_201439_247337000.jsonl` is3,189,950 bytes, SHA256 `9ea6daf0e739d58fcb9a9ee9b8c6c54326215cef6741ac23cdd264e59e2ff068`. Schema v2;51 pose records; normal `transition_complete` stop; `breakpoints_released=true`; no rejected rows.

All51 rows match original-PC file sampling exactly at the captured sampler time. All306 final scalar values also match execution of original Float-blender4E3050 using the captured prior output, prior fade and processor fade-bypass bit. Feeding those replayed values into the native finger relationship reproduces all four local joint outputs in every row:1,632 float components, zero numeric error.

Coverage: passive18 rows, specific01 fourteen rows, specific02 nineteen rows. Sequence33 is a right-hand specific02 transition at time0: previous fade1, current factor30 approximately0.9765624403953552. Its maximum source-to-final difference is0.00000858306884765625; native replay matches that difference exactly. The other50 rows have identical source and final scalar values. Thus this live capture verifies a nontrivial transition but does not independently cover the helper's increasing-fade branch; that branch currently has synthetic-state native tests.

The analyzer now requires stable clock/input/joint stamps and separately reports source, final scalar, and local-joint parity. Ordered capture links still do not prove thread/call-stack identity. Relationship blobs are fully identified by the logger against the configured PC source blobs.

This validates the captured single unflagged contributor with unit source weighting, using captured state. It does not establish a complete independent controller scheduler, world-transform/GPU parity, running index-finger correctness, or other rigs. The viewer has not been changed.

Next work can use this verified stateful scalar operation in controller reconstruction. Preserve per-processor previous output/fade and native fade-bypass semantics; do not replace them with fixed finger offsets. Remaining controller lifecycle and fade producers must remain explicit research boundaries. No additional generic idle capture is needed for this result.

Report: `ElsaSceneResearch/ControllerState/idle-transition-analysis-201439.json`. Native adapter: `ElsaSceneResearch/native_pc_blend_replay.py`; analyzer: `ElsaSceneResearch/analyze_idle_transition_capture.py`.
