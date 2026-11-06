# Explicit native Dilation transition — 2026-10-21

Prepared viewer animation:

`F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-explicit-dilation-transition.json`

Use the viewer's Open evaluated animation command. This is an opt-in test; default playback and current startup bundle are unchanged.

## Native behavior

The native Dilation blender4E35D0 differs from Float4E3050. With one unflagged contributor and partial fade, it mixes the retained prior Dilation output with the new contributor using the supplied factor. It does not use Float's525450 incremental-fade helper on this path. Two successive factors.25 and.5 on a translation2 toward10 produce4 then7, whereas the Float state follows its separately tested incremental rule. Quaternion hemisphere/normalization and uniform-scale arithmetic run in original game instructions. No guessed Euler offsets or post-import pose corrections are used.

The adapter explicitly seeds its prior8-component output (xyzw rotation, xyz translation, uniform scale). Each control retains its own output/bypass bit. The original default blend adapter behavior is preserved when no prior Dilation is supplied.

## Preview scope

`evaluate_native_clip.py` adds `--idle-transition-dilations`, requiring the existing `--idle-transition-state` option. This test uses passive idle phase0 as the outgoing seed and IdleC as the incoming clip, with the file's EaseDuration3 and explicit zero-origin preview clock.

Of41 incoming Dilation leaf controls,25 have complete Orientation/Translation fields in both source poses and are included. The other16 are reported as excluded, including node344 with partial incoming fields and others lacking complete outgoing data. Computed graph outputs are not directly overridden. Uniform scale remains1 in this preview; nonunit output is rejected. Transform controls and remaining channels still switch directly. The twelve verified finger Float controls continue through their own native temporal path.

This is not a complete native state transition, live binding reconstruction, automatic event scheduler, or a running-finger fix. Bypass initialization and the passive phase-zero seed remain explicit fixture choices.

## Checks

- Ten synthetic native Dilation cases pass, including quaternion sign, endpoints, translation and scale; retained-output and bypass checks also pass.
- Existing36 controlled blend-order cases and six Float temporal cases still pass.
- The303-frame/152-sample preview passes its palette, native matrix and dress geometry checks;7575 Dilation evaluations complete.
- Comparison against the finger-only transition records initial pose changes and downstream dynamics. After the transition window, differences are confined to hair/dress in the inspected first samples; the comparison report does not claim every later component or live game parity.

Reports: `ElsaSceneResearch/ControllerState/dilation-temporal-native-validation.json`, `OctaneCharacterViewer/NativePreviews/explicit-dilation-transition-comparison.json`, and the preview's `.validation.json`.

Reproduction: use the command in EXPLICIT_IDLE_TRANSITION_HANDOFF.md, change output to the filename above, and append `--idle-transition-dilations`.

Next boundary: the native Transform blender and how partial/missing fields obtain defaults. Validate their native state and source bindings before including the remaining controls.
