# Explicit Transform transition — 2026-10-22

The native Transform3d blender is now available as an opt-in backend path. RTTI identifies vtable1B2BA3C as Blender<TypedDataNode<Types::Transform3d>>, with execute4E3FC0 at vtable+40. It is distinct from Dilation execute4E35D0/vtable1B2B9C4.

## Verified numerical behavior

Transform uses full16-float output (rotation4, translation3, uniform1, Scale4, Unscale4). Its partial fade invokes525450 and retains prior factor at processor+34, unlike the tested Dilation path. A translation2 toward10 with successive factors.25 then.5 produces4 then6 for Transform, versus4 then7 for Dilation. Reusing either type's fade policy for all controls would be incorrect.

`test_transform_temporal_blend.py` passes12 cases with both quaternion signs, zero/full weights, rising/falling fade, translation and nonuniform Scale/Unscale. Retained-sequence and bypass checks also pass. These execute the original full routine with cached synthetic inputs, not a live actor's source/default bindings.

The existing ten Dilation cases, six Float temporal cases and36 controlled blend-order cases still pass after extending the common adapter.

## Preview and actual impact

`evaluate_native_clip.py` adds `--idle-transition-transforms`, requiring an explicit state path. Translation, quaternion and Scale channels must be present in both outgoing and incoming sources. This includes ten source controls and excludes nodes726,737,644,650. The existing idle evaluator's unit Scale/Unscale fixture is retained; no missing-channel runtime policy is invented.

Prepared artifact:

`F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-explicit-typed-transition.json`

It combines the earlier12 Float and25 Dilation controls with ten Transform controls. The303-frame/152-sample bake passes its geometry/native-matrix checks and executes3030 Transform blends.

**The exported palette is exactly identical to the prior Dilation+finger transition.** Do not present this as a visible improvement. The ten controls are brow, jaw and lip controls; those facial skin bones are not yet included in the46 source-evaluated bones and still inherit fallback offsets in the62-bone palette. Source differences during the initial window are also very small (max checked quaternion/translation component difference2.4582259356975555e-6). The source audit compares applied fields rather than different opcode encodings.

Reports: ControllerState/transform-temporal-native-validation.json, ControllerState/transform-transition-source-audit.json, NativePreviews/explicit-transform-transition-comparison.json and the prepared preview's validation JSON.

Reproduce with the prior explicit IdleC command, append both `--idle-transition-dilations --idle-transition-transforms`, and select the artifact path above.

## Remaining boundary

Missing-field defaults remain unresolved as a live blend policy. Existing native default-table getter tests establish table arithmetic only; they do not prove component participation, actor selection or when missing source channels inherit defaults. Keep incomplete controls excluded.

Next useful step is evaluating the native facial graph into the skin palette so these control outputs can affect the displayed face. Audit unsupported processors and compare native outputs before replacing fallback facial bones. No new Cheat Engine capture is required solely to inspect this completed numerical step.
