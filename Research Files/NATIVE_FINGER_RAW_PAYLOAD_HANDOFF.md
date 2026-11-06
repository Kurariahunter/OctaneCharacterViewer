# Preserve native finger payloads in the viewer — 2026-10-20

Comparing actual viewer evaluation routes against `ce_worldchain_20261020_003610_90229843.jsonl` exposed a small precision difference. The original relationship outputs were converted to affine matrices and subsequently reconstructed as rotors, losing native quaternion norm drift. Dilation skin outputs also used the viewer's unit-quaternion matrix formula rather than the original Dilation-to-matrix conversion. The initial 219-case audit failed at maximum matrix difference 0.00006550545045980183; Transform packed conversion error was at most 0.0000005960464477539062.

`pc_finger_controls.prepare_fingers` now retains native relationship outputs in the raw evaluator cache alongside its existing affine cache. `LegEval` routes TransformDilationWithTransform output through the raw native operator and the original Dilation-to-packed-matrix function. This preserves native numerical behavior without manual pose offsets or changing animation curves.

The updated boundary audit injects captured local and parent/converter inputs using the same raw-cache path as the viewer. All **219 cases now match exactly**, including final second-joint affine exports: maximum matrix and packed errors **0.0**. This checks those bounded routes with captured inputs, not full viewer source composition or the game's renderer palette consumption.

A full forward-run fixture bake passes: 37 evaluated frames, 19 output samples, 46 source-evaluated bones and 62 palette bones. Maximum ankle endpoint error 1.03e-6, native matrix/point error 2.38e-7, TRS shear 1.54e-7, dress root error zero and dress segment length error 3.89e-7. The bake is `NativePreviews/native-run-raw-finger-check.json`.

Audit artifacts: `ControllerState/world-chain-viewer-math-audit.json` preserves the failing baseline; `ControllerState/world-chain-viewer-math-fixed.json` records the exact updated result. Native validation reports are alongside each audit. No claim that this small numerical correction alone fixes visually noticeable finger deformation; upstream pose composition and actual rendered palette/bind application remain separate validation boundaries.

The hidden WPF selected-native smoke test exits zero and passes loading the run preview (19 samples, 46 source/16 fallback coverage). Independent C# versus NumPy skinning passes all 5419 vertices in each of three poses, maximum coordinate difference 4.44e-16. This verifies application rendering arithmetic with supplied palettes, not game visual parity.


## Visual comparison follow-up
Timing-matched saved previews show no meaningful visible hand change. Across 19 poses, latest hand displacement is at most 1.405e-7 model units (about 0.0003 pixels at the generated enlarged hand scale); older fixture checkpoint comparison is likewise about 1.351e-7. Full-mesh maximum displacements are 3.31e-5 and 1.12e-5 respectively. These results establish numerical changes, not a visible finger-pose fix. See visual-progress-comparison.png/json and compare_visual_progress.py. Images are shared-camera untextured geometry renders from the same float32 skinning inputs, not actual viewer screenshots or game comparisons.

