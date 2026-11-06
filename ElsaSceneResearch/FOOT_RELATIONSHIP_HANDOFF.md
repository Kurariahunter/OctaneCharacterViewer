> Follow-up: original numeric evaluation now runs in a controlled fixture. See FOOT_RELATIONSHIP_EVALUATION.md and foot-relationship-native-validation.json. The metadata-only status below is historical; full original animation target composition is still incomplete.

# Foot RelationshipProcessor: bounded trace handoff

Updated2026-10-15. Original executable hash remains f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705. No production importer, Unity preview or game asset changed in this pass.

## Verified address chain

Registration push0x5020CD (operand0x5020CE) -> factory0x5568B0 -> construction wrapper0x54EF70 -> allocator wrapper0x53F250 -> constructor0x53CC90. RTTI type descriptor0x200317C, name0x2003184 RelationshipProcessor@Samurai, vtable0x1B349AC. Execution slot16 is0x54C9A0. Allocator requests0x68 bytes plus appended arrays; initialization helper0x54C930.

## Runtime flow observed in disassembly

0x54C9A0 reads processor+0x58 and+0x64 and calls relationship record accessor0x503E00. If returned count iszero, it calls0x53E920 and returns. Otherwise it selects persistent-or-stack scratch arrays, calls0x544E00, then0x53D2B0 and finally0x53E920. The precise meaning of completion/cache helper0x53E920 is not established.

Processor fields observed, not a complete ABI:

| Offset | Observed use |
|---|---|
|+0x58|RelationshipData object passed as accessor this pointer|
|+0x64|Group/index passed to0x503E00|
|+0x28 /+0x2C|Pointer/count pair selecting input-side persistent scratch or stack fallback|
|+0x44 /+0x48|Pointer/count pair selecting output-side persistent scratch or stack fallback|
|+0x50|Referenced object whose+0x44 is read by0x544E00; exact role unresolved|
|+0x60 /+0x62|uint16 fields used for relative output operand lookup in0x53D2B0|

## Native-tested relationship table metadata

Elsa left/right RelationshipData nodes39 and66 contain identical580-byte blobs, SHA25673032eb1a654670678aae981cee41c85d79bdfd586156ceb61b851aca270cce1. Their RelationshipProcessor nodes are24/34. LastSegmentData nodes44/45 and71/72 are CacheArrayU16 with Count4. Actual cache initialization/meaning is unresolved.

Minimal RelationshipData object stores the raw blob pointer at+0x3C. The raw header uint32 at+8 is228; native accessors use it as the offset between the two table sections. uint16 at+0xC is1 group. Group offsets are section-relative uint32 entries starting+0x14.

Section0 base0: group header offset40, two counts4/4.
Section1 base228: group header offset268, two counts4/4.

Native0x503C90 was executed for both sections and agrees with the bounded parser's maxima4/4. Native0x503E00 for group0 returned count4 and a pointer corresponding to raw blob offset284. Those bytes are a record-list start, not four decoded target transforms.

For0x503E00(this, outCount, outPointer, group): select second section using blob+uint32(blob+8); select group via relative offset at section+0x14+group*4; read n=uint16(group+2); count=uint16(group+n*2+6); record-list pointer=group+n*2+8. Tested only on this valid authored blob. These observations are not general arbitrary-file validation or full relationship semantics.

Reproduce: python ElsaSceneResearch/probe_foot_relationship.py. It imports the existing pinned-EXE emulation setup, performs bounds checks on parsed fields, compares the native accessor outputs and saves foot-relationship-structure.json. This does not execute the full RelationshipProcessor.

## Exact next step

1. Decode the input record iterator in0x544E00 and the relative record access helpers0x503D60/0x503D80. Determine how input control values select/evaluate relationship records.
2. Trace output type dispatch and transform composition in0x53D2B0. Map the four output records at raw offset284 to source Output[0..3] without assuming a direct transform array.
3. Trace0x53E920 and LastSegmentData cache handling; construct initialized processor input/output arrays using factory name-based mappings rather than raw attribute order.
4. Only then execute a neutral foot-control fixture and compare all four output transforms against independent references. Follow with controlled ball/toe/foot inputs, then original clip controls and native IK.

No full foot-target decode, interpolation model or Unity character fix is claimed. The existing native IK controlled-target demo remains the latest verified solver test.

## Saved evidence

- foot-relationship-structure.json and probe_foot_relationship.py
- relationship-factory-disassembly.txt
- relationship-construction-disassembly.txt
- relationship-initialization-disassembly.txt
- relationship-runtime-disassembly.txt
- relationship-input-evaluation-disassembly.txt
- relationship-output-writes-disassembly.txt
- relationship-data-access-disassembly.txt

Disassembly extracts may extend beyond a function's return into neighboring code. Use the traced entry and control flow; do not assume every instruction in an excerpt belongs to one function.
