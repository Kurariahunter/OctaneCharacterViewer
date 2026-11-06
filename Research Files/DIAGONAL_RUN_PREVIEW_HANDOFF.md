# Diagonal-right run preview — 2026-10-20

Added the pinned PC `grl_bm_runrf.oct` source as a supported native preview profile. This reuses the verified sampler/rig pipeline, including the previously decoded 0x10 curve flag. The serialized WALKRUN group `Run Right Forward` supplies the main source, shared upper-body source at weight **0.9**, and its own `human_bm_runrf_lean_add` layer. Composition executes the original buffer blend routine. Exact companion file hashes, group source order and lean mode are checked before evaluation.

The run preview evaluator now selects group/lean companion from the profile and reads the selected group's upper weight. Forward run retains its existing default group and unit upper weight. The initializer, timing, gravity and warmup remain explicit preview fixtures; this is not dynamic speed/direction selection or full engine parity.

Startup cache `NativePreviews/current-native-run.json` includes both forward run and diagonal-right run. Select **grl_bm_runrf_NativePreview** in the clip dropdown, or open the native runrf OCT through Preview native clip. Per-clip source/composition metadata is stored in clip_sources; legacy top-level fields describe the first forward clip.

Validation: new bake passes 37 simulation frames, 19 samples, 46 source-driven/16 fallback palette bones. Max ankle endpoint error 6.31e-6; matrix/point error 2.68e-7; TRS shear 1.55e-7. WPF selected-native smoke evaluates the actual diagonal source, loads its output and renders it, exit zero. Independent C#/NumPy skinning agrees for three poses × 5419 vertices within 4.44e-16. Forward/diagonal geometry differs by more than 0.01 model units across matched samples, confirming distinct motion data rather than a relabelled forward cache. Saved screenshot inspected.

The running viewer locked the normal executable during build. A clean Release build with zero warnings/errors was produced in **bin/DiagonalPreview**. Launch_Viewer.cmd prefers this updated build and retains the original path as fallback. Close/reopen through that launcher to use it; the already-open instance remains on its loaded data.

Artifacts: NativePreviews/native-runrf.json, diagonal-run-preview.png, diagonal-run-delivery-validation.json and selected-native-preview-smoke.json. Index-finger investigation remains checkpointed; no new manual hand adjustments were added.
