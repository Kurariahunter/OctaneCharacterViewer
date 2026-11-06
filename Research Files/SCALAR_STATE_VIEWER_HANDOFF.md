# Native scalar state in idle preview — 2026-10-21

`evaluate_native_clip.py` now routes the verified twelve PC Elsa index/middle idle controls through original Float-blend instructions at4E3050 before the native relationship evaluation. `ElsaSceneResearch/native_scalar_state.py` owns a separate previous output, cumulative fade and fade-bypass flag per control, preserving state between evaluation ticks. New preview evaluations start a new state bank. Native scalar scratch memory uses32000000 to avoid the viewer's chain-reset workspace at11000000.

The current viewer is a single-clip preview. Its scalar factor remains explicitly1. No new fade timing, activation scheduler, joint offset, or manual pose correction has been invented. Locomotion's layered controller is not routed through this single-contributor path. Existing baked startup clips remain intact; freshly selected idle OCT previews use the updated Python backend without rebuilding the viewer executable.

## Validation

- State wrapper reproduces306 captured final game values exactly when supplied their recorded prior state. Independent controller keys retain separate state across updates.
- Specific02 preview completes401 simulation frames with201 exported poses and all previous palette/dynamics invariants passing.
- All199,392 matrix components across201 samples and62 bones are exactly equal to the previous specific02 bake. Full-weight state integration therefore preserves the existing animation.
- Native state evaluations:6,252, including120 warmup ticks.

Reports: `scalar-state-integration-validation.json`, `ElsaSceneResearch/ControllerState/scalar-state-wrapper-validation.json`, and `NativePreviews/native-scalar-state-specific02.validation.json`.

Prepared evaluated animation: `F:\DisneyInfinityPortalTest\OctaneCharacterViewer\NativePreviews\native-scalar-state-specific02.json`. Use the viewer's Open evaluated animation button to load it, or Preview native clip to evaluate an idle OCT with the updated backend.

## Remaining boundary

The new primitive is usable for time-varying factors, but the game controller must supply the correct factors, activation/reset rules and scheduling. Captured prior state validates the primitive; it does not independently reconstruct those producers. Next research should target the factor30 producer and controller lifecycle, reusing existing controller captures/static traces before requesting another capture. Do not claim that running index fingers are fixed by this integration.
