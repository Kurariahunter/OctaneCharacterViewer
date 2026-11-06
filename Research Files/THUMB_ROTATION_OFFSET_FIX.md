# Thumb rotation offset integration — 2026-10-20

Found a substantial omitted operation in `NativeSkinEval`: TransformTranslationOrientationConnection copied its input orientation while ignoring RotateOffset. Elsa processors 121 and 126 connect inputs 332/337 to thumb transforms 222/228 and explicitly reference rotor nodes 3/2, both approximately a 180-degree Z rotation. The other six connections of this type declare no rotation offset.

Static EXE chain: registration string `ProcessorNode::TransformTranslationOrientationConnection` at 1B302E8 → factory 4F4940 → 4ED600 → 4E11E0 → 4CD490 → constructor 4BA990 → vtable 1B2DD04 → execute 4E84A0 → helper 4DC8C0. That helper passes the optional rotation input to 4C7D70. Offline execution confirms that an identity input plus a Z half-turn offset produces the offset orientation, preserving translation and existing scale/unscale fields.

The native connection wrapper now supports a 16-float Transform output initialization. The raw evaluator invokes it when RotateOffset is declared. No arbitrary hand offsets or animation-curve edits were introduced. Six synthetic cases, three input rotations for each thumb, match original native execution exactly. These are native fixture tests; live thumb output capture has not yet independently confirmed this path.

The corrected forward-run bake passes 37 evaluated frames and 19 exported samples. Matched old/current geometry comparison shows maximum hand vertex movement **0.0498341 model units**, approximately **105 pixels** in the enlarged comparison, unlike prior negligible numerical changes. This is a demonstrably visible thumb change, not yet proof of in-game visual parity or a fix for every finger.

The WPF selected-native load/render smoke exits zero. A stable corrected cache, `NativePreviews/current-native-run.json`, is preferred at startup, with the old run cache retained as fallback. The native backend recomputes the corrected path when previewing supported clips.

Artifacts: `thumb-offset-comparison.png/json`, `NativePreviews/native-thumb-offset-run-test.json`, `ControllerState/thumb-offset-validation.json`, and `test_thumb_rotation_offset.py`. Next validate the visible thumb against the game and, if necessary, capture its actual connection output. Index/middle palette and raw mesh findings remain separate evidence.
