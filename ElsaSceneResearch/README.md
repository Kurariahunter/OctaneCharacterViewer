# Elsa historical scene sample check — 2026-10-14

Inspected the user-supplied fro_elsa.zip with the existing checked tuple decoder, without running the pasted historical Python code. See container-check.json for file hashes, consumed bytes, record counts, payload sizes and any unsupported formats.

The supplied March 2014 forum text identifies the same OCT SubNetworkPool/DataNodePool/ClipDataBlock path used by our research. Its uncertainty about influence remaps, Basis hierarchy and animation payloads is historical speculation, not a new decoder specification. The later PS3 Blender importer post reports weighted models and approximate parenting, not animation support.

This archive is useful as another character/older sample corpus, with original binary OCTs and accompanying text dumps. Platform/version provenance is not independently established. Container compatibility does not prove timed-curve or graph-evaluation compatibility, and no Elsa Unity animation has been generated.

Next: compare Elsa idle payload headers and command descriptors with the supported Yoda timed layout, then test exact channel mapping and native operator semantics. Preserve unsupported cases rather than guessing.

## Timed-curve follow-up
The unchanged Yoda decoder rejects all 30 motion payloads at command/static-header checks. Curve reading completes for the idle samples before command-boundary rejection. A separate experimental interleaved descriptor-count/port reader accepts three motions with exact dynamic boundaries and <=3 quantization-unit continuity; remaining samples are rejected. This is candidate layout evidence, not a universally established older format. Idle playback remains unresolved, including unknown command widths/semantics. See timed-curve-comparison.json for names, offsets and diagnostic values. Malformed short/truncated/invalid-pool samples were rejected for accepted cases. No production importer changes.

## Executable-backed rotation refinement
The supplied executable matches the previous native-rotation report SHA256. Read-only disassembly confirms eight-byte 0x1xxx rotation commands and axis source flags; see executable-findings.json and interpreter-disassembly.txt. Applying those widths/flags in the isolated research reader raises accepted structural/continuity cases from 3 to 12 of 30. All six Elsa idle samples still stop at a provisional interleaved-layout count check (17, port 140); layout semantics remain unresolved. No game process was launched, and no Unity importer was modified.
