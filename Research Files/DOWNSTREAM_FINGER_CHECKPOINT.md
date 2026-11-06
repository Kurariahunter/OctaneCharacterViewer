# Downstream finger audit checkpoint

Expanded pc_finger_transform_audit.py beyond two-input chains to native one-to-eight-input Dilation chains, mixed inverse chains with source-derived normal-input counts, and unary InvertDilation. The same run start/middle/end diagnostic bake now gives:

- 57 ConcatenateChainDilation comparisons.
- 15 ConcatenateChainInverseDilation comparisons.
- 9 InvertDilation comparisons.
- Maximum matrix error 3.703062273485713e-7 across all 81.

The entire 19-sample clips payload still equals the pre-diagnostic run bake. These are operator tests with evaluator-supplied inputs, not independent live world-transform captures. They include shared control/body ancestors reached during traversal, not exclusively finger-local operators.

## Current-pose skinning reference

The WPF SelfTest now embeds the actual sampled pose beside each skinned vertex reference. Previously validate_skinning.py assumed a fixed older run cache, which could mismatch whichever native preview was loaded by the latest smoke test. The validator now uses embedded samples when present and retains old-cache fallback for older reference files. JsonOptions includes public pose fields when serializing.

Release build has zero warnings/errors. Hidden selected-native/default-timing smoke exits zero and produces three self-contained current-pose records. Independent NumPy skinning agrees with C# for all 5419 vertices in each of three poses, maximum coordinate difference 4.440892098500626e-16. This verifies that both implementations apply the supplied palette/bind poses/weights consistently; it does not prove those supplied values match the native game's final mesh.

Artifacts: finger-expanded-hierarchy-validation.json, skinning-validation.json, skinning-reference-points.json, selected-native-preview-smoke.json, and NativePreviews/native-default-run-finger-audit.json.

## Remaining scope

Unchecked by this expanded audit: Dilation/Transform translation-orientation connections, Transform-Dilation conversions, mixed Transform chains, and upstream compose/Euler nodes. Many already use native helpers in the renderer, but they need an end-to-end correspondence check, not merely rerunning the same helper on itself.

The live idle relationship checkpoint remains exact at the local outputs. Run composition is not established by that idle result. Do not infer the game has the same final palette because isolated operators and CPU skinning agree.

Next audit source SkinInfluence associations against exported mesh bone order, bind-pose matrices and vertex influences; check whether the relationship-to-world conversion reaches the correct associated output for each hand bone. If that correspondence holds, target a final native skin-matrix capture for the remaining comparison. No manual finger or pose correction was made in this step.
