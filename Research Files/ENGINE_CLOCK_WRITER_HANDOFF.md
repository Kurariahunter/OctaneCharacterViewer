# Engine clock writer: 2026-10-19

## Evidence and result

Capture `ce_clockwriter_20261019_101605_38624390.jsonl` contains 16 float writes and 15 unsigned-integer writes. All 31 pass the address, setter stack-slot, argument-pointer and payload-address checks in `analyze_clock_writer_capture.py`. It stopped at its configured event limit, not a timeout/error. Breakpoints perturb timing; these events do not establish game FPS.

Addresses below are preferred VAs for the PC EXE SHA256 `f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705`. Live module base was 0x140000; preferred base is 0x400000.

| Item | Preferred VA | Meaning |
|---|---|---|
| Float setter | 0x4913B0 | Writes node+0x34 at 0x4913BC; post-write EIP 0x4913BF |
| Uint setter | 0x491560 | Writes node+0x34 at 0x491569; post-write EIP 0x49156C |
| Host bridge | 0x496B00 | Calls setters; captured returns 0x496B24 and 0x496B86 |
| Clock owner | 0x22018F0 | Engine clock state, not an animation-specific producer |
| Clock update | 0x67AFF0 | Reads raw timer, chooses effective delta, accumulates time |
| Raw timer | 0x40D590 | Timer-difference conversion includes multiplier 1000; has override path |

Setter stack offset +4 is a verified return slot because both setters push ESI before the watched write. This is not a heuristic scan of arbitrary stack words. Watched nodes were 0x05F53840 (float) and 0x05F53CC0 (uint), matching prior clock-producer captures. Payload addresses are node+0x34.

## Host bridge and clock layout

`0x496B00` publishes these owner fields into nodes belonging to its bridge object:

| Owner field | Bridge node | Interpretation |
|---|---|---|
| +0x24 / 0x2201914 | +0x18 | Accumulated engine time in seconds; watched float |
| +0x0C / 0x22018FC | +0x1C | Raw timer value converted by float 0.001 |
| +0x1C / 0x220190C | +0x20 | Effective engine delta in seconds |
| +0x00 / 0x22018F0 | +0x24 | Clock-update token; watched uint |

`0x67AFF0` stores raw elapsed integer ticks at +4, applies a cap through +0x34 before mode-dependent selection, and selects effective integer delta at +0x10. Its branches include zero/one-shot, shifting, and multiplication paths, plus a scale-transition branch. Their full policy and active live settings are not yet reconstructed. Do not substitute wall-clock delta for effective engine delta unconditionally.

The accumulation tail at 0x67B169 does:

1. Preserve previous accumulated milliseconds (+0x18 to +0x14).
2. Add effective delta (+0x10) to accumulated uint32 milliseconds (+0x18), wrapping modulo 2^32.
3. Write delta seconds (+0x1C) using the float constant 0.0010000000474974513.
4. Preserve prior float clock (+0x24 to +0x20).
5. Convert the new unsigned accumulated milliseconds to seconds using double 0.001, then store float32 at +0x24.
6. Increment the uint32 update token at +0x00.

The token advances per execution of this clock update, including a zero-delta update. It is not proven to equal rendered frames. Static caller 0x1378D10 configures this singleton, updates it, then decrements the token, so lifecycle/reset paths also matter.

## Native validation and viewer implications

`validate_pc_engine_clock_tail.py` executes the original accumulation tail in Unicorn for 16 cases: four accumulated values including unsigned/sign-boundary and wraparound cases, with deltas 0, 1, 16, and 100 ms. All pass exact float32 seconds/delta checks, previous-clock preservation, accumulated uint32 arithmetic, and token increment. The test seeds the x87 constant and stack; it does not run the OS timer, mode selection, scheduler or full game.

This completes the traced input chain for observed nodes:

engine clock -> host bridge -> shared typed nodes -> AnimCurveControlProcessor local time -> output time payload -> ClipProcessor sampler.

Earlier time-integration and getter fixtures independently verify the downstream pieces. This is not a newly executed end-to-end full-engine test. Cached controller input values can lag the shared nodes, as prior captures showed; do not refresh every controller indiscriminately or reset stale caches to force agreement.

Next: reconstruct clock mode/default selection and its scheduling relative to controller evaluation, then implement an explicit engine-clock adapter in the viewer. Keep current partial preview behavior separate until validated. No pose corrections or viewer changes were made in this step.

Artifacts: `clock-writer-capture-analysis.json`, `engine-clock-tail-validation.json`, `host_clock_bridge.txt`, `engine_clock_update.txt`, `clock_raw_timer.txt`. Re-run both scripts from F:/DisneyInfinityPortalTest with the supplied capture path for the analyzer.
