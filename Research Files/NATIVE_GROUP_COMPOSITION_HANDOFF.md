# Native forward-run group composition — 2026-10-20

The viewer now composes decoded main, upper-body and lean records into shared 52-byte channel rows and executes original routine 5A14D0 before applying leaf overrides. Explicit forward-run order/weights/modes are main (1,1), upper (1,1), lean (1,0). Port-to-node bindings must agree across layers. Partial translation/scale masks remain partial; computed graph outputs are still excluded by the leaf apply stage.

This replaces sequential layer application that restarted each record from serialized fields. The passive initializer and current profile phase remain preview fixtures. Runtime speed/direction graph selection, parent blending and scheduling are not integrated by this change. Walk and idle profiles remain on their existing path.

Tests cover partial channel preservation, isolation between ports, weighted scalar replacement, weighted additive translation and inconsistent binding rejection. The full run bake passes 37 evaluated frames and 19 exported samples across the 62-bone palette.

The visual comparison does **not** show a meaningful hand improvement: timing-matched old/current run previews across 19 poses have maximum measured hand displacement 1.053e-6 model units, approximately 0.0022 pixels in the enlarged geometry comparison. Maximum whole-mesh displacement is 0.000183653 model units. The visible finger defect is not resolved.

Artifacts: `NativePreviews/native-composed-run-test.json`, `native-composition-comparison.png/json`, `ControllerState/native-composition-validation.json`. Implementation: `compose_native_clip_layers.py` and `evaluate_native_clip.py`. The comparison uses matching untextured geometry projection and the viewer's float32 palette/bind inputs, not actual game screenshots.

Next actionable target: locate a game-versus-viewer pose or palette association difference large enough to explain the hand shape. Recheck actual rig bone mapping and full palette inputs before spending more captures on already exact individual operators. Do not claim full engine parity or add manual corrections to the native baseline.
