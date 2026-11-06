# Native clock option in the viewer

The viewer now exposes **Native clock (single activation)** beside Preview native clip. Enable it before selecting a supported OCT to pass `--timing native-default` to the Python evaluator. The option is unchecked by default. Changing it applies to the next native preview; it does not reinterpret the currently loaded cache. During evaluation it is disabled with the preview controls.

The loaded report's timing_configuration.mode is displayed in the scope text, distinguishing native clock / single activation from fixture timing even when opening an existing evaluated animation. The existing playback timer already pauses at the cache endpoint. The underlying engine default mode's single activation is preserved; this option does not reconstruct game repeat/restart scheduling or change the existing source re-evaluation button.

All four supported PC Elsa profiles pass native timing bake invariants:

| Profile | Simulation frames | Output samples |
|---|---|---|
| Active idle | 253 | 127 |
| Passive idle | 371 | 186 |
| Forward walk | 49 | 25 |
| Forward run | 37 | 19 |

Release build succeeds with zero warnings/errors. A hidden WPF smoke run with `--smoke-test --selected-native-smoke-test --native-default-timing` exercises the checked option, backend arguments, native run bake, report loading and skinned rendering. It exits zero and produces a passing selected-native-preview-smoke.json plus the existing viewer smoke outputs. The resulting backend report explicitly has native-default timing. Summary: native-timing-ui-validation.json.

This is integration/invariant verification, not a frame-matched visual comparison to the game. Partial graph coverage, unresolved layering, collision/dynamics fixture assumptions and unsupported clips remain unchanged. Rendered preview still uses baked poses; this is not real-time reimplementation of the whole native engine.

Restart the viewer through Launch_Viewer.cmd to use the rebuilt executable. Select the checkbox, click Preview native clip (.oct), then choose one of the four supported extracted clips. Next useful check is a visual comparison of hands, braid and dress under this timing path before extending configuration modes or exposing repeated native activations.
