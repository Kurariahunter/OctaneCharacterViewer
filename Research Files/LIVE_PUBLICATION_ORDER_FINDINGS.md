# Live alternate publication order — 2026-10-19

Capture: ce_publicationorder_20261019_104217_40197328.jsonl. SHA256, complete decoded checks and per-event links: publication-order-capture-analysis.json. Reproduce with analyze_publication_order_capture.py from the research root.

## Observed path

The capture contains 40 shared-clock updates, 40 publication-dispatch entries and 40 curve updates. It stops normally at the configured 120-event limit. Each site independently reaches its 40-event cap; later absence of curve events is censored, not evidence that animation stopped.

All 40 shared clock entries return to 0x43E954, the verified call inside 0x43E930. All 40 trampoline entries return to 0x13955EF, identifying verified caller 0x13955E0. All 40 curve entries return to 0x48D2CE in the lazy payload getter.

The observed path is:

```
shared clock advancement: 0x43E930 -> 0x67AFF0
publication route:        0x13955E0 -> 0x6A06D0 -> 0x69F9A0 -> 0x496B00
curve evaluation:         0x48D2B0 -> producer virtual +0x40 -> 0x533D10
```

Edges within each row are verified static calls/jumps; the ordering between rows is capture observation order. No thread IDs were captured, so this does not prove cross-thread causality or the full intervening scheduler call chain.

## Checks passing

- 39 consecutive clock-entry pairs increment token by one and accumulate the next effective delta correctly.
- Every publication entry sees a token one greater than its preceding clock-entry snapshot; its total milliseconds reflect that effective delta.
- All 40 publication states are normal mode, transition disabled, and effective delta equals min(raw delta, cap).
- All 40 curve-entry owner snapshots exactly match the preceding publication-entry decoded clock state. Seven distinct curve-state pointers occur.
- Every decoded owner seconds/delta value matches the established native float conversions.

This closes the missing RUN observation for this capture: the game used the alternate trampoline, not the registered RUN callback. It does not imply RUN is unused in every game mode.

## Limits and implementation consequence

Publication breakpoints are at trampoline entry, before setters execute. The static trampoline/bridge path is known, but this capture does not separately prove publication completion or contain typed-node payload snapshots. Prior writer captures independently identify those setters and watched nodes. Keep those separate evidence sources explicit.

Native default clock arithmetic and its observed placement before on-demand curve evaluation are now supported. A viewer adapter can advance integer engine milliseconds, publish time/token into its node model, and evaluate requested stale controllers while preserving their caches. It must not update every controller unconditionally, assume one tick per rendered frame, or invent smooth-scale delta arithmetic. This capture does not solve other clip decoding, pose composition, secondary dynamics, or missing body-channel behavior.

Next practical implementation: add a separately validated default clock adapter and demand-driven time-state test to the viewer/research pipeline, retaining the current preview as a regression reference. No further capture is required for that step. No viewer behavior was changed while analyzing this file.
