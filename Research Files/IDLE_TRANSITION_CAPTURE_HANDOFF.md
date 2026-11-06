# Idle transition capture

The completed 092605 idle capture matched file-sampled finger scalars and local joint outputs exactly in 161 of 162 rows. All 162 relationship evaluations matched when replayed with the actual captured scalar inputs. The remaining row is right-hand specific02 at observed clock 0.0400390625, immediately after passive idle. Its cause is unresolved; no timing offset or fade formula has been applied as a correction.

## Run

Attach Cheat Engine to the current DisneyInfinity3.exe. With Elsa loaded and unpaused, execute `F:\DisneyInfinityPortalTest\OctaneLiveInspector\CheatEngine\DI3_IdleTransitionLogger.lua` in the Lua engine. Keep its adjacent `DI3_IdlePhase_sources.lua` configuration in place.

Press F8 to begin and leave Elsa idle. The logger stops after the targeted early specific02 transition plus three seconds, 240 records, or 180 seconds. F9 stops early. A completion beep follows successful saving and breakpoint cleanup. Send the new `ce_idletransition_*.jsonl` from `OctaneLiveInspector\Captures`.

The logger releases the no-minimize helper's F8/F9 hotkeys while retaining that helper's current patch state. It installs no breakpoints until F8 and refuses existing debugger breakpoints. The bridge cannot install these execution hooks, so this capture still requires the CE logger.

## Evidence collected

Current v2 uses four guarded hardware execution breakpoints at preferred executable addresses 543F9B (actual sampler time), 4E3050 (Float-blend entry), 4E35C0 (normal scalar return), and 54CA19 (relationship output). Entry records the prior scalar output, processor flags, and prior cumulative fade at processor+34. Captures link controller, source bytes, port mapping, output aliases, stamps and callback order. They also record source scalars, final scalars, two factor nodes, filter coefficient, priority and flag separately. An entry clears any older completed trace for its output. Early-return evaluations have no normal-return trace and are rejected rather than using stale data.

These are read-only debugger observations. Latest ordered callback links do not establish thread/call-stack identity. The analyzer rejects inconsistent links. For v2 single unflagged contributors with unit filter/factor2c, it replays original executable instructions with captured prior state and reports final-output parity separately from file-source parity. This probe does not change the viewer or fix poses.

## Validation

`test_idle_transition_logger_mock.py` passes with genuine PC clip evaluation and mocked CE callbacks: exact signatures, no breakpoint when arming, actual sampling time distinct from the later clock, ordered links, exact source samples, rejection of wrong ports, four-breakpoint cleanup and completion beep. This is not live transition validation.

Analyze a live capture with `ElsaSceneResearch/analyze_idle_transition_capture.py CAPTURE --output REPORT.json`. Interpret rejected rows as unresolved boundaries rather than parity evidence.
