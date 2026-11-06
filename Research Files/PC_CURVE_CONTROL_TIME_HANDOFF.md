# AnimCurveControlProcessor local-time update

2026-10-19

Captured state vtable 0x1B35334 has virtual slot +0x40 pointing to 0x533D10. This function is the concrete AnimCurveControlProcessor update routine, not the clone/setup function at 0x54EB30.

When frozen-output flag byte +0x63 bit0 is clear, the processor reads input zero through 0x48D2B0. At 0x533D84 it reads that input clock and computes in float32:

```
delta = max(0, (+0x48 * +0x44) * (inputClock - previousInputClock))
+0x50 = inputClock
```

The routine then advances local time +0x54 forward or backward according to flag word +0x60 bit0 and applies range/boundary behavior using +0x3C/+0x40 and byte +0x62. The names/rules for all flag combinations are not yet established. The two rate fields are multiplicative factors; their upstream meanings are not identified merely by this multiplication. Negative rate or clock delta combinations are clamped after multiplication, not each independently.

Executed original instruction window 0x533D84..0x53409D in 40 finite controlled cases: two directions, four rate pairs, five clock changes (including zero, negative and large changes), with cyclic flag byte +0x62=14. Original remainder helpers execute on multi-span wrapping; no call-result stubs. All local-time expectations match exactly. The test supplies the input-clock pointer and skips node lookup, frozen-output branch and output emission. Stop/reset callbacks and every flag combination are not covered.

Replayed three captures for controller 0x08A0C100 using each preceding captured state plus the next captured +0x50 as input clock. All 133 consecutive comparisons match captured +0x54 exactly. Only three involve actual clock changes (one in each capture); the remaining 130 are repeated observations. Therefore do not describe this as 133 independent time advances or evidence for a complete cycle.

The full update statically emits +0x54, lower/upper ranges and status into output zero at offsets +0x34/+0x38/+0x3C/+0x40/+0x44. This output-emission tail has not been executed by the window test. +0x50 is now identified as the last input-clock value and +0x54 as local time in the processor's own clock units. Seconds, normalized phase and the identity of the clock producer are not independently established here.

Files: curve-control-time-validation.json, curve_control_update.txt; reproduce with ../validate_pc_curve_control_time.py. No viewer motion changed.

Next follow input zero's clock producer and output zero's downstream clip-time consumption. Then a filtered one-controller capture spanning a full cycle can validate actual range/end behavior without exhausting the event limit on repeated output blends. No broad long capture is requested now.
