# Clock transition and publication order — 2026-10-19

Same hash-pinned PC EXE and preferred addresses as ENGINE_CLOCK_WRITER_HANDOFF.md. No viewer behavior changed.

## Native transition tests

`validate_pc_clock_transition.py` executes original 0x67B02F through the clock update return for 32 cases. Raw deltas: 0, 16, 100, 1000 ms. Scale pairs/duration: 1 to .5 over parameter .25, .5 to 1 over .25, 1 to 1 over .25, and 1 to .5 with parameter zero. Retained effective deltas: 0 and 17 ms. All exact float32 checks pass.

For these finite nonnegative fixtures, with rounding after the indicated SSE operations:

```
dt = float32(raw_ms * float32(.001))
denominator = float32(dt + owner.float38)
numerator = float32(float32(current * owner.float38) + float32(target * dt))
current = float32(numerator / denominator)
```

The native exponent guard selects target directly if its denominator/numerator exponent test fails, including the tested zero denominator. Extreme/nonfinite guard cases are not modeled or tested here. Transition byte +0x51 clears when abs(float32(current-target)) <= float32(1e-7). This behaves as weighted smoothing for the tested positive parameters, not a linear countdown to a deadline.

Crucially, this branch does not write owner+0x10 (effective integer delta). The accumulation tail uses its existing value. Both retained-delta fixtures verify that behavior. Earlier 0x67AFF0 code calls 0x67AC00 before entering the tested window; its child callbacks may alter relevant state. Therefore this does NOT prove the entire game transition freezes the previous tick or ignores scale. Reconstruct those callbacks before implementing a complete transition policy.

## Verified local call order

Function 0x6A0740 has a verified entry and calls:

1. 0x69F9A0 (publishes clock nodes).
2. 0x6A06E0.
3. Tail jump 0x69F9D0.

0x69F9A0 calls no-op 0x1437630, invokes host bridge 0x496B00 on object 0x21AEED8, calls 0x77C460, then tail-jumps to 0x6490B0. This verifies publication precedes those later calls within this path. Their full animation responsibilities are not yet established; do not claim all controllers update in this order.

Separate wrapper 0x133EE60 updates the engine clock singleton through 0x67AFF0 before an optional virtual call and 0x40B770. Its placement relative to 0x6A0740 remains open. Function-boundary disassembly is saved in clock_publication_order.txt.

## Next work

Inspect 0x67AC00 -> 0x679000 child clock callbacks, then the callers of the two verified wrappers. Determine who writes effective delta during smoothing and how clock advancement is scheduled relative to node publication. A live capture is only needed if static control flow and fixtures cannot establish active configuration. Viewer integration remains pending this dependency; no manual pose adjustments were added.
