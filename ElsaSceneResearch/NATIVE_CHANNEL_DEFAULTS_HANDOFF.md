# Native channel-default checkpoint

2026-10-16. Follow-up to ELSA_LAYER_SCHEDULE_HANDOFF.md and the original-game reference recording.

## Confirmed result

All90 Elsa connection-map default values exactly match the stored DataNode fallback values used by the bounded evaluator. Therefore replacing those default values cannot correct the observed pose in these fixtures. Active bulge remains unresolved; no mesh, weights, clips or production importer changed.

## Native table lookup

Scene loader0x50125f..0x5012ce fetches two hashed properties and passes buffers/counts to0x4b41d0. Allocation constructor0x4b40c0, vtable0x1b2c034. Object+0xc holds ushort indices,+0x10 index count,+0x14 float pool,+0x18 float count. The loader copies index bytes then divides count by2, copies pool bytes then divides count by4. Property hash names have not been independently decoded; source table sizes and reader behavior corroborate this interpretation.

Original getter0x4b23d0 masks an index word with0x1fff, resolves pool_base+4*offset and copies64bytes. Scalar lookup block0x4e33d0..0x4e33f0 uses the same mask/address before weighting. The high3bits are ignored by these readers; their role elsewhere remains unverified. Offset0x1fff is a missing-value sentinel; sentinel semantics are disassembled but not included in the fixture tests.

validate_channel_defaults_native.py executes the unmodified routines/basic block in Unicorn.100 randomized cases use varying float offsets and all high-bit patterns (randomly sampled), with exact float32 readback for transform/scalar outputs. Source fixture tests all90 slots, with maximum default-versus-stored value error0. Elsa transform/dilation defaults share an identity record; reading the16-float common record does not establish a universal Dilation accessor. Runtime masks, blends and untouched-component rules are separate from the validated value lookup.

## BENT channel declaration loading

Static trace0x787480..0x787670 uses20-byte channel records: name+0, another property+4 (not interpreted here), priority float+8, weight float+0xc, index+0x10. Missing priority defaults0, missing Weight defaults1, missing ChannelIndex defaults-1. Weight literal at0x1b35cb4 and fallback float at0x1b24124 checked against file bytes.

Consequently FullBody has declared priority5,index0,implicit weight1; FullBodyBlends priority4,index4,explicit weight0; FeetInterface priority2,index9,implicit weight1. This is NOT evidence that FeetInterface is playing during the recorded idle. Priority direction, runtime enabling and layer input values remain unverified. Do not activate a layer merely because its default weight is1.

## Reproduction / next executable boundary

Run validate_channel_defaults_native.py and save_channel_loader_evidence.py. Reports: native-channel-default-validation.json and channel-declaration-loader-findings.json. Corresponding disassembly snapshots are included. Originals remain read-only; EXE SHA pinned in native report.

Next: follow runtime channel activation and the typed control blend path. The Float blend neighborhood0x4e339f..0x4e3412 demonstrates that remaining blend weight can contribute a default scalar, but complete priority grouping, transform blend behavior and game-selected inputs still need controlled native fixtures. A valid fix requires divergence from the original runtime or a matched game pose, not speculative adjustment of defaults now proven equal.
