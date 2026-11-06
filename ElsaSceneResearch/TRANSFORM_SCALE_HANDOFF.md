# Native Transform Scale/Unscale checkpoint

Updated2026-10-15. Extends ORIGINAL_FOOT_TARGET_HANDOFF.md; original character previews and production importer remain unchanged.

## Native helper results

Located Transform ComponentProcessor vtable0x1B3514C, execution0x5303E0. Low-bit-tagged aggregate/component pointers distinguish compose/decompose; relative component table maps Translation, Orientation, Scale and Unscale. Native compose copies Scale.w into uniform field, preserves Scale.xyz and copies Unscale.xyz while forcing Unscale.w=1.

Transform payload: qxyzw at0..0xC, translation+0x10..0x18, uniform+0x1C, Scale4 at+0x20 and Unscale4 at+0x30. Flattening to a regular matrix before retaining these fields was insufficient.

Native0x4C4350 point transform verified as: Unscale.xyz * (R * (point * Scale.xyz * uniform) + translation), with composed Unscale.w forced1. It updates the stored Scale.w copy from uniform. Native0x4C2D50 concatenation has its own metadata propagation: preserves child's Scale vector, combines child/parent uniform factors, resets resulting Unscale vector to1, and transforms child translation using child Unscale and parent orientation/uniform. It is not arbitrary multiplication of two flattened geometry matrices.

200 native component-compose,200 point-transform and100 concatenate tests passed with positive factors0.8..1.2 and mixed-axis rotations. Max numeric error3.426e-7. Original native helper execution plus independently written field/formula comparisons; not full loader/hierarchy validation. See native_transform_scale.py and transform-scale-native-validation.json.

## Recorded idle scale fixture

Used source active/passive target samples, original native IK rotors and full4-float scale payloads. Native Transform compose+concat+point helpers with explicit child Unscale=parent Scale reproduce the scale-aware segment endpoint. Active254 checks max7.335e-7; passive372 checks max8.529e-7 model units. Midpoint positions from concatenation and point-transform helpers agree exactly in the recorded fixture. Lower segment length0.41155261 is rounded from authored geometry.

This establishes that this explicit compensation fixture closes the earlier0.014943 passive endpoint error. It does NOT independently establish the original skin runtime assigns child Unscale this way, nor validate full character skin deformation. The earlier plain-matrix passive results remain historical diagnostics. Do not silently promote fixture metadata to confirmed original hierarchy behavior.

## New Unity diagnostics

Assets/ElsaOriginalLegResearch/OriginalTargetsDiagnostic_active/OriginalLegTargets.prefab
Assets/ElsaOriginalLegResearch/OriginalTargetsDiagnostic_passive/OriginalLegTargets.prefab

Drag one into an empty scene and press Play. Includes camera. Orange marks source target, cyan solved ankle. These use ORIGINAL idle-derived targets with the explicit scale fixture, unlike the earlier synthetic bend demo. They remain stick legs in hip-space display, not final original skinned Elsa animation. Labels state partial leg graph/scale fixture.

Isolated Unity6000.5.8f1 built both assets, checked target-marker errors and validated saved passive Animator movement; inspected passive render. Copied materials converted to URP and GUID references checked. Live project refresh/playback remains to be checked. Older previews preserved.

## Next source trace

Follow how the original skin/basis hierarchy supplies Unscale, including parent/child Scale component wiring and final influence transforms. Resolve missing upper-leg-to-skin mapping. Only after corroborating that assignment should the compensated original-clip matrices be exported as actual Elsa bone curves and the floor-contact/skinning test repeated. No manual foot offsets or forced unit scale have been installed.

## Reproduction

python ElsaSceneResearch/native_transform_scale.py
python ElsaSceneResearch/sample_original_foot_targets.py
python ElsaSceneResearch/validate_recorded_scale_chain.py

Existing machine-specific native research dependencies and pinned local executable required. The Unity diagnostics play sampled positions without the executable. Research copies in the project are evidence copies; the F: research directory contains their dependency graph.
