# Activation-to-fade capture

Prepared `F:\DisneyInfinityPortalTest\OctaneLiveInspector\CheatEngine\DI3_ActivationFadeLogger.lua` to close the activation-time configuration boundary. This is a targeted execution probe because the read-only bridge cannot record function calls or install debugger breakpoints.

## Run

Attach CE to DisneyInfinity3.exe. Execute the script, return to the loaded Elsa scene and press F8. Leave Elsa idle and unpaused until the completion beep. No scene reload is needed. F9 stops early. Limits:180 seconds or160 records. Output: `OctaneLiveInspector\Captures\ce_activationfade_*.jsonl`.

The probe unloads older known research loggers and releases conflicting F8/F9 no-minimize hotkeys while retaining that helper's current patch state. It refuses unrelated existing debugger breakpoints. It installs four read-only hardware execution breakpoints after F8; it makes no game-data/code writes. Completion beeps only after saving and breakpoint cleanup, including F9 and automatic completion/limits.

## Sites and evidence

-7701C4: before76CD90 activation; captures computed duration/parameter arguments, selected configuration row, global clock-offset input, source identity and prior transition state.
-7701C9: after activation; captures the same processor's initialized curve/time/completion fields.
-53C800: transition update entry; captures prior numeric state and cached node identities.
-53C8D4: normal update return; captures updated time/curve output and completion flag.

ASLR-adjusted signatures guard all four sites. Known PC Elsa idle ClipData payloads and controller+64 / factor-output producer aliases filter observations. Full source bytes accompany records for offline hashing. Stack progression links activation before/after and update entry/return. These ordered records do not prove thread/call-stack identity or unique actor identity when duplicate Elsa actors exist. Prefer the existing Elsa-only scene.

After a linked activation, the probe stops once at least two matched updates have been recorded and the processor reports completion. Completion callbacks that take the tail-call branch can bypass the normal-return breakpoint; that evaluation must not be fabricated as captured. A subsequent normal-return update can still show the completed state. Unknown source types or unsupported layouts are ignored rather than relabeled.

## Offline checks after the live run

Check configuration integer *float32(1/30) against the actual duration argument, and the independent parameter against its argument. Replay52D9B0 with the actual arguments/global offset/clock to compare activation fields. Then replay53C800 from each observed entry with its matched clock input to compare local time and final factor. Report missing entries, incomplete returns, source changes and stale stamps as boundaries. External event/callback effects remain outside the numeric replay.

Mock validation covers no breakpoints before F8, four signatures, source/controller/producer alias filtering,8-byte activation stack cleanup,16-byte update stack linkage, configuration recording, valid JSONL, cleanup/beep and partial setup failure cleanup without beep. Live activation parity is not yet established.
