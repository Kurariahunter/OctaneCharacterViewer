# Original foot targets and leg graph checkpoint

Updated2026-10-15. Continues the native foot relationship and IK handoff. No production importer, original game files or Unity previews changed.

## New executable-backed basis operations

60 deterministic mixed-axis rigid-transform cases for each of6 operators,360 total. All scale components fixed to1. Max error across the six operations4.291e-7. Explicit minimal native node/type metadata fixtures; full runtime loader not tested. See validate_foot_basis_native.py and foot-basis-native-validation.json.

| Operator | Factory -> wrapper/constructor chain | Runtime | Verified source matrix formula |
|---|---|---|---|
|TransformPositionWithDilation|0x4D47F0 ->0x4C3E90 ->0x4B6F20, vtable0x1B2C5CC|0x4D4B40|Converter @ homogeneous point|
|TransformDilationWithTransform|0x4D7590 ->0x4C5180 ->0x4B7540, vtable0x1B2CAD4|0x4D78D0|Converter @ Input|
|ConcatenateInverseTransformDilation|0x4F0240 ->0x4E9680 ->0x4DD6F0 ->0x4C99A0, vtable0x1B2E8E4|0x4D1220|inverse(Right) @ Left|
|InvertConcatenateChainTransform|0x4F17A0 ->0x4EA800 ->0x4DE410 ->0x4CA710, vtable0x1B2F064|0x4D2540|inverse(Input0) @ inverse(Input1)|
|Position3dOffsetProcessor|0x4F2BD0 ->0x4EC150 ->0x4DFF80 ->0x4CC0E0 ->0x4B8EF0, vtable0x1B2D20C|0x4C18A0 thunk ->0x4B8FD0|Input + Offset|
|FloatNegate|0x54B6D0 ->0x54B6A0 ->0x545E00 ->0x53FC80 ->0x5399A0, vtable0x1B34364|0x52D5C0|-Input|

The inverse-chain result differs from naively left-prepending inverse matrices: source input order is retained in this tested two-input chain. Test includes noncommuting rotations/translations; an initial reversed-order candidate failed and was rejected. These results do not validate arbitrary chain arity or nonuniform scales.

## Research-only graph integration

New evaluate_elsa_feet.py subclasses the bounded evaluator. It supports only Elsa relationship processors24/34 with the verified shared blob and scalar range[-100,100], and IK408/412 via isolated native routines. Other relations/IK types are rejected. Main production/evaluate_elsa_head.py support was not broadened.

The subclass includes checked matrix-to-source-quaternion conversion for feeding graph-derived rotors into native IK. Source component attribute order exposed another issue: applying Scale then replacing Orientation drops the scale. Diagnostic Transform compose now applies Orientation before Scale. This fixes attribute-order loss but is NOT a complete native Scale/Unscale implementation.

## Original idle sampling results

sample_original_foot_targets.py combines the selected original clip-local constant/timed controls at30Hz, now including foot group37/64, foot center47/74 and knee controls703/687, alongside body/hip/spine/shoulder/head controls. All8 scalar foot relationship controls are explicitly constantzero in active/passive idle files; their original quantization residuals are preserved by native relationship evaluation.

- Active:127 times,254 leg endpoint checks. Max target-to-reconstructed-ankle error7.57513901575561e-7 model units. Scale departure from1 <=1.10e-7. This establishes internal target -> native IK -> rigid forward-kinematics consistency for this clip, not skin/whole-game fidelity.
- Passive:186 times,372 diagnostic leg checks. Nonuniform scale departure up to0.0350783. Ordinary matrix chaining leaves up to0.0149429510 model-unit endpoint error. Passive is NOT validated ankle motion.

Sampling output: elsa-foot-target-samples.json and original-foot-target-validation.json. Intermediate matrices are hip-space graph transforms, not final Unity bone curves. Clip names inherited a diagnostic suffix; do not interpret that as final skin export.

## Passive scale investigation

Native solver emits scale compensation in the passive idle. A candidate forward-kinematics calculation that prevents parent nonuniform scale accumulating onto the child's scale reduces the diagnostic error to approximately9e-7 in an exploratory calculation. This is only a clue: it has NOT been independently verified against native Transform composition, so no such compensation was installed as a final decoder or Unity fix.

Transform payload observations: quaternion at0, translation at+0x10, uniform factor at+0x1C and extra4-float fields at+0x20 and+0x30. Existing scene Data uses Scale and Unscale vectors. Native compose helper0x4C2D50 copies the first operand's+0x20..+0x2C into output, combines uniform factors, resets output+0x30..+0x3C to1, and consults operand Unscale fields while translating. Simply treating the whole structure as a conventional4x4 matrix loses those semantics.

## Exact next step

1. Trace native Transform Scale/Unscale component compose and hierarchy concatenation, starting0x4C2D50. Construct nonuniform fixtures from recorded passive solver outputs and validate native child/parent transforms, not a guessed correction.
2. Extend representation to retain Scale/Unscale metadata instead of flattening prematurely to matrices. Verify source-to-skin composition and missing upper-leg mapping.
3. Re-run passive endpoint checks and compare active as a regression. Only then create an Elsa leg/foot-contact preview.

Do not manually offset feet, force scale1 or zero the relationship residuals to make a misleading successful preview. Current evidence supports a working active unit-scale graph segment and a clearly located passive scale dependency.
