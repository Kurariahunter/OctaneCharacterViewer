# Skirt bulge audit and authored knee-control correction

Date:2026-10-16. Working directory F:/DisneyInfinityPortalTest/ElsaSceneResearch.

## Delivered result

New independent prefab Assets/ElsaKneeDressResearch/KneeDressDiagnostic/Elsa_KneeDressComparison.prefab. Editor menu Tools/DI3 Static Converter/Research/Create Elsa Authored Knee Dress Preview. Native active/passive .anim clips and controllers beside prefab. All previous previews preserved.

IMPORTANT: active skirt bulge remains. This checkpoint fixes a genuine missing source control, not the entire visible problem. No speculative edits were made to the original skin weights, mesh, triangles or bind matrices.

## Controlled isolation

Movie012 shows a persistent side bulge. CPU linear-blend-skinning inspection localizes the outer positive-X skirt vertices (for example5170/5171/5174/5180/5181) to dressRightStart and UpperDress_Right weights. The185checked lower-skirt vertices have over50%weight on the four dress palette entries and bind height<.85. This is a diagnostic mask, not a new segmentation or weight assignment.

A reset-only counterfactual re-evaluates the same authored anchors but calls native chain reset every frame, rather than advancing persistent simulation. The first frame is identical to the stepped bake, and the bulge exists there. Across the previous active bake, maximum reset-only versus stepped lower-bone matrix difference is0.0005256831645965576. Previous passive bake is exactly identical. This evidence rules out accumulating native integration instability as the cause in these tests. It does not prove complete source pose fidelity or validate every skin/reference assumption.

## Real decoder omission found

Constant clip scalar channels were not included in the selected controls:

- Port189 -> model Float43 -> connection692 -> native left IK twist.
- Port197 -> model Float70 -> negate676 -> native right IK twist.
- Active constants: -0.07999999821186066 and+0.07903599739074707.
- Passive constants:0 and+1.
- Descriptor opcode0x0a (Float value), flags16. Active float pool indices101/102, passive6/105.

Original native IK interprets these values consistently with radians: recovered active thigh/dress changes4.583662611713893degrees left,4.528423825182368degrees right; passive right57.29579400345707degrees. No guessed degree conversion is applied; the values are passed to the original runtime. Source right sign inversion remains in its authored FloatNegate graph node.

Changes: bounded Eval supports a finite Value override only on Float nodes; sampler selects43/70, recognizes constant opcode10 and persists their values into frame controls. Timed scalar channels are still unsupported by this sampler and must fail rather than be assumed decoded. Native foot, skin, upper-dress and dynamic-dress samples were all regenerated from those controls together.

## Validation

- Original source ankle targets still reached: active127frames maxworlderror7.957833959352189e-7; passive186frames9.842101345675368e-7.
- Dynamic roots pinned exactly in both; chain length maxerrors active5.910069528214379e-8/passive7.221670444979011e-8. Skin-origin errors active1.2753339684474237e-7/passive1.156641147752108e-7. Native aim residual remains about0.000487direction magnitude (no artificial alignment correction).
- Corrected source twist changes only expected pose families: active Knee_Left/Right,UpperDress_Left/Right,dressLeftStart/Right; passive Knee_Right,UpperDress_Right,dressRightStart. Ankle/foot targets and other palette transforms retained within floating-point tolerance.
- Source weights, positions, triangles and bind-world matrices compared for exact equality. Weight sums valid. CPU skin outputs finite.
- Active skirt extent atframe60 remains asymmetric; maximum positive-X extent changes from0.32567to0.32960. Thus this source-correct fix does NOT eliminate the bulge and must not be presented as a cosmetic improvement.
- Isolated Unity6000.5.8f1 build/verification passed: bind deformation1.816246e-7; curve reconstruction active4.768372e-7/passive4.172325e-7; saved Animator instances move. World TRS residual1.5668599798300187e-7. Render inspected; active bulge remains. Diagnostic labels shortened after build to avoid overlap; no animation/mesh changes in that label-only edit.
- Live materials use the previously reviewed URP counterparts; all18non-built-in referenced GUIDs resolve.

## Reproduction/evidence

sample_knee_dress_controls.py; validate_knee_skin_clips.py; sample_knee_upper_dress_worlds.py; sample_knee_dynamic_dress.py; build_knee_dress_preview_data.py; DI3ElsaKneeDressPreview.BatchValidate. Shared evaluate_elsa_head.py contains the typed Float Value override.

sample_dress_reset_only.py regenerates the historical zero-knee reset-only counterfactual. audit_skirt_bulge.py verifies source-weight ownership, exact preservation, authored scalar records and before/after palettes.

Reports: skirt-bulge-audit.json; native-knee-skin-clip-validation.json; native-knee-upper-dress-samples.json; native-knee-dynamic-dress-samples.json; knee-dress-export-validation.json; knee-dress-delivery-validation.json; knee-dress-unity.log.

## Remaining investigation

Focus on the static pose/reference chain feeding UpperDress_Right and lower-dress anchors. The active bulge is present before simulation stepping and remains after the missing twist controls are restored. Compare source proxy/joint frames, original bind versus evaluated pose, omitted layer/constraint behavior and a trustworthy in-game pose reference before deciding whether a visible source asymmetry is wrong. Neither the current audit nor target-reaching tests alone proves a complete original pose. Force defaults, full engine scheduling, retargeting, arm/face/hair completion and seamless loop boundaries remain qualified as in NATIVE_DYNAMIC_DRESS_HANDOFF.md.
