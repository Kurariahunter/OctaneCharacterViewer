# Captured activation and duration fallback — 2026-10-21

Capture `ce_activationfade_20261021_210508_250366046.jsonl`:184,025 bytes; SHA256 `509e42f105da2575f700587369318e7dbc3ccfee6c514783a7cf8e29e8ee8bbc`. One activation and two matched update records, linked to PC Elsa specific03/controller0A54B980/TransitionProcessor0AE45740 in PID104600. Normal transition_complete stop, all breakpoints reported released.

## Exact independent replay

The selected configuration contains Transition integer-1 and parameter1. Actual activation arguments are duration-0.03333333507180214 and parameter1, exactly matching native float32 conversion by1/30. The global clock offset is0.004000000189989805; activation initializes local/previous time to43715.89453125 from clock43715.8984375, matching original instructions exactly. Completion clears.

Both captured update snapshots replay exactly through53C800, including local/previous time, curve fields, completion and outputs. Factors are0.0390624962747097 and1.0. All3 recorded operations therefore match their independently supplied prior states. Complete source ClipData hashes are verified.

**The capture is not a continuous numeric chain.** Between activation return and first update entry, duration+24 changes from the negative value to0.10000000894069672 without that writer being captured. Between the first update return and next captured entry, local clock/time/completion advance without all intermediate calls being captured. The analyzer exposes both gaps and reports continuous_numeric_chain=false. It does not reconstruct missing evaluations from interpolation.

## Matching native fallback path

The controller path at770364..77038C loads controller+64, callsBD74B0 to read processor+24, and replaces duration through525CB0 only when the current duration is negative. Replacement is the enclosing function770210's fifth argument. Zero/positive durations are retained. Its direct caller at788F60 forwards that argument; the origin/value selected farther upstream remains to be traced.

`test_transition_duration_fallback.py` executes the original guard/getter/setter window in12 cases, all passing. It also verifies that supplying the observed replacement value explains the observed duration-only change while preserving numeric time/curve/completion fields. This is candidate linkage using an observed later value, not independent live evidence that770387 performed this particular write or that its caller passed that value. No universal0.1-second default has been installed.

Negative durations are now permitted by the offline activation adapter because they demonstrably occur in the real activation path. The original native evaluator retains its own nonpositive-duration behavior; no Python clamp is substituted.

## Validation and next step

`test_activation_fade_analysis.py` checks3 exact recorded operations, requires the missing-write gap to remain visible, and verifies that corrupting an output causes a mismatch. The12 fallback tests pass. Reports/disassembly are in `ElsaSceneResearch/ControllerState/activation-fade-analysis-210508.json`, `transition-duration-fallback-validation.json`, and `transition-duration-fallback-disassembly.txt`.

Next trace the fifth argument passed through788F60/770210 to identify its actor/group/default source. The bridge/static path can be inspected before requesting another execution capture. The viewer remains unchanged; this result does not yet provide a complete actor scheduler or resolve running fingers.
