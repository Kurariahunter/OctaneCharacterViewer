# PC Elsa facial skin paths — 2026-10-22

Update: the four eyelid paths now have a separate opt-in bake and bounded native tests. See EYELID_GRAPH_HANDOFF.md. The original eight-path artifact and results below remain unchanged.

Prepared viewer animation:

`F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-facial-paths.json`

Use Open evaluated animation. This is an opt-in preview; startup/default playback has not been replaced.

## Blocker and native path

The initial audit attempted14 facial/eye skin outputs. Eight brows/jaw/lips stopped at unsupported TransformTranslationOrientationScaleConnection. Four lids stopped at unvalidated relationships. Eye direction stopped at TransformVectorWithDilation. Those are separate boundaries.

The PC registry at5020AF binds ProcessorNode::TransformTranslationOrientationScaleConnection to factory4F4C40. Factory4ED810/4E13A0 allocates constructor4BAB50, which assigns vtable1B2DE0C. Its execute slot+40 points to4D9F50, a wrapper for4C7750; that calls4BD920 for orientation/scale handling. Input wiring4C6F80 supplies Input, optional TranslateOffset, RotateOffset and ScaleOffset. The eight encountered PC facial instances contain only Input and Output.

`native_pc_scaled_connection.py` runs the original4D9F50 path with an explicit typed Transform input/output and null optional offsets. The result copies input translation, orientation and scale but preserves the destination's Unscale. It is not equivalent to replacing all16 floats with the input. No-offset100 randomized tests verify this exactly, including nonuniform scale and differing destination Unscale. Other offset/type combinations are rejected by the graph adapter rather than guessed.

The native graph evaluator now uses that adapter for the observed no-offset connection. All eight actual PC paths produce finite native matrices at start/middle/end of specific03 (24 smoke checks). Smoke success is not live parity.

## Viewer integration and measured difference

`evaluate_native_clip.py` adds `--native-facial-paths`, restricted to the supported PC Elsa idle profiles. It evaluates BrowCenter, BrowLeft, BrowRight, Jaw, CornerLipLeft, CornerLipRight, LowerLip and UpperLip through their source skin outputs, instead of inheriting their bind offsets from the head.

The prepared artifact also enables the earlier explicit IdleC Float/Dilation/Transform transition options. It evaluates54 source bones in the62-bone palette, compared with46 previously. The303-frame/152-sample bake passes its palette/native-matrix/dress geometry checks.

A numerical comparison against the previous typed transition changes exactly those eight facial bones, in152 samples. All other exported bone matrices are identical. The initial differences are sub-micro component values; later motion reaches a maximum matrix-component difference0.1741443890699466. This is a matrix-component difference, not a distance, angle, or visual-error score. No screenshot or live-game facial comparison was performed.

## Reproduce

```powershell
& 'C:/Users/Kurar/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'F:/DisneyInfinityPortalTest/OctaneCharacterViewer/evaluate_native_clip.py' 'F:/DisneyInfinityPortalTest/ElsaSceneResearch/InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions/elsa_bm_idle_specific03.oct' --output 'F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-facial-paths.json' --idle-transition-state '%FILENAME%/BasicMobility_Group/Idle_Group/Passive_Group/IdleC' --idle-transition-dilations --idle-transition-transforms --native-facial-paths
```

Evidence: ControllerState/facial-graph-initial-audit.json, scaled-facial-connection-disassembly.txt, scaled-facial-connection-validation.json and NativePreviews/facial-paths-comparison.json.

## Wii U reference and remaining work

The RPX symbols remain a useful named cross-platform reference. This particular connection was traced and tested directly in the PC executable; no Wii U-to-PC function equivalence was established or needed to claim its behavior. Symbol searches are saved under WiiUResearch/RPX/facial-connection-symbols.json; they are investigation leads, not verified matches.

Next: investigate the four native eyelid relationship paths, then the eye-direction vector transform. Missing-source defaults and automatic event/branch scheduling remain unresolved. This adds file-driven native graph evaluation, not pose offsets, an open-eye correction, a running-index-finger fix, or a complete engine recreation.
