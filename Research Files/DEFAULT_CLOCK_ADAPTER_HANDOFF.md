# Default engine clock adapter

`native_default_clock.py` provides the verified normal-mode input clock independently of preview rendering. No dependency on Unity, the game process, or Unicorn is required by this adapter.

```python
from native_default_clock import DefaultEngineClock, DemandClockConsumer
clock = DefaultEngineClock()  # normal mode, 100 ms cap
consumer = DemandClockConsumer(lambda inputs: (inputs.seconds, inputs.token))
clock.advance(16)             # integer milliseconds supplied by host
inputs = clock.publish()      # explicit publication after advancement
value = consumer.request(inputs)
```

Advance clamps the supplied uint32 delta to the selected cap, accumulates uint32 milliseconds with wraparound, produces native float32 seconds/delta conversions, and increments the uint32 token even for zero delta. Constructor seeds the native 17 ms effective delta. Cap 60 ms is also validated. Advancing does not automatically publish.

Publish creates immutable clock inputs and a new adapter invalidation generation. Consumers independently evaluate only when requested with a new publication object, then retain their result for repeated requests. A skipped consumer keeps its old cache. This is a minimal input-cache adapter, not the full native node graph. The unbounded adapter generation is not the native 16-bit metadata stamp and must not be exported as one. The evaluator owns native curve time and boundary behavior; the example lambda is not an animation decoder.

Validation: `ElsaSceneResearch/validate_default_clock_adapter.py` passes 40 comparisons against original normal-mode selection/accumulation code and 117 transitions across three live captures. Tests include 60/100 ms caps, zero and oversized deltas, uint32 time/token wraparound, separate publication, repeated requests, and independently stale consumers. Native test input EDI is pre-capped; OS timer and child traversal are outside the fixture.

The existing `evaluate_native_clip.py` bake remains on its established fixture timing. This module is deliberately not substituted into rendering before the native controller phase, loop endpoints, and dynamics tick conventions are connected and regression-tested. No new visual result is claimed yet.

Next: bind published inputs to the existing validated AnimCurveControlProcessor time state, test demand-driven phase updates against original code, then add an explicit opt-in preview timing mode with the current bake retained as a regression reference. Pause, shift/custom modes, smoothing, thread scheduling and full game node invalidation remain outside this default adapter.
