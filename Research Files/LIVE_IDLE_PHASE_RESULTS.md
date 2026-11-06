# Same-callback idle pose results — 2026-10-21

Capture ce_idlephase_20261021_092605_208423859.jsonl, PID104600/base00360000, SHA25622fc8cf4750e8f061583ae835d66c387beaea6d663b5d527615e1b19cbaf0802. Final size7334712bytes,162pose rows, normal time_limit stop and breakpoints_released=true. Initial analysis read the file just before the stop row was appended; final analysis uses the complete closed capture/hash above.

All162pose rows pass full source payload hashing, clock alias/range, source ports and same node stamps. No rows excluded as boundaries. This is same-stamp local finger evidence on a matched Elsa relationship/controller/source path, not full world palette/GPU or global-thread atomic proof.

## File time -> six scalar inputs -> four local joints
- Passive idle:78rows, both hands, all exact.
- Specific01:16rows, both hands, all exact.
- Specific02:42rows, both hands,41exact and one exception.
- Specific03:26rows, both hands, all exact.

Total161/162exact (not merely within tolerance): all six sampled scalar inputs AND all32local joint components have zero error for those161. This covers four local outputs (index and middle chains), not thumbs, dress or whole skeleton.

Exception sequence55, Right, specific02 phase0.0400390625, stamp51517. Max file-sampled scalar difference0.1549720764, propagated local joint component difference0.0022568107. It immediately follows passive samples and is the first captured specific02 sample. Later specific02 samples are exact. This timing is consistent with a transition boundary but does NOT establish fade/clock-order cause. Nearest nearby raw clip phase ~0.01137 still differs; exploratory passive-to-new blend fit with weight~.46997 and phase~.0247 also is not exact. Do not install either as a correction.

## Isolate the native relationship
Replaying ALL162 with the actual six captured input values yields exactly zero difference in every local joint component, including sequence55. Thus the exception arises before the relationship output calculation, between the observed current source/clock and final scalar inputs. Same stamps alone do not prove the inputs were sampled from that exact current clock in all transition cases.

Reports: ControllerState/live-idle-phase-analysis-092605.json (capture provenance and all rows), idle-phase-exception-092605.json (earlier isolated diagnostic). Analyzer enhanced to separate file-time comparison from actual-input native relationship replay. No animation samples or baseline pose offsets changed.

Next bounded question: at an activation transition, what phase was actually consumed by ClipProcessor, and what contributor/fade coefficients produced those six input values? One targeted transition capture could record source evaluation time and final scalar weights in the SAME linkage, instead of collecting another broad idle run. This is not necessary to claim the161exact samples; it is necessary before explaining the sole exception or making a generic transition fix. Running-index issue remains independently unresolved; do not infer it is fixed by idle success.
