# Targeted clock-order capture

Static searches still do not establish the indirect RUN dispatcher's global ordering. The adjacent global at 0x2012E94 is incremented in 0x6A7150's object setup; proximity does not identify the callback table owner. No new scheduler parity claim is made.

Prepared `OctaneLiveInspector/CheatEngine/DI3_ClockOrderLogger.lua` to capture original entry points using three hardware execute breakpoints:

- 0x67AFF0: clock update; records whether ECX is the shared singleton.
- 0x6A0740: lifecycle RUN entry, before publication.
- 0x533D10: curve-control update entry.

Each event records debugger sequence, elapsed time, ECX, ESP, the entry return address, and 88 raw bytes of the shared clock owner. Curve entries include 128 bytes of controller state. Return addresses at ESP are valid entry slots, not a general call-stack unwind. Clock updates are entry observations: their captured owner prefix precedes that update's mutations. RUN likewise precedes publication.

The logger verifies PE32 x86 and all three local instruction signatures, rebases preferred addresses, refuses existing breakpoints, and unloads older known research loggers. No injected code or game-data writes. F8 starts; F9 stops; automatic stop after 10 seconds or 120 events, with each site removed after 40 observations so one busy function does not consume the whole capture. Site caps can make later streams incomplete. Thread IDs are explicitly not captured; sequence is debugger observation order, not proof of cross-thread causality. Debugger pauses perturb timing.

## Run

1. Attach Cheat Engine to DisneyInfinity3.exe and open its Lua Engine.
2. Load/execute DI3_ClockOrderLogger.lua. Wait until the character and scene are ready.
3. Press F8, idle briefly then move; wait for automatic stop or press F9.
4. Supply the new `ce_clockorder_*.jsonl` from OctaneLiveInspector/Captures.

`test_clock_order_logger_mock.py` executes actual Lua 5.3 with mocked CE APIs and passes four scenarios: normal three-entry capture, signature rejection, second-breakpoint install failure cleanup, and per-site limit. These are tooling tests, not live game evidence. Report: clock-order-logger-mock-validation.json. Mock captures stay in CheatEngine/MockClockOrderCaptures and must not be interpreted as gameplay.

Next analysis should decode clock fields against the verified layout, distinguish shared/other clock objects, retain signature/ASLR provenance and compare per-controller cached state. Use entry return addresses to identify active callers. If multi-thread ambiguity matters, extend with a verified CE debugger-thread API rather than guessing thread identity.
