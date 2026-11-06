# Live clock order: two captures, 2026-10-19

Inputs: ce_clockorder_20261019_103730_39910078.jsonl and ce_clockorder_20261019_103752_39931718.jsonl. Capture hashes and decoded observations are in clock-order-capture-analysis.json. Analyzer: analyze_clock_order_captures.py. Static disassembly: active_clock_and_lazy_getter.txt.

## Results

Each capture contains 40 clock entries and 40 curve entries, zero RUN entries, and stops normally at the ten-second limit. Clock and curve sites reached their separate 40-hit caps early; later absence of those events is therefore not meaningful. RUN did not hit during either bounded capture. This does not prove the lifecycle callback is never used.

All clock entries target the shared singleton. Every clock return address rebases to 0x43E954, identifying the verified call at 0x43E94F inside function 0x43E930. This is the observed active caller, rather than the previously investigated polling wrapper 0x133EE60.

Across 78 consecutive clock-entry pairs, all checks pass:

- Token increments by exactly one.
- Next accumulated milliseconds equal previous accumulated milliseconds plus next effective delta, modulo uint32.
- Effective delta equals min(raw delta, cap) in the captured normal mode.
- Every decoded clock's float seconds and delta seconds match the established native conversions.

Both captures have mode 3, cap 100 ms, smoothing parameter zero and transition flag clear. Debugger overhead contributes to raw timing, including capped 100 ms deltas. Do not derive normal game frame rate from these measurements.

## On-demand curve evaluation

All 80 curve entries return to preferred 0x48D2CE. Verified native getter 0x48D2B0 compares node+0x20 with metadata+0x20; if unequal and node+0x18 producer is non-null, it invokes producer virtual +0x40. The captured curve entry is that invocation. It then returns payload pointer node+0x34.

Every captured curve sees a shared token exactly one beyond the most recent observed clock-entry token. Nine distinct curve-state pointers recur in each capture. The entry snapshot contains the controller's pre-update cache: no cached token already matches the shared token. Some lag by more than one update (up to 112 in the first capture, 934 in the second), so controllers need not evaluate every global update. Actor identity is not established from these pointers.

This supports a clock-advance followed by on-demand curve-evaluation path in debugger observation order. Thread IDs are absent; do not promote that ordering to global cross-thread causality. We have not captured host publication between these entries, so the exact clock-node publication route is still unresolved.

## Active wrapper static structure

0x43E930 calls shared clock update 0x67AFF0, then 0x43E700, 0x43E860, and 0x43E8E0 before later virtual calls. 0x43E700 forwards object 0x22034B8 to 0x70D560. That function has container/queued-work traversal; its complete responsibility and connection to clock publication are not yet established. No semantic engine subsystem name is assigned to it here.

## Next

Follow the actual 0x43E930 path, its queued-work calls and clock-publishing bridge instead of assuming RUN drives these observed updates. The native reader must preserve lazy metadata invalidation and per-controller cached time; advancing all controllers unconditionally would erase behavior present in these captures. A default clock arithmetic adapter is now backed by both isolated native tests and these live normal-mode transitions, but global scheduling parity remains unproven. No new capture is needed yet. No viewer behavior changed in this analysis.
