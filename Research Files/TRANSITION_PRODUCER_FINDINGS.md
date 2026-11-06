# Fade producer and activation — 2026-10-21

## Live identity

The read-only bridge still answered for PID104600/module00360000. Before inspecting the captured addresses, the module MZ header and PID were checked. Current reads confirmed controller0A54B980+30 still points to Float node0AE52DC0, whose producer is0AE45740. MSVC RTTI identifies that producer as `Samurai::TransitionProcessor`. The same producer is stored at controller+64. These pointers belong only to this process session; do not reuse them after a restart.

Evidence: `ElsaSceneResearch/ControllerState/live-fade-producer-identity.json` contains the controller, factor node, producer header and RTTI response. The observed configuration has start0, end1, duration0.10000000894069672, curve parameter1, parameter bits2, mode1, scale1, and completed flag1. This was a completed-state snapshot, not a live activation trace.

## Native routines

The vtable execute slot+40 resolves to preferred VA53C800. It reads the clock input, calculates `(clock - previousClock) * scale`, accumulates local time, evaluates the curve at1824010, writes the Float output, and then processes completion. Fields: +48 previous input clock, +4C local time, +50 time scale, +54 completion flag. Curve data begins at+1C.

Native activation52D9B0 initializes the curve through1822EB0, reads the cached clock, sets previous/local time, sets the curve time origin using the supplied offsets/delay, and clears completion. Wrapper53C780 first takes the current output as the new curve's starting value before calling52D9B0; it supports retargeting from the current value.

Disassembly confirms controller method76CD90 obtains its processor from controller+64 and calls52D9B0 with endpoints0/1, fixed parameter bits2/mode1, and arguments forwarded from its caller/global configuration. Controller method76CD00 uses+60 and calls53C780, with state checks at controller+3C. Do not conflate the +60 and +64 transitions. The live +64 match ties the fade node to the former direct activation path76CD90.

Raw direct-call scan candidates were confirmed by decoding these instruction windows. Indirect callers are not enumerated. Actor-level callers still decide activation duration, curve parameter, and scheduling; those decisions are not reconstructed here.

## Executable replay

`ElsaSceneResearch/native_transition_processor.py` executes original52D9B0 activation and53C800 update in the hash-pinned PC EXE. Clock/output nodes are explicit cached fixtures. Event ownership and completion callbacks are empty offline fixtures, while the native completion flag is allowed to execute. No event/callback effect on actor scheduling is claimed.

`test_native_transition_processor.py` passes18 numeric/update cases for rising/falling ramps, delayed activation, zero duration, local-clock accumulation and completion flags. The observed mode1 configuration produces a linear ramp. Combining its native factor with the native stateful scalar blender gives outputs2,4,6,8,10 for a target10 from prior output2 over a synthetic0.1-second fade. This validates the numerical composition using supplied activation arguments; it does not prove the game selects those arguments for every clip.

Report: `ElsaSceneResearch/ControllerState/transition-processor-native-validation.json`. Disassembly: `transition-processor-disassembly.txt` in that directory. The viewer's existing full-weight idle preview remains unchanged by this research step.

## Next boundary

Trace the instruction-confirmed callers of76CD90 and the actor's activation/setup path. Determine where duration/curve parameter come from and when scalar processor first-evaluation state is reset or retained. Reuse the still-linked read-only bridge for identity/setup observations; request an execution capture only if call timing/arguments cannot be recovered otherwise. No generic movement capture is required yet.
