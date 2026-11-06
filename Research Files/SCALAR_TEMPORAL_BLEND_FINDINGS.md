# Scalar transition state — 2026-10-21

The 200631 live capture established exact source sampling in all109 accepted rows, with four source-to-final differences at the Float-blender return. It did not capture previous output or previous cumulative fade. Those live final values cannot yet be independently replayed from complete observed inputs.

## Executable path

The Float blender begins at preferred VA4E3050. It takes the minimum factor30 over relevant contributors, then, unless the processor's fade-bypass bit31 at +18 bypasses fading, calls525450. That helper reads and updates the processor's stored fade at +34. In its interior increasing-fade branch it returns `(current - previous)/(1 - previous)`, not simply the current cumulative fade. Falling factors take a different branch, and threshold branches clamp near the endpoints.

At4E358F–4E35A4 the blender reads the previous scalar output from outputNode+34 and blends toward the newly computed target using that incremental factor. The fade-bypass flag can bypass this mixing. A near-zero incremental factor can return early without rewriting the value, while updating its stamp. These observations explain why a current source value and factor30 alone are insufficient inputs for native reproduction. They do not prove the exact prior state for the four old live rows.

## Offline validation

`ElsaSceneResearch/native_pc_blend_replay.py` now optionally executes the full original Float blender4E3050 with synthetic cached inputs and explicitly supplied previous output/fade/fade-bypass state. Existing Dilation execution4E35D0 remains the default.

`test_scalar_temporal_blend.py` passes six full-native state cases: increasing, decreasing, zero and complete fades, plus a fade-bypass bypass check. For target10 and previous output2, cumulative factor0.5 yields6 with previous fade0, but4.6666669845581055 with previous fade0.25. These are synthetic-state native results, not inferred live inputs. The existing36 controlled Dilation blend cases also pass after the adapter change.

Validation: `ElsaSceneResearch/ControllerState/scalar-temporal-native-validation.json`.

## Next live check

Updated `DI3_IdleTransitionLogger.lua` emits schema `di3_idle_transition_v2`. It replaces the early-return breakpoint with a Float-blend entry breakpoint, preserving the four-hardware-breakpoint limit. It captures prior output, prior fade, flags and entry order; normal returns attach that entry snapshot. Missing/early returns cannot reuse an older completed trace.

The mock test passes entry/return capture, exact native final-output replay for its genuine-PC-source fixture, older-probe unload, wrong-port rejection, cleanup and beep. This does not yet validate live v2 state replay.

Run the same updated logger, F8 with Elsa idle/unpaused, wait for the completion beep. No scene reload needed. Analyze with `analyze_idle_transition_capture.py`; compare both `exact_source_rows` and `native_final_exact_rows`. No viewer pose or manual finger correction has been added.
