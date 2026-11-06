# Direct native relationship pose capture

New probe: OctaneLiveInspector/CheatEngine/DI3_RelationshipPoseLogger.lua. It observes original RelationshipProcessor execution at entry 0x54C9A0 and normal full-path epilogue 0x54CA19. At the latter, ESI is still the processor and ESP is original entry ESP minus 0x330 (0x328 locals, saved ESI and EDI). Pair key combines processor pointer and reconstructed entry stack. No thread identity is inferred.

This bypasses the unresolved controller-context-to-final-graph lookup by observing the actual evaluator directly. It captures candidate six-input/four-output hand and one-input/one-output thumb relationships. Count and 16-byte prefix gates limit reads to candidate blocks of 836 or 196 bytes matching the known file layout. Full captured blob SHA256 must match an extracted relationship before accepting identity; prefix/count alone are not sufficient.

For each accepted entry/exit, snapshot includes processor header, full relationship blob, input Float-sized cached payloads and output Dilation-sized payloads (with vtable pointers and metadata stamps). Entry outputs supply initial values for possible native replay; exit inputs reflect dependencies read by that evaluation. Width assumptions must be confirmed from captured node types before interpretation. Recording does not force evaluation or write game data.

The normal exit site covers the nonempty selected-relationship path; the early return at 0x54C9D4 is not captured. Reject orphaned/ambiguous pairs and pairs with mismatched blob or counts. A last entry can be incomplete at the 64-event cap. Capture timeout ten seconds. Signature/ASLR/PE32 checks, no-existing-breakpoints guard, F8/F9 and cleanup are retained. Other research loggers unload on script execution.

Three Lua5.3 mock scenarios pass: paired entry/exit (same pair key, six inputs/four outputs and 836-byte blob), wrong signature, and partial breakpoint installation cleanup. These are tool tests, not live evaluator parity. Report: relationship-pose-logger-mock-validation.json.

## Capture

Attach CE to DisneyInfinity3.exe and execute DI3_RelationshipPoseLogger.lua. With Elsa already loaded in the same scene, press F8 while idle for an initial baseline, or while already moving for that state. The cap can fill quickly; changing state after starting may be too late. F9 stops early. Send ce_relationshippose_*.jsonl from OctaneLiveInspector/Captures.

Next analysis: exact blob-hash join, paired node/input/output validation, then replay original native relationship code with entry initial outputs and exit input values. Compare raw transforms and distinguish mismatched inputs from evaluator/output differences before any hand correction. This probe does not itself establish actor identity or final skinning parity.
