# Alternate publication path — 2026-10-19

Same preferred PC executable addresses/hash as preceding handoffs. No viewer behavior changed.

## Static path found

Searching relative JMP as well as CALL references establishes an alternate route:

```
0x13955E0 -> call 0x6A06D0 at 0x13955EA (return 0x13955EF)
0x6A06D0 -> tail-jump 0x69F9A0
0x69F9A0 -> call 0x496B00 at 0x69F9AA
0x496B00 -> publish shared clock values into typed nodes
```

Second verified caller 0x6A17E0 calls the trampoline at 0x6A17E3 (return 0x6A17E8), then calls 0x6A1790 and tail-jumps to 0x69F9D0. The registered RUN callback 0x6A0740 is a separate route to 0x69F9A0. Thus zero RUN hits do not imply zero clock publication. This corrects the earlier focus on the lifecycle wrapper; the shared publishing function can be reached without it.

Function 0x13955E0 first calls 0x1381C30, then the trampoline, and afterward passes global delta seconds to later calls. Its complete relationship to active wrapper 0x43E930 is not established by these static edges. Disassembly is saved in alternate_publication_path.txt. We have not yet observed which trampoline caller executes during the supplied captures.

## Targeted follow-up probe

New file `OctaneLiveInspector/CheatEngine/DI3_PublicationOrderLogger.lua` preserves the prior probe and substitutes the verified 0x6A06D0 trampoline for the unobserved RUN site. Its other two sites remain clock update 0x67AFF0 and curve update 0x533D10. Event name is publish_dispatch and output prefix ce_publicationorder_. Trampoline entry captures its caller return address before publication occurs.

F8 begins after gameplay is ready; F9 stops early; ten-second timeout and 40 events/site. Read-only hardware execution breakpoints, no code injection or game-data writes. ASLR/PE32/local signatures, existing-breakpoint refusal and cleanup retained. No thread ID; observation order remains bounded evidence rather than cross-thread causality.

Four Lua5.3 mock scenarios pass (normal three-site capture, bad signature, partial install cleanup, per-site cap). These are tooling tests, not live publication evidence. See publication-order-logger-mock-validation.json.

Run this new probe in CE Lua Engine, press F8 after loading gameplay, idle briefly and move. Supply ce_publicationorder_*.jsonl. Analyze token progression and entry return addresses; if publication is seen, compare its clock state with curve observations. Do not infer publication completion from an entry snapshot alone.
