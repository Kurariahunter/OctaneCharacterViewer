# Foot relationship native evaluation checkpoint

Updated2026-10-15. This advances FOOT_RELATIONSHIP_HANDOFF.md from metadata-only tracing to execution of the authored foot relationship math.

## Result

The original complete RelationshipProcessor entry0x54C9A0 now returns successfully in an isolated minimal fixture. Its output matches separate input evaluator0x544E00 + output writer0x53D2B0 execution exactly in69 cases: neutral, single-axis values[-100,-75,-25,0,25,75,100] for each of4 controls, and40 deterministic mixed-input cases.

Tested source is the identical580-byte RelationshipData in Elsa nodes39/66, SHA25673032eb1a654670678aae981cee41c85d79bdfd586156ceb61b851aca270cce1. Executable hash remains pinned in foot-relationship-native-validation.json. Native code was emulated, not launched as a game.

## Observed response

Each scalar affects only its corresponding output rotation. The selected output type is Dilation; quaternion Y/Z components and translation stay zero, uniform scale stays1, and quaternions remain unit within1e-5. Unrelated outputs are unchanged in the axis-isolation checks.

Under the transposed source quaternion matrix convention, rotations behave approximately as:

- output0: +input0*pi/200 about source X
- output1: -input1*pi/200
- output2: +input2*pi/200
- output3: -input3*pi/200

This is a comparison model, NOT an exact replacement formula. The maximum difference from ideal linear angles is0.00023973127728460497 radians. Zero controls produce small original-curve quantization residuals: max quaternion XYZ component0.000035953773476649076. Do not silently zero/correct these or declare them exact bind-pose matches.

## Source input/output mapping

Processor24 left: inputs [40 Ball,41 Heel,42 Tip,38 Toes], outputs [58,52,50,92]. Processor34 right: inputs [67 Ball,68 Heel,69 Tip,65 Toes], outputs [85,79,77,98]. Both share identical relationship bytes, so the minimal numeric relationship tests use one shared blob, not two independently different relations.

Clip table inspection: active/passive idle have all8 scalar controls in constant-channel records, opcode0x0A, value0. No timed commands drive these8 scalars in those two clips. The active-to-passive transition contains timed scalar commands for some of them, but transition playback has not been tested here.

These idle relationships are effectively fixed near-identity rotations. This does not remove the need to decode Foot_Group and FootCenter transforms, body/hip conversion and leg IK. These are not complete ankle-target outputs by themselves.

## Runtime object details now established

Processor input table: uint16 count at+0x5C and uint16 relative pointer-table offset at+0x5E. Output table: count+0x60 and relative offset+0x62. Unlike IK, these are count/offset pairs, not the IK offset/count byte layout. Helper0x53CEA0 reads input nodes from this table.

Cache objects at+0x50/+0x54 provide uint16 segment-cache arrays via cacheObject+0x44. Our test caches are four zero-initialized uint16 entries each; returned cache words are recorded. Processor+0x58 points to RelationshipData whose+0x3C points to authored bytes. Group index at+0x64 iszero.

0x53E920 is now more specifically traced as output version-stamp propagation: find the first non-null output, call0x506320 to obtain metadata's uint16 version via node+0x1C -> metadata+0x20, then assign that version to non-null outputs at+0x20. It does not perform the relationship numeric interpolation. The full entry includes this routine.

Output type checks select the Dilation payload layout;0x504340 writes its quaternion, translation and scale. Our fixture supplies a minimal selected-Dilation type predicate and zero version metadata. This validates that branch's numeric behavior, not original class registration or arbitrary object types.

Input evaluation iterates section0 records through0x503D60/0x503D80, reads input scalar payloads, and invokes scalar dispatcher0x53D090. Section1 then consumes section0 numeric results. Dispatcher inspects(record+4)&0x1C0 and calls type-specific curve routines. Several candidate curve implementations are listed in relationship-scalar-evaluator-disassembly.txt; they have not all been independently decoded.

## Limits

This is a controlled minimal runtime fixture. It resets segment caches and initializes output Dilation transforms to identity for each case. It does not test persistent game cache state, nonzero preexisting output transforms, out-of-range controls, other relationship blobs, other type dispatch branches or complete game loader correctness. Comparison of full vs staged execution is internal consistency; approximate linear-angle behavior supplies an additional numeric sanity check, not independent original-game playback ground truth.

No production graph/importer changes or new character preview were made. Unsupported RelationshipProcessor and IK nodes still fail in the general evaluator unless a separately supported integration is implemented later.

## Reproduce and continue

Run python ElsaSceneResearch/native_foot_relationship.py with existing research dependencies and pinned local executable. It saves foot-relationship-native-validation.json. Native_foot_relationship.py exposes run(values,full=True) for the tested shared blob. Preserve input order and the scope above.

Next:

1. Validate original Foot_Group/FootCenter transform chain and required inverse/concatenate/basis operators against executable implementations. Idle scalar foot records are already constantzero; avoid spending effort on invented movement there.
2. Verify relationship neutral output against authored graph baselines with explicit quantization tolerance; do not hide differences through broad rotation corrections.
3. Feed actual original foot target translations, pole vectors and knee twist into native IK. Retain explicit unsupported-operator rejection until every dependency is accounted for.
4. Resolve upper-leg-to-skin composition and scale before generating a new Elsa foot-contact preview.

Primary artifacts: native_foot_relationship.py, foot-relationship-native-validation.json, foot-relationship-structure.json and relationship-*-disassembly.txt. Existing character previews remain available unchanged.
