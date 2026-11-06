# Clock-to-curve time adapter

`native_cyclic_time.py` connects published `DefaultEngineClock` inputs to demand-driven curve-time state. It implements the previously validated native boundary configuration byte 0x0E only. It is not a general replacement for every AnimCurveControlProcessor mode.

```python
from native_default_clock import DefaultEngineClock
from native_cyclic_time import CyclicCurveTime
clock = DefaultEngineClock()
curve = CyclicCurveTime(0., 1.5)
clock.advance(16)
phase = curve.request(clock.publish())
```

Rates are multiplied with native float32 rounding; elapsed shared-clock seconds are computed from the consumer's cached prior clock. Negative resulting delta is clamped to zero. The prior clock updates only when requested. Reverse direction is supported. Repeated requests for the same publication reuse the cached phase; a skipped consumer catches up from its own cached clock when demanded later.

Loop handling matches the tested native branch: it preserves exact endpoints and only reduces overshoot with remainder when overshoot exceeds one full range. Blind modulo differs at exact full-range overshoots. Inputs require finite values, positive float32 ranges and an initially in-range phase. Other boundary flags, callbacks and frozen-state rules are not silently approximated.

`ElsaSceneResearch/validate_cyclic_time_adapter.py` passes 99 exact float32 comparisons with original EXE arithmetic 0x533D84..0x53409D:

- 40 direction/rate/delta cases matching earlier native fixtures.
- 16 exact-endpoint and multi-loop cases.
- 43 evaluations in a clock/publication sequence with one frequently requested and one intermittently requested consumer, plus repeated-request cache assertions.

Native helpers for remainder execute unchanged in these fixtures. Node lookup, state flag/token bookkeeping, frozen branch and output emission are outside the window. The adapter invalidation serial remains an implementation detail, not native metadata.

The renderer's existing bake is unchanged. To enable this as an opt-in timing path, first establish each supported profile's actual boundary configuration, initialize its phase/cache explicitly, and align dynamics dt/output timestamps with the supplied integer-ms schedule. Keep the current 60 Hz fixture bake as a regression reference. Do not apply 0x0E universally merely because it passed these bounded tests.
