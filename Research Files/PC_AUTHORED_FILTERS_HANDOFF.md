# Authored biped filter arrays verified

The runtime loader at 0x4FBBA0 (bounded interior trace already saved nearby) replaces `.ct` with `.bct` through string arguments at 0x4FBC2D/0x4FBC32: 0x1B2FC38 is `.ct`, 0x1B2FC3C is `.bct`. It parses named `Filters` and `Mirrors` sections. Their static string globals are 0x212062C and 0x2120634. Filter float payloads must remain separate from the uint32 mirror/remap payload.

Located installed source: F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/assets/gamedb/biped/characters/biped/biped.bct
SHA256: e47d4936acc1aef4f21f69cd577124db46c67e1189135e327ff46b4c96a93bcd

The safe tuple reader now handles float arrays with 16-bit counts (0x52), named float arrays (0x16/0x56), and the observed named uint32 array with a 16-bit count (0x35E). Compound records preserve the label in `value` and the numeric payload in `extra`; existing record shapes are unchanged. The BCT consumes its full byte length and its record count plus skipped implicit root matches the header. Truncated BCTs are rejected. Existing Yoda reader checks pass.

The BCT contains 92 named Filters, all with 968 float coefficients, plus a separate Mirror record. All 31 distinct named filter references (88 occurrences) in PC Elsa's BENT resolve in this biped BCT. No fabricated defaults were used for unresolved names. Preserve all 968 coefficients: the current PC Elsa/biped reverse map has 935 ports, which does not justify truncating the authored arrays or assuming equal lengths in every map.

All 92*112=10,304 filter/source-slot selections are in bounds through the verified LocalToPortIndices map. The native replay fixture was extended to keep arrays longer than 64 floats in separate memory from scalar nodes. It supports at most 1024 floats per array and fails outside bounds; this is a test-fixture limit, not an engine limit.

489 native tests cover each distinct mapped coefficient per filter. Each invokes the original 0x5440C0 contributor builder and 0x4E35D0 blend with the actual 968-entry filter array and actual port index. Expected weighted quaternion/translation comparison passes: max rotor error 9.405e-8; max translation error 1.163e-7. Inputs are synthetic base/delta poses, compact source slot zero, additive flag, scalar +0x2C=.5, unit scale, no fade. This is not proof that a particular Filter is active in the current game scene. Prior indexed-filter and 36 controlled blend regressions pass.

Examples: HeadTurn has coefficient 1 only at port 545. RightHandOnly has ten coefficient-1 ports. Upperbody has 31 coefficient-0.1 ports, not a binary mask. CarryRArm contains fractional values including .4, .5, .6, .9. Do not normalize or threshold these arrays by their names.

Reproduce: ../validate_pc_authored_filters.py. Reports and cached source coefficients are in this folder. The reader extension is ../../TupleDecoderResearch/decode_tup_safe.py.

Next resolve Filter assignment and inherited layers for the selected native clip/source network, then feed these authored port weights into the viewer's source composition. Walking/run declarations with no explicit Filter must not receive an arbitrary Upperbody mask. The Bullseye tables need their own source filter owner; biped arrays must not be applied merely because a port happens to be in range. Viewer animation output is unchanged in this research step.
